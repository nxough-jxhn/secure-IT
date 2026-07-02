from flask import session

from database import (
    get_app_shell_context,
    get_user_dashboard_data,
    get_user_progress,
    MODULE_BADGES,
)
from secure_it import login_required, make_layout


# Namecard visual themes — used to generate CSS gradient in the template
NAMECARD_DEFS = [
    {
        "id": "social_sentinel",
        "name": "Social Sentinel",
        "type": "Category",
        "condition": "Complete all Social-Based modules",
        "condition_short": "All Social-Based modules",
        "theme": "social",
        "gradient": "linear-gradient(135deg, #1e3a5f 0%, #0d2137 60%, #1a4a6b 100%)",
        "accent": "#60a5fa",
        "icon": "💬",
        "desc": "Dark blue — chat and message motifs",
    },
    {
        "id": "malware_hunter",
        "name": "Malware Hunter",
        "type": "Category",
        "condition": "Complete all Malware-Based modules",
        "condition_short": "All Malware-Based modules",
        "theme": "malware",
        "gradient": "linear-gradient(135deg, #450a0a 0%, #1c0505 60%, #500d0d 100%)",
        "accent": "#f87171",
        "icon": "🦠",
        "desc": "Deep red — virus and bug motifs",
    },
    {
        "id": "network_warden",
        "name": "Network Warden",
        "type": "Category",
        "condition": "Complete all Network-Based modules",
        "condition_short": "All Network-Based modules",
        "theme": "network",
        "gradient": "linear-gradient(135deg, #0a3a3a 0%, #041c1c 60%, #0d4040 100%)",
        "accent": "#2dd4bf",
        "icon": "📡",
        "desc": "Teal — network and signal motifs",
    },
    {
        "id": "code_guardian",
        "name": "Code Guardian",
        "type": "Category",
        "condition": "Complete the SQL Injection module",
        "condition_short": "SQL Injection module",
        "theme": "code",
        "gradient": "linear-gradient(135deg, #052e16 0%, #021a0d 60%, #064e3b 100%)",
        "accent": "#00ff9f",
        "icon": "💻",
        "desc": "Green — code and terminal motifs",
    },
    {
        "id": "cyber_throne",
        "name": "⚡ Cyber Throne",
        "type": "Leaderboard",
        "condition": "Reach 1st place on the leaderboard",
        "condition_short": "1st place on leaderboard",
        "theme": "gold",
        "gradient": "linear-gradient(135deg, #78350f 0%, #451a03 55%, #92400e 100%)",
        "accent": "#fbbf24",
        "icon": "👑",
        "desc": "Gold — animated border, crown motif",
        "animated": True,
    },
    {
        "id": "iron_vanguard",
        "name": "🛡️ Iron Vanguard",
        "type": "Leaderboard",
        "condition": "Reach 2nd place on the leaderboard",
        "condition_short": "2nd place on leaderboard",
        "theme": "silver",
        "gradient": "linear-gradient(135deg, #374151 0%, #1f2937 55%, #4b5563 100%)",
        "accent": "#9ca3af",
        "icon": "🛡️",
        "desc": "Silver — shield motif",
    },
    {
        "id": "bronze_bastion",
        "name": "🔰 Bronze Bastion",
        "type": "Leaderboard",
        "condition": "Reach 3rd place on the leaderboard",
        "condition_short": "3rd place on leaderboard",
        "theme": "bronze",
        "gradient": "linear-gradient(135deg, #431407 0%, #27100a 55%, #5a1a09 100%)",
        "accent": "#d97706",
        "icon": "🔰",
        "desc": "Bronze — fortress motif",
    },
    {
        "id": "secureit_elite",
        "name": "👑 Secure-IT Elite",
        "type": "Ultimate",
        "condition": "Complete all 10 modules AND achieve 1,500 pts",
        "condition_short": "All modules + 1,500 pts",
        "theme": "elite",
        "gradient": "linear-gradient(135deg, #1a0533 0%, #0d0220 55%, #280550 100%)",
        "accent": "#c084fc",
        "icon": "⭐",
        "desc": "Gold animated — crown and shield, exclusive design",
        "animated": True,
        "rare": True,
    },
]

