from database import get_metrics, get_student_profile

from secure_it import make_layout


def landing_page():
    profile = get_student_profile()
    metrics = get_metrics()
    return make_layout(
        "landing",
        "Secure-IT",
        "Gamified cybersecurity awareness for students",
        "landing_page.html",
        profile=profile,
        metrics=metrics,
    )
