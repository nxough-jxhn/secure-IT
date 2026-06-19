from database import get_metrics

from secure_it import login_required, make_layout


@login_required
def dashboard_page():
    metrics = get_metrics()
    from database import get_student_profile

    profile = get_student_profile()
    return make_layout(
        "dashboard",
        "Student Dashboard",
        "Track progress, badges, and learning milestones.",
        "dashboard.html",
        profile=profile,
        metrics=metrics,
    )
