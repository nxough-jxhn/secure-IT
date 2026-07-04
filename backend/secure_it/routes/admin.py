from analytics import get_admin_analytics, get_user_monitoring_rows, get_simulation_management_rows, get_activity_log_rows
from flask import jsonify, request as flask_request, session as flask_session
from database import (
    _users_collection, _normalize_email,
    get_quiz_questions_for_attack,
    get_all_quiz_questions_for_attack,
    create_quiz_question,
    update_quiz_question,
    delete_quiz_question,
    toggle_quiz_question_active,
    count_active_quiz_questions,
    list_all_forum_posts,
    get_forum_posts_by_user,
    admin_disable_forum_post,
    admin_disable_forum_comment,
    list_all_users,
)
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


@admin_required
def toggle_user_page():
    """POST /admin/toggle-user  { email, disabled: bool }"""
    payload  = flask_request.get_json(silent=True) or {}
    email    = str(payload.get("email", "")).strip().lower()
    disabled = bool(payload.get("disabled", False))

    if not email:
        return jsonify({"error": "Missing email"}), 400

    users_col = _users_collection()
    if users_col is None:
        return jsonify({"error": "Database unavailable"}), 503

    try:
        users_col.update_one(
            {"email": _normalize_email(email)},
            {"$set": {"disabled": disabled}},
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"success": True, "email": email, "disabled": disabled})


@admin_required
def admin_quiz_manager_page():
    from simulation_data import ATTACKS
    attacks_list = [
        {
            "id":         aid,
            "name":       a["name"],
            "icon":       a.get("icon", "🎯"),
            "category":   a.get("category_label", ""),
            "q_count":    count_active_quiz_questions(aid),
        }
        for aid, a in ATTACKS.items()
    ]
    return make_admin_layout(
        "admin_quiz",
        "Quiz Manager",
        "Create, edit, and manage randomized quiz questions per attack.",
        "admin_quiz_manager.html",
        attacks=attacks_list,
    )


@admin_required
def admin_quiz_questions_api(attack_id: str):
    """GET /admin/quiz/questions/<attack_id> — return all questions for an attack."""
    questions = get_all_quiz_questions_for_attack(attack_id)
    return jsonify(questions)


@admin_required
def admin_quiz_create_api():
    """POST /admin/quiz/create"""
    payload = flask_request.get_json(silent=True) or {}
    attack_id     = str(payload.get("attack_id", "")).strip()
    question      = str(payload.get("question", "")).strip()
    choices       = [str(c).strip() for c in payload.get("choices", [])]
    correct_index = int(payload.get("correct_index", 0))
    explanation   = str(payload.get("explanation", "")).strip()

    if not attack_id or not question or len(choices) < 2:
        return jsonify({"error": "attack_id, question, and at least 2 choices are required"}), 400
    if correct_index < 0 or correct_index >= len(choices):
        return jsonify({"error": "correct_index out of range"}), 400

    created_by = flask_session.get("user_email", "admin")
    doc = create_quiz_question(attack_id, question, choices, correct_index, explanation, created_by)
    if not doc:
        return jsonify({"error": "Database error"}), 500
    return jsonify({"success": True, "question": doc}), 201


@admin_required
def admin_quiz_update_api(question_id: str):
    """PATCH /admin/quiz/<question_id>"""
    payload = flask_request.get_json(silent=True) or {}
    allowed = {"question", "choices", "correct_index", "explanation", "active"}
    updates = {k: v for k, v in payload.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    ok = update_quiz_question(question_id, updates)
    return jsonify({"success": ok})


@admin_required
def admin_quiz_delete_api(question_id: str):
    """DELETE /admin/quiz/<question_id>"""
    ok = delete_quiz_question(question_id)
    return jsonify({"success": ok})


@admin_required
def admin_quiz_toggle_api(question_id: str):
    """POST /admin/quiz/<question_id>/toggle  { active: bool }"""
    payload = flask_request.get_json(silent=True) or {}
    active = bool(payload.get("active", True))
    ok = toggle_quiz_question_active(question_id, active)
    return jsonify({"success": ok})


@admin_required
def admin_simulations_page():
    attacks    = get_simulation_management_rows()
    activities = get_activity_log_rows()
    return make_admin_layout(
        "admin_simulations",
        "Simulations Monitor",
        "Per-attack statistics, user participation, and leaderboards.",
        "admin_simulations.html",
        attacks=attacks,
        activities=activities,
    )


@admin_required
def admin_community_page():
    """GET /admin/community — post management table."""
    posts = list_all_forum_posts(limit=200)
    return make_admin_layout(
        "admin_community",
        "Community Post Management",
        "Review, disable, or re-enable community posts and monitor forum activity.",
        "admin_community.html",
        posts=posts,
    )


@admin_required
def admin_comments_page():
    """GET /admin/community/comments — comment management by user."""
    users = list_all_users()
    user_list = [
        {
            "name":  u.get("name", u.get("email", "")),
            "email": u.get("email", ""),
        }
        for u in users
    ]
    return make_admin_layout(
        "admin_comments",
        "Comment Management",
        "Select a user to review their posts and manage comments.",
        "admin_comments.html",
        user_list=user_list,
    )


@admin_required
def admin_community_posts_api():
    """GET /admin/community/posts?email=<email> — return posts for a user (AJAX)."""
    email = flask_request.args.get("email", "").strip()
    if not email:
        return jsonify({"error": "email required"}), 400
    posts = get_forum_posts_by_user(email)
    return jsonify(posts)


@admin_required
def admin_toggle_post_api(post_id: str):
    """POST /admin/community/post/<post_id>/toggle  { disabled: bool }"""
    payload  = flask_request.get_json(silent=True) or {}
    disabled = bool(payload.get("disabled", False))
    ok = admin_disable_forum_post(post_id, disabled)
    return jsonify({"success": ok, "post_id": post_id, "disabled": disabled})


@admin_required
def admin_toggle_comment_api(post_id: str, comment_index: int):
    """POST /admin/community/post/<post_id>/comment/<comment_index>/toggle  { disabled: bool }"""
    payload  = flask_request.get_json(silent=True) or {}
    disabled = bool(payload.get("disabled", False))
    ok = admin_disable_forum_comment(post_id, comment_index, disabled)
    return jsonify({"success": ok, "post_id": post_id, "comment_index": comment_index, "disabled": disabled})
