"""Admin analytics aggregation for Secure-IT."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from database import get_database, get_user_by_email, list_all_users


def _results_collection():
    db = get_database()
    if db is None:
        return None
    return db["simulation_results"]


def _activities_collection():
    db = get_database()
    if db is None:
        return None
    return db["activity_logs"]


def get_admin_analytics() -> dict[str, Any]:
    users = list_all_users()
    results_col = _results_collection()

    total_users = len(users)
    active_window = datetime.now(timezone.utc) - timedelta(days=7)
    active_emails: set[str] = set()

    simulation_results: list[dict] = []
    if results_col is not None:
        simulation_results = list(results_col.find({}).sort("completed_at", -1).limit(2000))

    for row in simulation_results:
        completed_at = row.get("completed_at")
        if completed_at and getattr(completed_at, "tzinfo", None) is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        if completed_at and completed_at >= active_window:
            active_emails.add(str(row.get("email", "")))

    completed_sims = len(simulation_results)
    sim_scores = [int(r.get("simulation_score", 0)) for r in simulation_results if r.get("simulation_score") is not None]
    quiz_scores = [int(r.get("quiz_score", 0)) for r in simulation_results if r.get("quiz_score") is not None]

    avg_sim = round(sum(sim_scores) / len(sim_scores)) if sim_scores else 0
    avg_quiz = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0

    attack_counts = Counter(str(r.get("attack_id", "unknown")) for r in simulation_results)
    failed_scenarios = Counter()
    mistake_counter = Counter()

    for row in simulation_results:
        score = int(row.get("simulation_score", 0))
        attack_id = str(row.get("attack_id", "unknown"))
        if score < 70:
            failed_scenarios[attack_id] += 1
        for mistake in row.get("mistakes", []) or []:
            mistake_counter[str(mistake)] += 1

    user_ranking = _build_user_ranking(users, simulation_results)
    awareness_score = _awareness_score(sim_scores, quiz_scores, completed_sims, total_users)

    recent_activity = _build_recent_activity(simulation_results, users)
    performance_chart = _performance_by_attack(simulation_results)
    completion_chart = _completion_rates(simulation_results, attack_counts)

    # ── New fields for the admin dashboard ──────────────────────

    # Total points earned across all users
    total_points_earned = sum(int(u.get("points", 0)) for u in users)

    # Points gained per day for the last 10 days
    now = datetime.now(timezone.utc)
    points_by_day: list[dict[str, Any]] = []
    day_buckets: dict[str, int] = {}
    for i in range(9, -1, -1):
        day = now - timedelta(days=i)
        day_buckets[day.strftime("%Y-%m-%d")] = 0

    for row in simulation_results:
        pts = int(row.get("points_earned") or 0)
        if pts <= 0:
            continue
        completed_at = row.get("completed_at")
        if not completed_at:
            continue
        if getattr(completed_at, "tzinfo", None) is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        ds = completed_at.strftime("%Y-%m-%d")
        if ds in day_buckets:
            day_buckets[ds] += pts

    max_pts = max(day_buckets.values(), default=1) or 1
    for ds, pts in day_buckets.items():
        points_by_day.append({
            "date":  ds[5:],          # MM-DD
            "points": pts,
            "pct":   round(pts / max_pts * 100),
        })

    # Trend: compare last 5 days vs prior 5 days
    vals = [v for v in day_buckets.values()]
    recent_half  = sum(vals[5:])
    previous_half = sum(vals[:5])
    if previous_half > 0:
        points_trend_pct = round(((recent_half - previous_half) / previous_half) * 100)
    else:
        points_trend_pct = 100 if recent_half > 0 else 0

    # Progress by category — count users who started each category
    # (started = completed easy sim of at least one attack in that category)
    try:
        from simulation_data import ATTACKS
        from database import CATEGORY_ORDER
        cat_attack_map: dict[str, list[str]] = defaultdict(list)
        for attack_id, attack in ATTACKS.items():
            cat_attack_map[attack.get("category", "")].append(attack_id)

        cat_labels = {
            "social_based":    "Social",
            "malware_based":   "Malware",
            "network_based":   "Network",
            "injection_based": "Injection",
        }

        category_progress: list[dict[str, Any]] = []
        for cat_id, _ in CATEGORY_ORDER:
            attack_ids = set(cat_attack_map.get(cat_id, []))
            started = sum(
                1 for u in users
                if attack_ids & set(u.get("simulations_completed", []))
            )
            category_progress.append({
                "id":          cat_id,
                "short_label": cat_labels.get(cat_id, cat_id),
                "started":     started,
            })
    except Exception:
        category_progress = []

    return {
        "total_users":             total_users,
        "active_users":            len(active_emails),
        "completed_simulations":   completed_sims,
        "average_simulation_score": avg_sim,
        "average_quiz_score":      avg_quiz,
        "awareness_score":         awareness_score,
        "most_selected_attacks":   attack_counts.most_common(5),
        "most_failed_scenarios":   failed_scenarios.most_common(5),
        "common_mistakes":         mistake_counter.most_common(5),
        "user_ranking":            user_ranking[:10],
        "recent_activity":         recent_activity[:15],
        "performance_chart":       performance_chart,
        "completion_chart":        completion_chart,
        # New dashboard fields
        "total_points_earned":     total_points_earned,
        "points_by_day":           points_by_day,
        "points_trend_pct":        points_trend_pct,
        "category_progress":       category_progress,
        "recent_posts":            [],   # community feature not yet built
    }


def _awareness_score(sim_scores: list[int], quiz_scores: list[int], completed: int, total_users: int) -> int:
    if not sim_scores and not quiz_scores:
        return 0
    blended = []
    blended.extend(sim_scores)
    blended.extend(quiz_scores)
    base = round(sum(blended) / len(blended)) if blended else 0
    participation = min(100, round((completed / max(total_users, 1)) * 100))
    return round((base * 0.75) + (participation * 0.25))


def _build_user_ranking(users: list[dict], results: list[dict]) -> list[dict]:
    scores_by_email: dict[str, list[int]] = defaultdict(list)
    for row in results:
        email = str(row.get("email", ""))
        if row.get("simulation_score") is not None:
            scores_by_email[email].append(int(row.get("simulation_score", 0)))
        if row.get("quiz_score") is not None:
            scores_by_email[email].append(int(row.get("quiz_score", 0)))

    ranking = []
    for user in users:
        email = str(user.get("email", ""))
        user_scores = scores_by_email.get(email, [])
        avg = round(sum(user_scores) / len(user_scores)) if user_scores else 0
        ranking.append(
            {
                "name": user.get("name", email),
                "email": email,
                "points": int(user.get("points", 0)),
                "level": user.get("level", "Beginner"),
                "completed": len(user.get("simulations_completed", [])),
                "average_score": avg,
            }
        )

    ranking.sort(key=lambda item: (item["points"], item["average_score"]), reverse=True)
    return ranking


def _build_recent_activity(results: list[dict], users: list[dict]) -> list[dict]:
    user_map = {str(u.get("email", "")): u.get("name", "User") for u in users}
    activity = []
    for row in results:
        email = str(row.get("email", ""))
        mistakes = row.get("mistakes") or []
        activity.append(
            {
                "user": user_map.get(email, email),
                "email": email,
                "attack_id": row.get("attack_id", ""),
                "simulation_score": row.get("simulation_score", 0),
                "quiz_score": row.get("quiz_score"),
                "status": "Completed",
                "mistakes": mistakes[:2],
                "time_spent_seconds": row.get("time_spent_seconds", 0),
                "completed_at": row.get("completed_at"),
            }
        )
    return activity


def _performance_by_attack(results: list[dict]) -> list[dict]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for row in results:
        attack = str(row.get("attack_id", "unknown"))
        if row.get("simulation_score") is not None:
            buckets[attack].append(int(row.get("simulation_score", 0)))

    chart = []
    for attack_id, scores in buckets.items():
        chart.append({"attack_id": attack_id, "average": round(sum(scores) / len(scores))})
    chart.sort(key=lambda item: item["average"], reverse=True)
    return chart


def _completion_rates(results: list[dict], attack_counts: Counter) -> list[dict]:
    completed_users = Counter(str(r.get("email", "")) for r in results)
    return [
        {"attack_id": attack_id, "attempts": count, "unique_users": len({r.get("email") for r in results if r.get("attack_id") == attack_id})}
        for attack_id, count in attack_counts.most_common(8)
    ]


def get_user_monitoring_rows() -> list[dict]:
    users = list_all_users()
    results_col = _results_collection()
    results: list[dict] = []
    if results_col is not None:
        results = list(results_col.find({}).sort("completed_at", -1).limit(200))

    by_email: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        by_email[str(row.get("email", ""))].append(row)

    rows = []
    for user in users:
        email = str(user.get("email", ""))
        attempts = by_email.get(email, [])
        latest = attempts[0] if attempts else None
        rows.append(
            {
                "username": user.get("name", email),
                "email": email,
                "completed_simulations": len(user.get("simulations_completed", [])),
                "points": int(user.get("points", 0)),
                "level": user.get("level", "Beginner"),
                "current_progress": f"{len(user.get('simulations_completed', []))} missions",
                "latest_simulation": latest.get("attack_id") if latest else "—",
                "latest_score": latest.get("simulation_score") if latest else "—",
                "time_spent": sum(int(a.get("time_spent_seconds", 0)) for a in attempts),
                "mistakes": (latest.get("mistakes") or ["—"])[0] if latest and latest.get("mistakes") else "—",
                "active_namecard": user.get("active_namecard", ""),
                "profile_picture": user.get("profile_picture", ""),
                "disabled": bool(user.get("disabled", False)),
                "attempt_history": [
                    {
                        "attack_id": a.get("attack_id"),
                        "score": a.get("simulation_score"),
                        "quiz_score": a.get("quiz_score"),
                        "mistakes": a.get("mistakes", []),
                    }
                    for a in attempts[:5]
                ],
            }
        )

    rows.sort(key=lambda item: item["completed_simulations"], reverse=True)
    return rows


def get_simulation_management_rows() -> list[dict]:
    """Return per-attack stats for the admin simulations page."""
    from simulation_data import ATTACKS

    results_col = _results_collection()
    users = list_all_users()
    user_map = {str(u.get("email", "")): u for u in users}

    results: list[dict] = []
    if results_col is not None:
        results = list(results_col.find({}).sort("completed_at", -1).limit(2000))

    # Index results by attack_id
    by_attack: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        by_attack[str(row.get("attack_id", ""))].append(row)

    # Build per-user easy-sim completion set
    easy_completed_by_user: dict[str, set[str]] = defaultdict(set)
    for u in users:
        for att_id in u.get("simulations_completed", []):
            easy_completed_by_user[str(u.get("email", ""))].add(att_id)

    rows = []
    for attack_id, attack in ATTACKS.items():
        attack_results = by_attack.get(attack_id, [])

        sim_scores  = [int(r["simulation_score"]) for r in attack_results if r.get("simulation_score") is not None]
        quiz_scores = [int(r["quiz_score"])        for r in attack_results if r.get("quiz_score") is not None]
        avg_sim  = round(sum(sim_scores)  / len(sim_scores))  if sim_scores  else 0
        avg_quiz = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0

        unique_attempted = len({str(r.get("email", "")) for r in attack_results})
        fail_count       = sum(1 for s in sim_scores if s < 70)

        # Users who completed easy sim for this attack
        started_users = []
        for u in users:
            email = str(u.get("email", ""))
            if attack_id in easy_completed_by_user[email]:
                started_users.append({
                    "name":  u.get("name", email),
                    "email": email,
                    "profile_picture": u.get("profile_picture", ""),
                })

        # Top scorers on hard sim + quiz (by total points_earned for this attack)
        pts_by_email: dict[str, int] = defaultdict(int)
        for r in attack_results:
            pts_by_email[str(r.get("email", ""))] += int(r.get("points_earned") or 0)

        top_scorers = sorted(
            [
                {
                    "name":   user_map.get(e, {}).get("name", e),
                    "email":  e,
                    "pts":    p,
                    "sim_score":  max(
                        (int(r["simulation_score"]) for r in by_attack[attack_id]
                         if str(r.get("email")) == e and r.get("simulation_score") is not None),
                        default=None,
                    ),
                    "quiz_score": max(
                        (int(r["quiz_score"]) for r in by_attack[attack_id]
                         if str(r.get("email")) == e and r.get("quiz_score") is not None),
                        default=None,
                    ),
                }
                for e, p in pts_by_email.items()
            ],
            key=lambda x: x["pts"],
            reverse=True,
        )[:5]

        rows.append({
            "id":            attack_id,
            "name":          attack["name"],
            "icon":          attack.get("icon", "🎯"),
            "image":         attack.get("image", ""),
            "difficulty":    attack.get("difficulty", "Beginner"),
            "category":      attack.get("category", ""),
            "category_label":attack.get("category_label", ""),
            "short_description": attack.get("short_description", ""),
            "attempts":      len(attack_results),
            "unique_users":  unique_attempted,
            "avg_sim_score": avg_sim,
            "avg_quiz_score":avg_quiz,
            "fail_count":    fail_count,
            "started_users": started_users,
            "top_scorers":   top_scorers,
        })

    return rows


def get_activity_log_rows() -> list[dict]:
    """Return all hard-sim + quiz activity rows for the table view."""
    from simulation_data import ATTACKS

    results_col = _results_collection()
    users = list_all_users()
    user_map = {str(u.get("email", "")): u.get("name", u.get("email", "")) for u in users}
    attack_map = {k: {"name": v["name"], "category": v.get("category", ""), "category_label": v.get("category_label", "")} for k, v in ATTACKS.items()}

    results: list[dict] = []
    if results_col is not None:
        # Only hard-sim (completion_stage == 'hard') and quiz entries
        results = list(results_col.find(
            {"completion_stage": {"$in": ["hard", "quiz"]}}
        ).sort("completed_at", -1).limit(2000))

    rows = []
    for r in results:
        attack_id  = str(r.get("attack_id", ""))
        email      = str(r.get("email", ""))
        stage      = str(r.get("completion_stage", ""))
        atk        = attack_map.get(attack_id, {"name": attack_id, "category": "", "category_label": ""})

        completed_at = r.get("completed_at")
        if completed_at:
            if hasattr(completed_at, "strftime"):
                date_str = completed_at.strftime("%Y-%m-%d")
                time_str = completed_at.strftime("%H:%M")
            else:
                date_str = str(completed_at)[:10]
                time_str = str(completed_at)[11:16]
        else:
            date_str = "—"
            time_str = "—"

        ts = int(r.get("time_spent_seconds") or 0)
        duration = f"{ts // 60}m {ts % 60}s" if ts else "—"

        sim_score  = r.get("simulation_score")
        quiz_score = r.get("quiz_score")
        pts        = int(r.get("points_earned") or 0)
        mistakes   = r.get("mistakes") or []
        good       = r.get("good_actions") or []

        rows.append({
            "user":           user_map.get(email, email),
            "email":          email,
            "attack_id":      attack_id,
            "attack_name":    atk["name"],
            "category":       atk["category"],
            "category_label": atk["category_label"],
            "stage":          stage,           # 'hard' | 'quiz'
            "sim_score":      sim_score,
            "quiz_score":     quiz_score,
            "points_earned":  pts,
            "mistakes":       mistakes,
            "good_actions":   good,
            "duration":       duration,
            "date":           date_str,
            "time":           time_str,
        })

    return rows
