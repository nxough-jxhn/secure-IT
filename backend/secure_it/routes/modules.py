from flask import abort, session, redirect, url_for

from database import get_app_shell_context, get_cyber_range_categories
from secure_it import login_required, make_layout

VALID_CATEGORIES = frozenset({"social_based", "malware_based", "network_based", "injection_based"})


def modules_page():
    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    categories = get_cyber_range_categories(email)
    return make_layout(
        "modules",
        "Cyberattack Modules",
        "Browse all attack categories and training modules.",
        "modules/placeholder.html",
        **shell,
        categories=categories,
        page_kind="all",
    )


def modules_category_page(category_id: str):
    if category_id not in VALID_CATEGORIES:
        abort(404)

    titles = {
        "social_based": "Social-Based Attacks",
        "malware_based": "Malware-Based Attacks",
        "network_based": "Network-Based Attacks",
        "injection_based": "Injection-Based Attacks",
    }

    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    categories = get_cyber_range_categories(email)

    return make_layout(
        "modules",
        titles[category_id],
        f"Modules under the {titles[category_id]} category.",
        "modules/placeholder.html",
        **shell,
        categories=categories,
        page_kind="category",
        category_id=category_id,
    )
