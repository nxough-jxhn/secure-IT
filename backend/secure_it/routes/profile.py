from flask import redirect, request, session, url_for

from cloudinary_uploader import upload_profile_picture
from database import (
    get_user_by_email,
    get_app_shell_context,
    get_leaderboard,
    get_user_rank,
    update_user_by_email,
    MODULE_BADGES,
    list_forum_posts,
)
from secure_it import login_required, make_layout


def _allowed_profile_picture(file_storage) -> bool:
    mimetype = getattr(file_storage, "mimetype", "") or ""
    if mimetype not in {"image/jpeg", "image/png", "image/webp"}:
        return False

    header = file_storage.stream.read(12)
    file_storage.stream.seek(0)
    if header.startswith(b"\xff\xd8\xff"):
        return True
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return True
    return False


def _sync_session(user: dict):
    session["display_name"] = user.get("name", session.get("display_name", ""))
    session["year_level"] = user.get("year_level", "")
    session["profile_picture"] = user.get("profile_picture", "")


@login_required
def profile_page():
    email = session.get("user_email")
    user = get_user_by_email(email) if email else None
    if not user:
        return redirect(url_for("logout_page"))

    message = None
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        year_level = request.form.get("year_level", "").strip()
        profile_picture = request.files.get("profile_picture")

        if not name:
            error = "Name is required."
        elif not year_level:
            error = "Select your year level."
        else:
            updates = {"name": name, "year_level": year_level}

            if profile_picture and profile_picture.filename:
                if not _allowed_profile_picture(profile_picture):
                    error = "Profile picture must be a JPG, PNG, or WEBP image."
                else:
                    uploaded_image = upload_profile_picture(profile_picture)
                    if uploaded_image is None:
                        error = "Could not upload profile picture right now."
                    else:
                        updates["profile_picture"] = uploaded_image

            if not error:
                updated_user = update_user_by_email(email, updates)
                if updated_user:
                    _sync_session(updated_user)
                    message = "Profile updated successfully."
                    user = updated_user
                else:
                    error = "Could not save profile changes."

    shell = get_app_shell_context(email)

    # Build badge list for display panel
    earned_badge_names = set(shell["profile"].get("badges", []))
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
        {"id": "first_step",  "name": "First Step",  "condition": "Complete your first module",  "earned": len(shell["profile"]["simulations_completed"]) >= 1},
        {"id": "full_shield", "name": "Full Shield",  "condition": "Complete all 10 modules",     "earned": len(shell["profile"]["simulations_completed"]) >= 10},
    ]

    all_namecards = [
        {"id": "social_sentinel", "name": "Social Sentinel", "theme": "Social-Based",      "earned": False},
        {"id": "malware_hunter",  "name": "Malware Hunter",  "theme": "Malware-Based",     "earned": False},
        {"id": "network_warden",  "name": "Network Warden",  "theme": "Network-Based",     "earned": False},
        {"id": "code_guardian",   "name": "Code Guardian",   "theme": "Injection-Based",   "earned": False},
        {"id": "cyber_throne",    "name": "Cyber Throne",    "theme": "1st on Leaderboard","earned": shell.get("rank") == 1},
    ]

    leaderboard = get_leaderboard(limit=8)
    recent_posts = list_forum_posts(limit=4, viewer_email=email)

    return make_layout(
        "profile",
        "Profile",
        "Your Secure-IT learner profile.",
        "profile.html",
        **shell,
        user=user,
        message=message,
        error=error,
        all_badges=all_badges,
        milestone_badges=milestone_badges,
        all_namecards=all_namecards,
        leaderboard=leaderboard,
        recent_posts=recent_posts,
    )
