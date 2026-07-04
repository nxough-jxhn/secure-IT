from flask import redirect, request, session, url_for, jsonify

from secure_it import login_required, make_layout
from database import (
    add_forum_post_comment,
    create_forum_post,
    delete_forum_post,
    edit_forum_post_comment,
    delete_forum_post_comment,
    get_app_shell_context,
    list_forum_posts,
    toggle_forum_post_like,
    update_forum_post,
)
from cloudinary_uploader import upload_profile_picture  # reuse for community images

FORUM_CATEGORIES = ["General", "Tips & Tricks", "Challenge Help", "Showcase", "Question"]


def _upload_images(files) -> list[str]:
    """Upload up to 4 images and return a list of URLs."""
    urls: list[str] = []
    for f in files[:4]:
        if not f or not f.filename:
            continue
        mime = getattr(f, "mimetype", "") or ""
        if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
            continue
        header = f.stream.read(12)
        f.stream.seek(0)
        is_valid = (
            header.startswith(b"\xff\xd8\xff")
            or header.startswith(b"\x89PNG\r\n\x1a\n")
            or (header[:4] == b"RIFF" and header[8:12] == b"WEBP")
            or header[:6] in (b"GIF87a", b"GIF89a")
        )
        if not is_valid:
            continue
        url = upload_profile_picture(f)
        if url:
            urls.append(url)
    return urls


@login_required
def forum_page():
    email     = session.get("user_email", "")
    shell     = get_app_shell_context(email)
    error     = None
    success   = None

    if request.method == "POST":
        action  = request.form.get("action", "create")
        post_id = request.form.get("post_id", "")
        content = (request.form.get("content", "") or "").strip()

        if action == "create":
            title    = (request.form.get("title", "") or "").strip()
            category = (request.form.get("category", "General") or "General").strip()
            if category not in FORUM_CATEGORIES:
                category = "General"

            if not title:
                error = "Post title is required."
            elif not content:
                error = "Post description is required."
            else:
                # Upload up to 4 images
                files  = request.files.getlist("images")
                images = _upload_images(files)
                create_forum_post(
                    email=email,
                    author_name=session.get("display_name", "Secure-IT Learner"),
                    profile_picture=session.get("profile_picture", ""),
                    title=title,
                    category=category,
                    content=content,
                    images=images,
                )
                return redirect(url_for("forum_page", posted="1"))

        elif action == "like":
            if not post_id:
                error = "Unable to like this post."
            else:
                toggle_forum_post_like(post_id=post_id, email=email)
                return redirect(url_for("forum_page", _anchor="posts"))

        elif action == "comment":
            if not post_id:
                error = "Unable to find the post."
            elif not content:
                error = "Write a comment before posting."
            elif add_forum_post_comment(
                post_id=post_id,
                email=email,
                author_name=session.get("display_name", "Secure-IT Learner"),
                profile_picture=session.get("profile_picture", ""),
                content=content,
            ):
                return redirect(url_for("forum_page", commented="1"))
            else:
                error = "Unable to submit your comment."

        elif action == "delete":
            if not post_id:
                error = "Unable to find the post to delete."
            elif delete_forum_post(post_id=post_id, email=email):
                return redirect(url_for("forum_page", deleted="1"))
            else:
                error = "You can only delete your own post."

        else:
            error = "Unknown forum action."

    if request.args.get("posted")     == "1": success = "Your post is live."
    elif request.args.get("commented") == "1": success = "Comment added."
    elif request.args.get("deleted")  == "1": success = "Post deleted."

    posts = list_forum_posts(limit=60, viewer_email=email)
    return make_layout(
        "community",
        "Community Forum",
        "Share tips, questions, and challenge highlights.",
        "community.html",
        **shell,
        posts=posts,
        categories=FORUM_CATEGORIES,
        error=error,
        success=success,
    )


@login_required
def forum_like_api(post_id: str):
    """POST /community/like/<post_id> — AJAX like toggle."""
    email = session.get("user_email", "")
    ok = toggle_forum_post_like(post_id=post_id, email=email)
    return jsonify({"success": ok})


@login_required
def forum_comment_api(post_id: str):
    """POST /community/comment/<post_id> — AJAX add comment."""
    email   = session.get("user_email", "")
    payload = request.get_json(silent=True) or {}
    content = str(payload.get("content", "")).strip()
    if not content:
        return jsonify({"error": "Empty comment"}), 400
    ok = add_forum_post_comment(
        post_id=post_id,
        email=email,
        author_name=session.get("display_name", "Secure-IT Learner"),
        profile_picture=session.get("profile_picture", ""),
        content=content,
    )
    if ok:
        return jsonify({
            "success": True,
            "author_name":     session.get("display_name", "Learner"),
            "profile_picture": session.get("profile_picture", ""),
            "content":         content,
        })
    return jsonify({"error": "Failed to add comment"}), 500


@login_required
def forum_delete_api(post_id: str):
    """DELETE /community/post/<post_id>"""
    email = session.get("user_email", "")
    ok = delete_forum_post(post_id=post_id, email=email)
    return jsonify({"success": ok})


@login_required
def forum_edit_comment_api(post_id: str, comment_index: int):
    """PATCH /community/comment/<post_id>/<comment_index>"""
    email   = session.get("user_email", "")
    payload = request.get_json(silent=True) or {}
    content = str(payload.get("content", "")).strip()
    if not content:
        return jsonify({"error": "Empty content"}), 400
    ok = edit_forum_post_comment(post_id, email, comment_index, content)
    return jsonify({"success": ok})


@login_required
def forum_delete_comment_api(post_id: str, comment_index: int):
    """DELETE /community/comment/<post_id>/<comment_index>"""
    email = session.get("user_email", "")
    ok = delete_forum_post_comment(post_id, email, comment_index)
    return jsonify({"success": ok})
