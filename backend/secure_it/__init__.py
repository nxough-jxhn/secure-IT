import os
import secrets
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency during setup
    load_dotenv = None


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = REPO_ROOT / "frontend"

if load_dotenv is not None:
    load_dotenv(REPO_ROOT / ".env")


def normalize_role(role) -> str:
    return str(role or "student").strip().lower()


def is_admin_role(role) -> bool:
    return normalize_role(role) == "admin"


def _resolve_secret_key() -> str:
    secret_key = (
        os.getenv("SECRET_KEY", "").strip()
        or os.getenv("FLASK_SECRET_KEY", "").strip()
        or os.getenv("SECURE_IT_SECRET_KEY", "").strip()
    )
    if secret_key:
        return secret_key

    node_env = os.getenv("NODE_ENV", "").strip().lower()
    if node_env == "development":
        return secrets.token_hex(32)

    raise RuntimeError("A secret key must be configured in production.")


def make_layout(active_page: str, title: str, subtitle: str, content_template: str, **context):
    user_role = normalize_role(session.get("user_role", "guest"))
    base_context = {
        "active_page": active_page,
        "title": title,
        "subtitle": subtitle,
        "year": datetime.now().year,
        "is_logged_in": session.get("logged_in", False),
        "user_role": user_role,
        "is_admin": is_admin_role(user_role),
        "display_name": session.get("display_name", "Guest"),
        "year_level": session.get("year_level", ""),
        "profile_picture": session.get("profile_picture", ""),
        "email_verified": session.get("email_verified", False),
    }
    base_context.update(context)
    return render_template(content_template, **base_context)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        if not is_admin_role(session.get("user_role")):
            return redirect(url_for("dashboard_page"))
        return view(*args, **kwargs)

    return wrapped_view


