from flask import session

from database import (
    get_app_shell_context,
    get_leaderboard,
    get_user_rank,
    LEADERBOARD_RANK_TITLES,
    MODULE_BADGES,
)
from secure_it import login_required, make_layout


def _rank_title(rank: int | None) -> str:
    if rank is None:
        return LEADERBOARD_RANK_TITLES["default"]
    if rank == 1:
        return LEADERBOARD_RANK_TITLES[1]
    if rank == 2:
        return LEADERBOARD_RANK_TITLES[2]
    if rank == 3:
        return LEADERBOARD_RANK_TITLES[3]
    if rank <= 10:
        return LEADERBOARD_RANK_TITLES["top_10"]
    return LEADERBOARD_RANK_TITLES["default"]


@login_required
def leaderboard_page():
    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    leaderboard = get_leaderboard(limit=50)
    user_rank = shell.get("rank")

    # Attach rank titles and medal to each entry
    for entry in leaderboard:
        r = entry.get("rank", 0)
        entry["rank_title"] = _rank_title(r)
        entry["medal"] = "🥇" if r == 1 else "🥈" if r == 2 else "🥉" if r == 3 else ""
        entry["is_current_user"] = (
            entry.get("name", "").lower()
            == session.get("display_name", "").lower()
        )

    top3 = leaderboard[:3]
    rest = leaderboard[3:]

    # All module + milestone badges for badge shelf
    from database import get_user_progress
    progress = get_user_progress(email)
    earned_badge_names = set(progress.get("badges", []))

    all_badges = [
        {
            "id": v["badge_id"],
            "name": v["badge_name"],
            "module": k,
            "earned": v["badge_name"] in earned_badge_names,
        }
        for k, v in MODULE_BADGES.items()
    ]
    milestone_badges = [
        {"id": "first_step",    "name": "First Step",    "icon": "👣", "condition": "Complete your first module"},
        {"id": "full_shield",   "name": "Full Shield",   "icon": "🛡️", "condition": "Complete all 10 modules"},
        {"id": "perfect_strike","name": "Perfect Strike","icon": "🎯", "condition": "Get 100% on any quiz"},
        {"id": "flawless",      "name": "Flawless",      "icon": "✨", "condition": "100% on all 10 quizzes"},
        {"id": "persistent",    "name": "Persistent",    "icon": "💪", "condition": "Use both retakes and finish"},
        {"id": "unstoppable",   "name": "Unstoppable",   "icon": "⚡", "condition": "All 10 Hard Sims on first try"},
    ]
    for mb in milestone_badges:
        mb["earned"] = mb["name"] in earned_badge_names

    return make_layout(
        "leaderboard",
        "Leaderboard",
        "See how you stack up against other defenders.",
        "leaderboard.html",
        **shell,
        leaderboard=leaderboard,
        top3=top3,
        rest=rest,
        user_rank=user_rank,
        user_rank_title=_rank_title(user_rank),
        all_badges=all_badges,
        milestone_badges=milestone_badges,
    )
