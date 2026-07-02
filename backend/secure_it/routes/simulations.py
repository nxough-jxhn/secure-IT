import json
import time

from flask import abort, jsonify, redirect, render_template, request, session, url_for

from database import (
    get_app_shell_context,
    get_cyber_range_categories,
    get_level_progress,
    get_simulation_retakes,
    increment_simulation_retake,
    get_user_by_email,
    get_user_progress,
    get_user_rank,
    record_simulation_completion,
    update_module_progress,
)
from secure_it import login_required, make_layout
from simulation_data import get_attack
from simulation_missions import get_workspace_mission


def _require_mission(attack_id: str):
    mission = get_workspace_mission(attack_id)
    if not mission:
        abort(404)
    return mission


def _require_attack(attack_id: str):
    attack = get_attack(attack_id)
    if not attack:
        abort(404)
    return attack


def _module_progress_entry(email: str, attack_id: str) -> dict:
    progress = get_user_progress(email)
    return dict(progress.get("module_progress", {}).get(attack_id, {}))


def _render_attack_info_page(attack_id: str, attack: dict):
    email = session.get("user_email", "")
    update_module_progress(email, attack_id, {"info_viewed": True})
    module_progress = _module_progress_entry(email, attack_id)
    shell = get_app_shell_context(email)
    overview = attack.get("overview", {})
    info_page = attack.get("info_page", {})

    return make_layout(
        "simulations",
        attack["name"],
        attack.get("category_label", ""),
        "modules/attack_info.html",
        **shell,
        attack=attack,
        attack_id=attack_id,
        overview=overview,
        info_page=info_page,
        module_progress=module_progress,
    )


@login_required
def simulations_page():
    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    categories = get_cyber_range_categories(email)
    return make_layout(
        "simulations",
        "Cyber Range",
        "Select a mission room, review the briefing, then enter the interactive workspace.",
        "simulations.html",
        **shell,
        categories=categories,
    )


@login_required
def simulation_overview_page(attack_id: str):
    attack = _require_attack(attack_id)
    if attack.get("info_page"):
        return _render_attack_info_page(attack_id, attack)

    mission = _require_mission(attack_id)
    progress = get_user_progress(session.get("user_email", ""))
    completed = attack_id in progress.get("simulations_completed", [])
    return make_layout(
        "simulations",
        mission["mission_title"],
        "Mission briefing — review objectives before entering the lab.",
        "simulation_mission.html",
        mission=mission,
        completed=completed,
    )


@login_required
def phishing_fake_email_page():
    return simulation_overview_page("phishing_fake_email")


EASY_SIMULATION_PAGES: dict[str, dict[str, str]] = {
    "phishing_fake_email": {
        "template": "simulations/phishing_easy.html",
        "interface_key": "email_data",
    },
    "sql_injection": {
        "template": "simulations/sql_injection_easy.html",
        "interface_key": "form_data",
    },
    "social_engineering": {
        "template": "simulations/social_engineering_easy.html",
        "interface_key": "call_data",
    },
    "mitm": {
        "template": "simulations/mitm_easy.html",
        "interface_key": "browser_data",
    },
}


@login_required
def simulation_easy_page(attack_id: str):
    attack = _require_attack(attack_id)
    page_config = EASY_SIMULATION_PAGES.get(attack_id)
    if not page_config:
        abort(404)

    email = session.get("user_email", "")
    module_progress = _module_progress_entry(email, attack_id)
    if not module_progress.get("info_viewed"):
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    easy = attack.get("easy_simulation", {})
    first_step = (easy.get("steps") or [{}])[0]
    interface = first_step.get("interface", {})
    indicators = easy.get("indicators", [])

    context = {
        "attack": attack,
        "attack_id": attack_id,
        page_config["interface_key"]: interface,
        "indicators": indicators,
        "complete_url": url_for("simulation_easy_complete_page", attack_id=attack_id),
        "back_url": url_for("simulation_overview_page", attack_id=attack_id),
    }

    return render_template(page_config["template"], **context)


@login_required
def simulation_easy_complete_page(attack_id: str):
    if request.method != "POST":
        abort(405)

    _require_attack(attack_id)
    email = session.get("user_email", "")
    if email:
        update_module_progress(email, attack_id, {"easy_complete": True})

    return jsonify(
        {
            "success": True,
            "redirect": url_for("simulation_overview_page", attack_id=attack_id),
        }
    )


@login_required
def simulation_start_page(attack_id: str):
    attack = get_attack(attack_id)
    if attack and attack.get("info_page"):
        email = session.get("user_email", "")
        module_progress = _module_progress_entry(email, attack_id)
        if not module_progress.get("easy_complete"):
            return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    _require_mission(attack_id)
    session[f"sim_started_{attack_id}"] = True
    session[f"sim_started_at_{attack_id}"] = int(time.time())
    session.pop(f"sim_result_{attack_id}", None)
    session.pop(f"quiz_result_{attack_id}", None)
    return redirect(url_for("simulation_play_page", attack_id=attack_id))


