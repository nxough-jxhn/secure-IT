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
        simulation_results = list(results_col.find({}).sort("completed_at", -1).limit(500))

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

    return {
        "total_users": total_users,
        "active_users": len(active_emails),
        "completed_simulations": completed_sims,
        "average_simulation_score": avg_sim,
        "average_quiz_score": avg_quiz,
        "awareness_score": awareness_score,
        "most_selected_attacks": attack_counts.most_common(5),
        "most_failed_scenarios": failed_scenarios.most_common(5),
        "common_mistakes": mistake_counter.most_common(5),
        "user_ranking": user_ranking[:10],
        "recent_activity": recent_activity[:15],
        "performance_chart": performance_chart,
        "completion_chart": completion_chart,
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
