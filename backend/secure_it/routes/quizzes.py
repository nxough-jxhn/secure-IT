from secure_it import login_required, make_layout


@login_required
def quizzes_page():
    return make_layout(
        "quizzes",
        "Knowledge Quizzes",
        "Check understanding at the end of each module.",
        "quizzes.html",
    )
