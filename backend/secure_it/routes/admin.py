from analytics import get_admin_analytics, get_user_monitoring_rows
from secure_it import admin_required


def make_admin_layout(active_page: str, title: str, subtitle: str, content_template: str, **context):
    from datetime import datetime
    from flask import render_template

    base_context = {
        "active_page": active_page,
        "title": title,
        "subtitle": subtitle,
        "year": datetime.now().year,
    }
    base_context.update(context)
    return render_template(content_template, **base_context)


@admin_required
def admin_page():
    analytics = get_admin_analytics()
    return make_admin_layout(
        "admin",
        "Security Analytics Overview",
        "Real-time platform intelligence from simulations, quizzes, and learner activity.",
        "admin_dashboard.html",
        analytics=analytics,
    )


@admin_required
def admin_users_page():
    users = get_user_monitoring_rows()
    return make_admin_layout(
        "admin_users",
        "User Activity Monitor",
        "Track learner progress, scores, mistakes, and attempt history.",
        "admin_users.html",
        users=users,
    )
