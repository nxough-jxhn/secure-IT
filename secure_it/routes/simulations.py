from database import get_recent_attempts

from secure_it import login_required, make_layout


@login_required
def simulations_page():
    return make_layout(
        "simulations",
        "Simulations",
        "Practice in safe scenarios before facing the real thing.",
        "simulations.html",
        recent_attempts=get_recent_attempts(),
    )
