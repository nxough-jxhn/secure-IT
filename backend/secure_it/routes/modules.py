from flask import abort

from secure_it import login_required, make_layout

VALID_CATEGORIES = frozenset({"social_based", "malware_based", "network_based", "injection_based"})


@login_required
def modules_page():
    return make_layout(
        "modules",
        "Cyberattack Modules",
        "Browse all attack categories and training modules.",
        "modules/placeholder.html",
        page_kind="all",
    )


@login_required
def modules_category_page(category_id: str):
    if category_id not in VALID_CATEGORIES:
        abort(404)

    titles = {
        "social_based": "Social-Based Attacks",
        "malware_based": "Malware-Based Attacks",
        "network_based": "Network-Based Attacks",
        "injection_based": "Injection-Based Attacks",
    }

    return make_layout(
        "modules",
        titles[category_id],
        f"Modules under the {titles[category_id]} category.",
        "modules/placeholder.html",
        page_kind="category",
        category_id=category_id,
    )