@login_required
def simulation_play_page(attack_id: str):
    mission = _require_mission(attack_id)
    if not session.get(f"sim_started_{attack_id}"):
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    workspace_payload = {
        "attack_id": mission["attack_id"],
        "name": mission["name"],
        "mission_title": mission["mission_title"],
        "objectives": mission.get("objectives", []),
        "tools": mission.get("tools", []),
        "skills_learned": mission.get("skills_learned", []),
        "inbox": mission.get("inbox", {}),
        "logs": mission.get("logs", []),
        "terminal_responses": mission.get("terminal_responses", {}),
        "terminal_help": mission.get("terminal_help", "Type help"),
        "tasks": mission.get("tasks", []),
        "decisions": mission.get("decisions", []),
        "complete_url": url_for("simulation_complete_page", attack_id=attack_id),
        "briefing_url": url_for("simulation_overview_page", attack_id=attack_id),
        "gmail_mode": mission.get("gmail_mode", False),
        "sqli_mode": mission.get("sqli_mode", False),
        "email": mission.get("email", {}),
        "signs": mission.get("signs", []),
        "url_analysis": mission.get("url_analysis", {}),
        "login_form": mission.get("login_form", {}),
        "request_inspector": mission.get("request_inspector", {}),
    }

    if mission.get("gmail_mode"):
        template = "simulations/phishing_hard.html"
    elif mission.get("sqli_mode"):
        template = "simulations/sql_injection_hard.html"
    elif mission.get("sim_template"):
        # Each custom attack sets sim_template to its dedicated hard sim HTML
        template = mission["sim_template"]
    else:
        template = "simulation_workspace.html"

    return make_layout(
        "simulations",
        mission["mission_title"],
        "Interactive investigation workspace",
        template,
        mission=mission,
        workspace_data=workspace_payload,
    )


