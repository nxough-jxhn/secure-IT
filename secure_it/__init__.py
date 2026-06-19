import os
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, redirect, render_template, request, session, url_for

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency during setup
    load_dotenv = None


SECRET_KEY = "secure-it-development-key"
BASE_DIR = Path(__file__).resolve().parent.parent

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


def make_layout(active_page: str, title: str, subtitle: str, content_template: str, **context):
    base_context = {
        "active_page": active_page,
        "title": title,
        "subtitle": subtitle,
        "year": datetime.now().year,
        "is_logged_in": session.get("logged_in", False),
        "user_role": session.get("user_role", "guest"),
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
        if session.get("user_role") != "admin":
            return redirect(url_for("dashboard_page"))
        return view(*args, **kwargs)

    return wrapped_view


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.secret_key = SECRET_KEY
    app.config["REQUIRE_EMAIL_VERIFICATION"] = os.getenv("REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true"
    try:
        app.config["EMAIL_VERIFY_TTL_HOURS"] = int(os.getenv("EMAIL_VERIFY_TTL_HOURS", "24"))
    except ValueError:
        app.config["EMAIL_VERIFY_TTL_HOURS"] = 24

    from .routes.admin import admin_page
    from .routes.auth import login_page, logout_page, register_page, social_login_page, verify_email_page
    from .routes.dashboard import dashboard_page
    from .routes.landing import landing_page
    from .routes.quizzes import quizzes_page
    from .routes.simulations import simulations_page

    app.add_url_rule("/", endpoint="landing_page", view_func=landing_page)
    app.add_url_rule("/login", methods=["GET", "POST"], endpoint="login_page", view_func=login_page)
    app.add_url_rule("/register", methods=["POST"], endpoint="register_page", view_func=register_page)
    app.add_url_rule("/social/<provider>", methods=["GET"], endpoint="social_login_page", view_func=social_login_page)
    app.add_url_rule("/verify-email/<token>", methods=["GET"], endpoint="verify_email_page", view_func=verify_email_page)
    app.add_url_rule("/dashboard", endpoint="dashboard_page", view_func=dashboard_page)
    app.add_url_rule("/simulations", endpoint="simulations_page", view_func=simulations_page)
    app.add_url_rule("/quizzes", endpoint="quizzes_page", view_func=quizzes_page)
    app.add_url_rule("/admin", endpoint="admin_page", view_func=admin_page)
    app.add_url_rule("/logout", endpoint="logout_page", view_func=logout_page)

    return app