def create_app():
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "templates"),
        static_folder=str(FRONTEND_DIR / "static"),
    )
    app.secret_key = _resolve_secret_key()
    app.config["REQUIRE_EMAIL_VERIFICATION"] = os.getenv("REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true"
    try:
        app.config["EMAIL_VERIFY_TTL_HOURS"] = int(os.getenv("EMAIL_VERIFY_TTL_HOURS", "24"))
    except ValueError:
        app.config["EMAIL_VERIFY_TTL_HOURS"] = 24

    from .routes.admin import admin_page, admin_users_page, toggle_user_page, admin_simulations_page, admin_quiz_manager_page, admin_quiz_questions_api, admin_quiz_create_api, admin_quiz_update_api, admin_quiz_delete_api, admin_quiz_toggle_api, admin_community_page, admin_comments_page, admin_community_posts_api, admin_toggle_post_api, admin_toggle_comment_api
    from .routes.auth import (
        firebase_login,
        login_page,
        logout_page,
        register_page,
        verify_email_page,
    )
    from .routes.dashboard import dashboard_page
    from .routes.landing import landing_page
    from .routes.leaderboard import leaderboard_page
    from .routes.collection import collection_page, set_namecard_page
    from .routes.modules import modules_category_page, modules_page
    from .routes.community import forum_page, forum_like_api, forum_comment_api, forum_delete_api, forum_edit_comment_api, forum_delete_comment_api
    from .routes.profile import profile_page
    from .routes.quizzes import quizzes_page
    from .routes.simulations import (
        adware_pop_up_page,
        evil_twin_page,
        phishing_fake_email_page,
        phishing_fake_website_page,
        simulation_complete_page,
        simulation_easy_complete_page,
        simulation_easy_page,
        simulation_overview_page,
        simulation_play_page,
        simulation_quiz_page,
        simulation_quiz_submit_page,
        simulation_results_page,
        simulation_start_page,
        simulations_page,
    )

    app.add_url_rule("/", endpoint="landing_page", view_func=landing_page)
    app.add_url_rule("/login", methods=["GET", "POST"], endpoint="login_page", view_func=login_page)
    app.add_url_rule("/register", methods=["POST"], endpoint="register_page", view_func=register_page)
    app.add_url_rule("/auth/firebase", methods=["POST"], endpoint="firebase_login", view_func=firebase_login)
    app.add_url_rule("/verify-email/<token>", methods=["GET"], endpoint="verify_email_page", view_func=verify_email_page)
    app.add_url_rule("/dashboard", endpoint="dashboard_page", view_func=dashboard_page)
    app.add_url_rule("/leaderboard", endpoint="leaderboard_page", view_func=leaderboard_page)
    app.add_url_rule("/collection", endpoint="collection_page", view_func=collection_page)
    app.add_url_rule("/collection/set-namecard", methods=["POST"], endpoint="set_namecard_page", view_func=set_namecard_page)
    app.add_url_rule("/profile", methods=["GET", "POST"], endpoint="profile_page", view_func=profile_page)
    app.add_url_rule("/modules", endpoint="modules_page", view_func=modules_page)
    app.add_url_rule("/modules/category/<category_id>", endpoint="modules_category_page", view_func=modules_category_page)
    app.add_url_rule("/simulations", endpoint="simulations_page", view_func=simulations_page)
    app.add_url_rule("/phishing_fake_email", endpoint="phishing_fake_email_page", view_func=phishing_fake_email_page)
    app.add_url_rule("/phishing_fake_website", endpoint="phishing_fake_website_page", view_func=phishing_fake_website_page)
    app.add_url_rule("/adware_pop_up", endpoint="adware_pop_up_page", view_func=adware_pop_up_page)
    app.add_url_rule("/evil_twin", endpoint="evil_twin_page", view_func=evil_twin_page)
    app.add_url_rule("/simulations/<attack_id>", endpoint="simulation_overview_page", view_func=simulation_overview_page)
    app.add_url_rule("/simulations/<attack_id>/easy", endpoint="simulation_easy_page", view_func=simulation_easy_page)
    app.add_url_rule(
        "/simulations/<attack_id>/easy/complete",
        methods=["POST"],
        endpoint="simulation_easy_complete_page",
        view_func=simulation_easy_complete_page,
    )
    app.add_url_rule("/simulations/<attack_id>/start", endpoint="simulation_start_page", view_func=simulation_start_page)
    app.add_url_rule("/simulations/<attack_id>/play", endpoint="simulation_play_page", view_func=simulation_play_page)
    app.add_url_rule("/simulations/<attack_id>/complete", methods=["POST"], endpoint="simulation_complete_page", view_func=simulation_complete_page)
    app.add_url_rule("/simulations/<attack_id>/results", endpoint="simulation_results_page", view_func=simulation_results_page)
    app.add_url_rule("/simulations/<attack_id>/quiz", endpoint="simulation_quiz_page", view_func=simulation_quiz_page)
    app.add_url_rule("/simulations/<attack_id>/quiz/submit", methods=["POST"], endpoint="simulation_quiz_submit_page", view_func=simulation_quiz_submit_page)
    app.add_url_rule("/quizzes", endpoint="quizzes_page", view_func=quizzes_page)
    app.add_url_rule("/community", methods=["GET", "POST"], endpoint="forum_page", view_func=forum_page)
    app.add_url_rule("/community/like/<post_id>", methods=["POST"], endpoint="forum_like_api", view_func=forum_like_api)
    app.add_url_rule("/community/comment/<post_id>", methods=["POST"], endpoint="forum_comment_api", view_func=forum_comment_api)
    app.add_url_rule("/community/post/<post_id>", methods=["DELETE"], endpoint="forum_delete_api", view_func=forum_delete_api)
    app.add_url_rule("/community/comment/<post_id>/<int:comment_index>", methods=["PATCH"], endpoint="forum_edit_comment_api", view_func=forum_edit_comment_api)
    app.add_url_rule("/community/comment/<post_id>/<int:comment_index>", methods=["DELETE"], endpoint="forum_delete_comment_api", view_func=forum_delete_comment_api)
    app.add_url_rule("/admin", endpoint="admin_page", view_func=admin_page)
    app.add_url_rule("/admin/users", endpoint="admin_users_page", view_func=admin_users_page)
    app.add_url_rule("/admin/toggle-user", methods=["POST"], endpoint="toggle_user_page", view_func=toggle_user_page)
    app.add_url_rule("/admin/simulations", endpoint="admin_simulations_page", view_func=admin_simulations_page)
    app.add_url_rule("/admin/quiz",                    endpoint="admin_quiz_manager_page",   view_func=admin_quiz_manager_page)
    app.add_url_rule("/admin/quiz/questions/<attack_id>", endpoint="admin_quiz_questions_api", view_func=admin_quiz_questions_api)
    app.add_url_rule("/admin/quiz/create",             methods=["POST"],   endpoint="admin_quiz_create_api",   view_func=admin_quiz_create_api)
    app.add_url_rule("/admin/quiz/<question_id>",      methods=["PATCH"],  endpoint="admin_quiz_update_api",   view_func=admin_quiz_update_api)
    app.add_url_rule("/admin/quiz/<question_id>",      methods=["DELETE"], endpoint="admin_quiz_delete_api",   view_func=admin_quiz_delete_api)
    app.add_url_rule("/admin/quiz/<question_id>/toggle", methods=["POST"], endpoint="admin_quiz_toggle_api",   view_func=admin_quiz_toggle_api)
    app.add_url_rule("/admin/community",               endpoint="admin_community_page",          view_func=admin_community_page)
    app.add_url_rule("/admin/community/comments",      endpoint="admin_comments_page",           view_func=admin_comments_page)
    app.add_url_rule("/admin/community/posts",         endpoint="admin_community_posts_api",     view_func=admin_community_posts_api)
    app.add_url_rule("/admin/community/post/<post_id>/toggle", methods=["POST"], endpoint="admin_toggle_post_api", view_func=admin_toggle_post_api)
    app.add_url_rule("/admin/community/post/<post_id>/comment/<int:comment_index>/toggle", methods=["POST"], endpoint="admin_toggle_comment_api", view_func=admin_toggle_comment_api)
    app.add_url_rule("/logout", methods=["POST"], endpoint="logout_page", view_func=logout_page)

    from firebase_auth import get_firebase_web_config

    @app.context_processor
    def inject_firebase_config():
        return {"firebase_config": get_firebase_web_config()}

    return app
