from flask import session

from database import get_app_shell_context, get_user_dashboard_data, MODULE_BADGES, list_forum_posts
from secure_it import login_required, make_layout
from simulation_missions import list_mission_summaries


@login_required
def dashboard_page():
    email = session.get("user_email", "")
    data = get_user_dashboard_data(email)
    shell = get_app_shell_context(email)
    missions = list_mission_summaries()
    completed_set = set(data["simulations_completed"])

    # Modules in progress or completed for "Module Progress" row
    history_ids = {h.get("attack_id") for h in (data.get("history") or [])}
    active_modules = [
        m for m in missions
        if m["id"] in completed_set or m["id"] in history_ids
    ][:6]

    # Recommended = not yet completed
    recommended = [m for m in missions if m["id"] not in completed_set][:3]
    if not recommended:
        recommended = missions[:3]

    # Build badge list: all 10 module badges + milestone badges, mark earned/locked
    earned_badge_names = set(data.get("badges", []))
    all_badges = [
        {"id": v["badge_id"], "name": v["badge_name"],
         "module": k, "earned": v["badge_name"] in earned_badge_names}
        for k, v in MODULE_BADGES.items()
    ]
    milestone_badges = [
        {"id": "first_step", "name": "First Step", "condition": "Complete your first module", "earned": len(completed_set) >= 1},
        {"id": "full_shield", "name": "Full Shield", "condition": "Complete all 10 modules", "earned": len(completed_set) >= 10},
        {"id": "perfect_strike", "name": "Perfect Strike", "condition": "Get 100% on any quiz", "earned": any(
            h.get("quiz_score") is not None and int(h.get("quiz_score")) == 100
            for h in (data.get("history") or []))},
        {"id": "persistent", "name": "Persistent", "condition": "Use both retakes and finish", "earned": False},
        {"id": "unstoppable", "name": "Unstoppable", "condition": "Complete all 10 Hard Sims on first try", "earned": False},
        {"id": "flawless", "name": "Flawless", "condition": "Get 100% on all 10 quizzes", "earned": False},
    ]

    # Namecard definitions
    all_namecards = [
        {"id": "social_sentinel", "name": "Social Sentinel", "theme": "Social-Based", "earned": False},
        {"id": "malware_hunter", "name": "Malware Hunter", "theme": "Malware-Based", "earned": False},
        {"id": "network_warden", "name": "Network Warden", "theme": "Network-Based", "earned": False},
        {"id": "code_guardian", "name": "Code Guardian", "theme": "Injection-Based", "earned": False},
        {"id": "cyber_throne", "name": "Cyber Throne", "theme": "1st on Leaderboard", "earned": data.get("rank") == 1},
        {"id": "iron_vanguard", "name": "Iron Vanguard", "theme": "2nd on Leaderboard", "earned": data.get("rank") == 2},
        {"id": "bronze_bastion", "name": "Bronze Bastion", "theme": "3rd on Leaderboard", "earned": data.get("rank") == 3},
        {"id": "secureit_elite", "name": "Secure-IT Elite", "theme": "All modules + max pts", "earned": False},
    ]

    # Certificate definitions
    all_certificates = [
        {"id": "performance", "name": "Performance Certificate", "condition": "Available to all users", "earned": True},
        {"id": "completion", "name": "Completion Certificate", "condition": "Complete all 10 modules", "earned": len(completed_set) >= 10},
        {"id": "perfect_score", "name": "Perfect Score Certificate", "condition": "Achieve 1,500 pts", "earned": int(data.get("points", 0)) >= 1500},
        {"id": "leaderboard", "name": "Leaderboard Certificate", "condition": "Rank in Top 10", "earned": data.get("rank") is not None and data["rank"] <= 10},
    ]

    recent_posts = list_forum_posts(limit=6, viewer_email=email)

    return make_layout(
        "dashboard",
        "Learning Dashboard",
        "Your personal cybersecurity training hub.",
        "dashboard.html",
        **shell,
        metrics=data["metrics"],
        history=data["history"],
        recommended=recommended,
        average_score=data["average_score"],
        category_progress=data["category_progress"],
        next_mission=data["next_mission"],
        leaderboard=data["leaderboard"],
        active_modules=active_modules,
        all_badges=all_badges,
        milestone_badges=milestone_badges,
        all_namecards=all_namecards,
        all_certificates=all_certificates,
        user_points=data["points"],
        user_rank=data.get("rank"),
        recent_posts=recent_posts,
    )