@login_required
def simulation_complete_page(attack_id: str):
    mission = _require_mission(attack_id)
    if request.method != "POST":
        return redirect(url_for("simulation_play_page", attack_id=attack_id))

    payload = request.get_json(silent=True) or {}
    def _safe_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _safe_list(value):
        return list(value) if isinstance(value, list) else []

    score = max(0, min(100, _safe_int(payload.get("score", 0))))
    good_decisions = _safe_list(payload.get("good_decisions"))
    mistakes = _safe_list(payload.get("mistakes"))
    recommendations = _safe_list(payload.get("recommendations"))
    actions_log = _safe_list(payload.get("actions_log"))
    time_spent_seconds = max(0, _safe_int(payload.get("time_spent_seconds", 0)))
    skills_developed = _safe_list(payload.get("skills_developed")) or list(mission.get("skills_learned", []))
    flags_found = _safe_list(payload.get("flags_found"))
    started_at = session.get(f"sim_started_at_{attack_id}")
    if started_at and not time_spent_seconds:
        time_spent_seconds = max(0, int(time.time()) - int(started_at))

    points_earned = max(10, score // 2)
    max_mission_points = 50

    email = session.get("user_email")
    profile_delta = {}
    if email:
        before_progress = get_user_progress(email)
        before_rank = get_user_rank(email)
        profile_delta = {
            "points_before": before_progress["points"],
            "level_before": before_progress["level"],
            "rank_before": before_rank,
        }

    result = {
        "score": score,
        "good_decisions": good_decisions,
        "mistakes": mistakes,
        "recommendations": recommendations,
        "points_earned": points_earned,
        "max_mission_points": max_mission_points,
        "time_spent_seconds": time_spent_seconds,
        "skills_developed": skills_developed,
        "actions_log": actions_log,
        "flags_found": flags_found,
    }

    if email:
        progress = get_user_progress(email)
        module_progress = progress.get("module_progress", {}).get(attack_id, {})
        already_completed = bool(module_progress.get("module_complete"))
        user = get_user_by_email(email)
        progress_updates = None

        if mission.get("gmail_mode") or mission.get("sqli_mode"):
            retake_data = get_simulation_retakes(email, attack_id)
            retake_count = int(retake_data.get("count", 0))
            if retake_count < 2 and not already_completed:
                increment_simulation_retake(email, attack_id)
            else:
                user = record_simulation_completion(
                    email,
                    attack_id,
                    simulation_score=score,
                    points_earned=points_earned,
                    mistakes=mistakes,
                    good_actions=good_decisions,
                    time_spent_seconds=time_spent_seconds,
                    actions_log=actions_log,
                    skills_developed=skills_developed,
                    flags_found=flags_found,
                )
                progress_updates = {"hard_complete": True}
                if flags_found:
                    progress_updates["hard_flags_found"] = flags_found
                    progress_updates["hard_flags_count"] = len(flags_found)
        else:
            user = record_simulation_completion(
                email,
                attack_id,
                simulation_score=score,
                points_earned=points_earned,
                mistakes=mistakes,
                good_actions=good_decisions,
                time_spent_seconds=time_spent_seconds,
                actions_log=actions_log,
                skills_developed=skills_developed,
                flags_found=flags_found,
            )
            progress_updates = {"hard_complete": True}
            if flags_found:
                progress_updates["hard_flags_found"] = flags_found
                progress_updates["hard_flags_count"] = len(flags_found)

        if progress_updates:
            update_module_progress(email, attack_id, progress_updates)

        if user:
            after_rank = get_user_rank(email)
            after_points = int(user.get("points", 0))
            after_level = str(user.get("level", profile_delta.get("level_before", "")))
            rank_before = profile_delta.get("rank_before")
            rank_direction = "same"
            if rank_before and after_rank:
                if after_rank < rank_before:
                    rank_direction = "up"
                elif after_rank > rank_before:
                    rank_direction = "down"

            profile_delta.update(
                {
                    "points_after": after_points,
                    "points_earned": points_earned,
                    "level_after": after_level,
                    "level_changed": profile_delta.get("level_before") != after_level,
                    "rank_after": after_rank,
                    "rank_direction": rank_direction,
                    "level_progress": get_level_progress(after_points),
                }
            )
            result["profile_delta"] = profile_delta

    session[f"sim_result_{attack_id}"] = result

    return jsonify({"success": True, "redirect": url_for("simulation_results_page", attack_id=attack_id)})


@login_required
def simulation_results_page(attack_id: str):
    mission = _require_mission(attack_id)
    result = session.get(f"sim_result_{attack_id}")
    if not result:
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    minutes = result.get("time_spent_seconds", 0) // 60
    seconds = result.get("time_spent_seconds", 0) % 60

    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    profile_delta = result.get("profile_delta", {})
    max_pts = result.get("max_mission_points", 50)
    points_pct = round((result.get("points_earned", 0) / max(max_pts, 1)) * 100)

    return make_layout(
        "simulations",
        "Mission Debrief",
        f"Performance report for {mission['name']}.",
        "simulation_results.html",
        mission=mission,
        result=result,
        time_display=f"{minutes}m {seconds}s",
        profile_delta=profile_delta,
        points_pct=points_pct,
        max_mission_points=max_pts,
        **shell,
    )


@login_required
def simulation_quiz_page(attack_id: str):
    mission = _require_mission(attack_id)
    if not session.get(f"sim_result_{attack_id}"):
        return redirect(url_for("simulation_overview_page", attack_id=attack_id))

    quiz_data = {
        "attack_id": mission["attack_id"],
        "name": mission["name"],
        "questions": mission.get("quiz", []),
        "submit_url": url_for("simulation_quiz_submit_page", attack_id=attack_id),
        "simulations_url": url_for("simulations_page"),
    }
    shell = get_app_shell_context(session.get("user_email", ""))
    return make_layout(
        "simulations",
        f"{mission['name']} Quiz",
        "Scenario-based knowledge check",
        "simulation_quiz.html",
        mission=mission,
        quiz_data=quiz_data,
        **shell,
    )


@login_required
def simulation_quiz_submit_page(attack_id: str):
    mission = _require_mission(attack_id)
    if request.method != "POST":
        return redirect(url_for("simulation_quiz_page", attack_id=attack_id))

    payload = request.get_json(silent=True) or {}
    answers = payload.get("answers", [])
    questions = mission.get("quiz", [])
    correct_count = 0
    feedback = []

    for index, question in enumerate(questions):
        try:
            selected = int(answers[index]) if index < len(answers) else -1
        except (TypeError, ValueError):
            selected = -1
        is_correct = selected == question["correct"]
        if is_correct:
            correct_count += 1
        feedback.append(
            {
                "question": question["question"],
                "correct": is_correct,
                "explanation": question["explanation"],
                "selected": selected,
                "correct_index": question["correct"],
                "options": question["options"],
            }
        )

    total = len(questions) or 1
    quiz_score = round((correct_count / total) * 100)
    quiz_points = max(5, quiz_score // 3)

    sim_result = session.get(f"sim_result_{attack_id}", {})
    session[f"quiz_result_{attack_id}"] = {
        "score": quiz_score,
        "correct_count": correct_count,
        "total": total,
        "feedback": feedback,
        "points_earned": quiz_points,
    }

    email = session.get("user_email")
    if email:
        record_simulation_completion(
            email,
            attack_id,
            simulation_score=int(sim_result.get("score", 0)),
            quiz_score=quiz_score,
            points_earned=quiz_points,
            mistakes=sim_result.get("mistakes", []),
            good_actions=sim_result.get("good_decisions", []),
            time_spent_seconds=int(sim_result.get("time_spent_seconds", 0)),
            skills_developed=sim_result.get("skills_developed", []),
        )

    return jsonify(
        {
            "success": True,
            "score": quiz_score,
            "correct_count": correct_count,
            "total": total,
            "points_earned": quiz_points,
            "feedback": feedback,
            "redirect": url_for("simulations_page"),
        }
    )
