from flask import session

from database import (
    get_app_shell_context,
    get_user_dashboard_data,
    get_user_progress,
    get_leaderboard,
    MODULE_BADGES,
    LEADERBOARD_RANK_TITLES,
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
        "png": "img/namecards/namecard_social_sentinel.png",
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
        "png": "img/namecards/namecard_malware_hunter.png",
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
        "png": "img/namecards/namecard_network_warden.png",
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
        "png": "img/namecards/namecard_code_guardian.png",
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
        "png": "img/namecards/namecard_cyber_throne.png",
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
        "png": "img/namecards/namecard_iron_vanguard.png",
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
        "png": "img/namecards/namecard_bronze_bastion.png",
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
        "png": "img/namecards/namecard_secureit_elite.png",
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

    # Leaderboard data (top 10)
    leaderboard_entries = get_leaderboard(limit=10)
    display_name = session.get("display_name", "")
    for entry in leaderboard_entries:
        r = entry.get("rank", 0)
        entry["is_current_user"] = entry.get("name", "").lower() == display_name.lower()
        entry["medal"] = "🥇" if r == 1 else "🥈" if r == 2 else "🥉" if r == 3 else ""
        rank_val = entry.get("rank", 0)
        if rank_val == 1:
            entry["rank_title"] = LEADERBOARD_RANK_TITLES[1]
        elif rank_val == 2:
            entry["rank_title"] = LEADERBOARD_RANK_TITLES[2]
        elif rank_val == 3:
            entry["rank_title"] = LEADERBOARD_RANK_TITLES[3]
        elif rank_val <= 10:
            entry["rank_title"] = LEADERBOARD_RANK_TITLES["top_10"]
        else:
            entry["rank_title"] = LEADERBOARD_RANK_TITLES["default"]

    lb_top3 = leaderboard_entries[:3]
    lb_rest = leaderboard_entries[3:]

    # Badge data
    all_badges = [
        {
            "id": v["badge_id"],
            "name": v["badge_name"],
            "module": k,
            "earned": v["badge_name"] in earned_badge_names,
        }
        for k, v in MODULE_BADGES.items()
    ]
    milestone_badges = [
        {"id": "first_step",     "name": "First Step",     "icon": "👣", "condition": "Complete your first module",         "earned": len(completed_set) >= 1},
        {"id": "full_shield",    "name": "Full Shield",    "icon": "🛡️", "condition": "Complete all 10 modules",             "earned": len(completed_set) >= 10},
        {"id": "perfect_strike", "name": "Perfect Strike", "icon": "🎯", "condition": "Get 100% on any quiz",               "earned": False},
        {"id": "flawless",       "name": "Flawless",       "icon": "✨", "condition": "Get 100% on all 10 quizzes",          "earned": False},
        {"id": "persistent",     "name": "Persistent",     "icon": "💪", "condition": "Use both retakes and finish",         "earned": False},
        {"id": "unstoppable",    "name": "Unstoppable",    "icon": "⚡", "condition": "Complete all 10 Hard Sims first try", "earned": False},
    ]

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
        lb_top3=lb_top3,
        lb_rest=lb_rest,
        all_badges=all_badges,
        milestone_badges=milestone_badges,
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