CERT_DEFS = [
    {
        "id": "performance",
        "name": "Performance Certificate",
        "icon": "📊",
        "svg": "img/certificates/performance.svg",
        "accent": "#00ff9f",
        "condition": "Available to all users at any stage",
        "condition_short": "Always available",
        "desc": (
            "Updates dynamically every time your points change. "
            "Displays your current total points, level title, modules completed, and date generated."
        ),
        "color": "#00ff9f",
    },
    {
        "id": "leaderboard",
        "name": "Leaderboard Certificate",
        "icon": "🥇",
        "svg": "img/certificates/leaderboard.svg",
        "accent": "#e07060",
        "condition": "Rank in the Top 10 of the global leaderboard",
        "condition_short": "Top 10 rank",
        "desc": (
            "Updates dynamically with your rank. Top 3 receive a gold/silver/bronze version. "
            "Reflects your last top-10 standing if your rank drops."
        ),
        "color": "#e07060",
    },
    {
        "id": "completion",
        "name": "Completion Certificate",
        "icon": "🎓",
        "svg": "img/certificates/completion.svg",
        "accent": "#60a5fa",
        "condition": "Complete all 10 modules (Easy Sim + Hard Sim + Quiz passed)",
        "condition_short": "All 10 modules complete",
        "desc": (
            "One-time permanent certificate issued when you finish every module. "
            "Displays all 10 badges earned — suitable for a portfolio or CV."
        ),
        "color": "#60a5fa",
    },
    {
        "id": "perfect_score",
        "name": "Perfect Score Certificate",
        "icon": "🏆",
        "svg": "img/certificates/perfect_score.svg",
        "accent": "#fbbf24",
        "condition": "Achieve the maximum possible score — 1,500 pts",
        "condition_short": "1,500 pts total",
        "desc": (
            "Visually distinct gold design. Extremely rare — awarded only to users who "
            "achieve the maximum possible points across all 10 modules."
        ),
        "color": "#fbbf24",
    },
]


@login_required
def collection_page():
    email = session.get("user_email", "")
    shell = get_app_shell_context(email)
    data = get_user_dashboard_data(email)
    progress = get_user_progress(email)

    completed_set = set(data.get("simulations_completed", []))
    earned_badge_names = set(data.get("badges", []))
    points = int(data.get("points", 0))
    rank = data.get("rank")

    # Determine earned namecards
    social_ids   = {"phishing_fake_email", "phishing_fake_website", "social_engineering"}
    malware_ids  = {"keylogger", "ransomware", "spyware", "adware"}
    network_ids  = {"mitm", "evil_twin"}
    sqli_ids     = {"sql_injection"}

    namecard_earned = {
        "social_sentinel":  social_ids.issubset(completed_set),
        "malware_hunter":   malware_ids.issubset(completed_set),
        "network_warden":   network_ids.issubset(completed_set),
        "code_guardian":    sqli_ids.issubset(completed_set),
        "cyber_throne":     rank == 1,
        "iron_vanguard":    rank == 2,
        "bronze_bastion":   rank == 3,
        "secureit_elite":   len(completed_set) >= 10 and points >= 1500,
    }

    active_namecard_id = progress.get("active_namecard") or data.get("active_namecard_id")

    namecards = []
    for nc in NAMECARD_DEFS:
        nc_copy = dict(nc)
        nc_copy["earned"] = namecard_earned.get(nc["id"], False)
        nc_copy["active"] = (nc["id"] == active_namecard_id)
        namecards.append(nc_copy)

    # Determine earned certificates
    cert_earned = {
        "performance":  True,
        "completion":   len(completed_set) >= 10,
        "perfect_score": points >= 1500,
        "leaderboard":  rank is not None and rank <= 10,
    }

    certificates = []
    for cert in CERT_DEFS:
        c_copy = dict(cert)
        c_copy["earned"] = cert_earned.get(cert["id"], False)
        certificates.append(c_copy)

    return make_layout(
        "collection",
        "Collection",
        "Your namecards, certificates, and earned rewards.",
        "collection.html",
        **shell,
        namecards=namecards,
        certificates=certificates,
        active_namecard_id=active_namecard_id,
        user_points=points,
        user_rank=rank,
    )


@login_required
def set_namecard_page():
    from flask import jsonify, request
    from database import update_module_progress

    payload = request.get_json(silent=True) or {}
    namecard_id = str(payload.get("namecard_id", "")).strip()
    valid_ids = {nc["id"] for nc in NAMECARD_DEFS}
    if not namecard_id or namecard_id not in valid_ids:
        return jsonify({"error": "Invalid namecard ID"}), 400

    email = session.get("user_email", "")
    if email:
        from database import _users_collection, _normalize_email
        users = _users_collection()
        if users is not None:
            try:
                users.update_one(
                    {"email": _normalize_email(email)},
                    {"$set": {"active_namecard": namecard_id}},
                )
            except Exception:
                pass

    return jsonify({"success": True})
