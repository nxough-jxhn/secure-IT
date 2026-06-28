from dataclasses import dataclass
from datetime import datetime, timezone
import os
import secrets
from pathlib import Path
from functools import lru_cache
from typing import Any

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:  # pragma: no cover - dependency may not be installed yet
    MongoClient = None

    class PyMongoError(Exception):
        pass

from werkzeug.security import check_password_hash, generate_password_hash


@dataclass(frozen=True)
class StudentProfile:
    name: str
    level: str
    points: int
    badges: list[str]
    completion: int
    year_level: str = ""
    profile_picture: str = ""


DEFAULT_PROFILE = StudentProfile(
    name="You",
    level="Beginner",
    points=860,
    badges=["Starter Shield", "Phish Hunter", "Password Guardian"],
    completion=68,
)

DEFAULT_METRICS = {
    "modules_complete": 4,
    "total_modules": 10,
    "average_score": 78,
    "active_simulations": 10,
}

DEFAULT_ATTEMPTS = [
    "/admin/login",
    "/wp-admin",
    "/api/v1/users",
    "/admin/dashboard",
    "/backup.zip",
    "/hidden-panel",
    "/.git/config",
    "/portal/settings",
]

DEFAULT_DEMO_USERS = [
    {
        "name": "Demo Student",
        "email": "student@secure-it.local",
        "password": "student123",
        "role": "student",
    },
    {
        "name": "Demo Admin",
        "email": "admin@secure-it.local",
        "password": "admin123",
        "role": "admin",
    },
]

REPO_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIRECTORY = REPO_ROOT / "frontend" / "static" / "uploads" / "profiles"


def _default_database_name() -> str:
    return os.getenv("DB_NAME") or os.getenv("MONGO_DB_NAME") or "secure_it"


@lru_cache(maxsize=1)
def get_mongo_client():
    db_uri = os.getenv("DB_URI") or os.getenv("MONGODB_URI")
    if not db_uri or MongoClient is None:
        return None

    try:
        return MongoClient(db_uri, serverSelectionTimeoutMS=2500)
    except PyMongoError:
        return None


def get_database():
    client = get_mongo_client()
    if client is None:
        return None

    try:
        client.admin.command("ping")
    except PyMongoError:
        return None

    return client[_default_database_name()]


def _collection(name: str):
    database = get_database()
    if database is None:
        return None
    return database[name]


def _users_collection():
    collection = _collection("users")
    if collection is None:
        return None

    try:
        collection.create_index("email", unique=True)
    except PyMongoError:
        pass

    return collection


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _is_gmail_address(email: str) -> bool:
    normalized_email = _normalize_email(email)
    return normalized_email.endswith("@gmail.com") or normalized_email.endswith("@googlemail.com")


def _utcnow():
    return datetime.now(timezone.utc)


def _default_user_progress_fields() -> dict[str, Any]:
    return {
        "points": 0,
        "level": "Rookie",
        "simulations_completed": [],
        "module_progress": {},
        "simulation_retakes": {},
        "active_namecard": None,
    }


def _to_profile(document: dict | None) -> StudentProfile:
    if not document:
        return DEFAULT_PROFILE

    return StudentProfile(
        name=str(document.get("name", DEFAULT_PROFILE.name)),
        level=str(document.get("level", DEFAULT_PROFILE.level)),
        points=int(document.get("points", DEFAULT_PROFILE.points)),
        badges=list(document.get("badges", DEFAULT_PROFILE.badges)),
        completion=int(document.get("completion", DEFAULT_PROFILE.completion)),
        year_level=str(document.get("year_level", "")),
        profile_picture=str(document.get("profile_picture", "")),
    )


def get_student_profile() -> StudentProfile:
    collection = _collection("profiles")
    if collection is None:
        return DEFAULT_PROFILE

    document = collection.find_one({}, sort=[("updated_at", -1), ("_id", -1)])
    return _to_profile(document)


def get_metrics() -> dict:
    collection = _collection("metrics")
    if collection is None:
        return DEFAULT_METRICS.copy()

    document = collection.find_one({}, sort=[("updated_at", -1), ("_id", -1)])
    if not document:
        return DEFAULT_METRICS.copy()

    metrics = DEFAULT_METRICS.copy()
    metrics.update({
        "modules_complete": int(document.get("modules_complete", metrics["modules_complete"])),
        "total_modules": int(document.get("total_modules", metrics["total_modules"])),
        "average_score": int(document.get("average_score", metrics["average_score"])),
        "active_simulations": int(document.get("active_simulations", metrics["active_simulations"])),
    })
    return metrics


def get_recent_attempts() -> list[str]:
    collection = _collection("attempts")
    if collection is None:
        return DEFAULT_ATTEMPTS.copy()

    attempts: list[str] = []
    for document in collection.find({}, sort=[("created_at", -1), ("_id", -1)]).limit(20):
        attempt = document.get("path") or document.get("attempt") or document.get("value")
        if attempt:
            attempts.append(str(attempt))

    return attempts or DEFAULT_ATTEMPTS.copy()


def get_user_by_email(email: str):
    collection = _users_collection()
    if collection is None:
        return None

    return collection.find_one({"email": _normalize_email(email)})


def list_all_users() -> list[dict]:
    collection = _users_collection()
    if collection is None:
        return []

    return list(collection.find({}, sort=[("updated_at", -1)]))


def log_activity(email: str, activity_type: str, details: dict[str, Any] | None = None):
    db = get_database()
    if db is None:
        return

    try:
        db["activity_logs"].insert_one(
            {
                "email": _normalize_email(email),
                "activity_type": activity_type,
                "details": details or {},
                "created_at": _utcnow(),
            }
        )
    except PyMongoError:
        pass


def get_user_simulation_history(email: str, limit: int = 10) -> list[dict]:
    collection = _simulation_results_collection()
    if collection is None:
        return []

    return list(
        collection.find({"email": _normalize_email(email)}, sort=[("completed_at", -1)]).limit(limit)
    )


LEVEL_THRESHOLDS: list[tuple[int, str]] = [
    (0, "Rookie"),
    (300, "Aware"),
    (600, "Defender"),
    (1000, "Guardian"),
    (1300, "Cyber Shield"),
]

CATEGORY_ORDER = [
    ("social_based", "Social-Based Attacks"),
    ("malware_based", "Malware-Based Attacks"),
    ("network_based", "Network-Based Attacks"),
    ("injection_based", "Injection-Based Attacks"),
]


def _attacks_grouped_by_category() -> dict[str, list[str]]:
    try:
        from simulation_data import ATTACKS
    except ImportError:
        return {}

    grouped: dict[str, list[str]] = {}
    for attack_id, attack in ATTACKS.items():
        grouped.setdefault(str(attack.get("category", "uncategorized")), []).append(attack_id)
    return grouped


def _all_attack_ids() -> list[str]:
    try:
        from simulation_data import ATTACKS
    except ImportError:
        return []

    return list(ATTACKS.keys())


MODULE_BADGES: dict[str, dict[str, str]] = {
    "phishing_fake_email": {"badge_id": "phishing_spotter", "badge_name": "Phishing Spotter"},
    "phishing_fake_website": {"badge_id": "web_defender", "badge_name": "Web Defender"},
    "social_engineering": {"badge_id": "mind_shield", "badge_name": "Mind Shield"},
    "keylogger": {"badge_id": "key_defender", "badge_name": "Key Defender"},
    "ransomware": {"badge_id": "ransomware_survivor", "badge_name": "Ransomware Survivor"},
    "spyware": {"badge_id": "spy_catcher", "badge_name": "Spy Catcher"},
    "adware": {"badge_id": "ad_blocker", "badge_name": "Ad Blocker"},
    "mitm": {"badge_id": "mitm_detector", "badge_name": "MITM Detector"},
    "evil_twin": {"badge_id": "signal_guardian", "badge_name": "Signal Guardian"},
    "sql_injection": {"badge_id": "code_breaker", "badge_name": "Code Breaker"},
}

LEADERBOARD_RANK_TITLES = {
    1: "Top Defender",
    2: "Elite Guard",
    3: "Cyber Ace",
    "top_10": "Honor Shield",
    "default": "Active Learner",
}


def _attacks_by_category() -> dict[str, list[str]]:
    try:
        from simulation_data import ATTACKS
    except ImportError:
        return {}

    grouped: dict[str, list[str]] = {}
    for attack_id, attack in ATTACKS.items():
        category = attack.get("category") or "uncategorized"
        grouped.setdefault(category, []).append(attack_id)
    return grouped


def get_level_progress(points: int) -> dict[str, Any]:
    points = max(int(points), 0)
    current_index = 0
    for index, (threshold, _level_name) in enumerate(LEVEL_THRESHOLDS):
        if points >= threshold:
            current_index = index
        else:
            break

    current_threshold, current_level = LEVEL_THRESHOLDS[current_index]
    if current_index + 1 < len(LEVEL_THRESHOLDS):
        next_threshold, _next_level = LEVEL_THRESHOLDS[current_index + 1]
    else:
        next_threshold = current_threshold + 200

    span = max(next_threshold - current_threshold, 1)
    percent_in_level = round(((points - current_threshold) / span) * 100)

    return {
        "level_number": current_index + 1,
        "level_name": current_level,
        "current_points": points,
        "prev_threshold": current_threshold,
        "next_threshold": next_threshold,
        "percent_in_level": min(max(percent_in_level, 0), 100),
    }


def get_category_progress(module_progress: dict[str, Any], simulations_completed: list[str]) -> list[dict[str, Any]]:
    grouped = _attacks_by_category()
    completed_set = set(simulations_completed or [])
    rows: list[dict[str, Any]] = []

    for category_id, label in CATEGORY_ORDER:
        attack_ids = grouped.get(category_id, [])
        total = len(attack_ids)
        if total == 0:
            continue

        earned = 0.0
        completed_count = 0
        in_progress_count = 0
        for attack_id in attack_ids:
            entry = module_progress.get(attack_id, {})
            if entry.get("module_complete") is True:
                earned += 1.0
                completed_count += 1
            elif attack_id in completed_set or entry:
                earned += 0.35
                in_progress_count += 1

        percent = round((earned / total) * 100)
        rows.append(
            {
                "id": category_id,
                "label": label,
                "short_label": label.replace("-Based Attacks", "").strip(),
                "total": total,
                "completed": completed_count,
                "in_progress": in_progress_count,
                "percent": min(max(percent, 0), 100),
            }
        )

    return rows


def get_module_status_counts(module_progress: dict[str, Any], simulations_completed: list[str]) -> dict[str, int]:
    try:
        from simulation_data import ATTACKS
    except ImportError:
        return {"completed": 0, "in_progress": 0, "locked": 0, "total": 0}

    total = len(ATTACKS)
    completed = 0
    in_progress = 0
    completed_set = set(simulations_completed or [])

    for attack_id in ATTACKS:
        entry = module_progress.get(attack_id, {})
        if entry.get("module_complete") is True:
            completed += 1
        elif attack_id in completed_set or entry:
            in_progress += 1

    locked = max(total - completed - in_progress, 0)
    return {
        "completed": completed,
        "in_progress": in_progress,
        "locked": locked,
        "total": total,
    }


def get_next_mission(simulations_completed: list[str]) -> dict[str, Any] | None:
    try:
        from simulation_data import ATTACKS
    except ImportError:
        return None

    completed_set = set(simulations_completed or [])
    for index, attack_id in enumerate(ATTACKS.keys(), start=1):
        if attack_id in completed_set:
            continue
        attack = ATTACKS[attack_id]
        return {
            "id": attack_id,
            "name": attack["name"],
            "module_number": index,
            "category_label": attack.get("category_label", ""),
        }

    return None


def get_leaderboard(limit: int = 10) -> list[dict[str, Any]]:
    collection = _leaderboard_collection()
    if collection is not None:
        try:
            entries = list(collection.find({}, sort=[("rank", 1), ("points", -1)]).limit(limit))
            if entries:
                return [
                    {
                        "rank": int(entry.get("rank", index + 1)),
                        "name": str(entry.get("display_name") or entry.get("name") or "Learner"),
                        "points": int(entry.get("points", 0)),
                    }
                    for index, entry in enumerate(entries)
                ]
        except PyMongoError:
            pass

    users = _users_collection()
    if users is None:
        return []

    try:
        documents = list(
            users.find(
                {"role": {"$ne": "admin"}},
                {"name": 1, "points": 1, "email": 1},
            ).sort([("points", -1), ("name", 1)]).limit(limit)
        )
    except PyMongoError:
        return []

    return [
        {
            "rank": index + 1,
            "name": str(document.get("name") or document.get("email", "Learner")),
            "points": int(document.get("points", 0)),
        }
        for index, document in enumerate(documents)
    ]


def get_user_rank(email: str) -> int | None:
    user = get_user_by_email(email)
    if not user:
        return None

    points = int(user.get("points", 0))
    collection = _leaderboard_collection()
    if collection is not None:
        try:
            entry = collection.find_one({"email": _normalize_email(email)})
            if entry and entry.get("rank") is not None:
                return int(entry["rank"])
        except PyMongoError:
            pass

    users = _users_collection()
    if users is None:
        return None

    try:
        higher_ranked = users.count_documents({"role": {"$ne": "admin"}, "points": {"$gt": points}})
    except PyMongoError:
        return None

    return higher_ranked + 1


def build_active_namecard(user: dict | None, progress: dict[str, Any]) -> dict[str, Any]:
    if not user:
        return {
            "title": "Active Learner",
            "subtitle": "Secure-IT Trainee",
            "level_label": "Level 1 — Rookie",
            "theme": "default",
        }

    level_progress = get_level_progress(int(user.get("points", 0)))
    initials = "".join(part[0] for part in str(user.get("name", "Learner")).split()[:2]).upper() or "SL"

    return {
        "title": str(user.get("name", "Learner")),
        "subtitle": f"{user.get('year_level') or 'Student'} · Active Learner",
        "level_label": f"Level {level_progress['level_number']} — {user.get('level', level_progress['level_name'])}",
        "initials": initials,
        "profile_picture": str(user.get("profile_picture", "")),
        "active_namecard_id": progress.get("active_namecard") or user.get("active_namecard"),
        "theme": "default",
    }


def get_user_dashboard_data(email: str) -> dict[str, Any]:
    user = get_user_by_email(email)
    history = get_user_simulation_history(email, limit=8)
    progress = get_user_progress(email)
    metrics = get_metrics()

    badges = []
    badges_collection = _badges_collection()
    if badges_collection is not None:
        user_badges = badges_collection.find_one({"email": _normalize_email(email)})
        if user_badges:
            badges = [b["badge_name"] for b in user_badges.get("badges_earned", [])]

    sim_scores = [int(h.get("simulation_score", 0)) for h in history if h.get("simulation_score") is not None]
    quiz_scores = [int(h.get("quiz_score", 0)) for h in history if h.get("quiz_score") is not None]
    all_scores = sim_scores + quiz_scores
    average_score = round(sum(all_scores) / len(all_scores)) if all_scores else metrics.get("average_score", 0)

    module_progress = dict(user.get("module_progress", {})) if user else {}
    simulations_completed = list(progress["simulations_completed"])
    module_status = get_module_status_counts(module_progress, simulations_completed)
    completed_modules = module_status["completed"]
    total_modules = module_status["total"] or int(metrics.get("total_modules", 10))
    completion = round((completed_modules / total_modules) * 100) if total_modules else 0

    return {
        "name": user.get("name", "Student") if user else "Student",
        "year_level": str(user.get("year_level", "")) if user else "",
        "profile_picture": str(user.get("profile_picture", "")) if user else "",
        "points": progress["points"],
        "level": progress["level"],
        "completion": min(completion, 100),
        "badges": badges,
        "simulations_completed": simulations_completed,
        "history": history,
        "average_score": average_score,
        "metrics": metrics,
        "module_status": module_status,
        "category_progress": get_category_progress(module_progress, simulations_completed),
        "level_progress": get_level_progress(progress["points"]),
        "leaderboard": get_leaderboard(limit=5),
        "rank": get_user_rank(email),
        "next_mission": get_next_mission(simulations_completed),
        "namecard": build_active_namecard(user, progress),
        "pending_missions": max(total_modules - len(set(simulations_completed)), 0),
    }


def get_app_shell_context(email: str) -> dict[str, Any]:
    data = get_user_dashboard_data(email)
    profile = {
        "name": data["name"],
        "level": data["level"],
        "points": data["points"],
        "badges": data["badges"],
        "completion": data["completion"],
        "simulations_completed": data["simulations_completed"],
        "year_level": data["year_level"],
        "profile_picture": data["profile_picture"],
    }
    return {
        "profile": profile,
        "namecard": data["namecard"],
        "module_status": data["module_status"],
        "level_progress": data["level_progress"],
        "rank": data["rank"],
        "pending_missions": data["pending_missions"],
    }


def get_cyber_range_categories(email: str) -> list[dict[str, Any]]:
    try:
        from simulation_data import ATTACKS
        from simulation_missions import list_mission_summaries
    except ImportError:
        return []

    progress = get_user_progress(email)
    module_progress = progress["module_progress"]
    summaries = {mission["id"]: mission for mission in list_mission_summaries()}

    def mission_complete(attack_id: str) -> bool:
        return bool(module_progress.get(attack_id, {}).get("module_complete"))

    categories: list[dict[str, Any]] = []

    for index, (category_id, label) in enumerate(CATEGORY_ORDER, start=1):
        attack_ids = [attack_id for attack_id in ATTACKS if ATTACKS[attack_id].get("category") == category_id]
        missions: list[dict[str, Any]] = []

        for attack_id in attack_ids:
            attack = ATTACKS[attack_id]
            summary = summaries.get(attack_id, {})
            state = "completed" if mission_complete(attack_id) else "available"

            missions.append(
                {
                    "id": attack_id,
                    "name": attack["name"],
                    "icon": attack.get("icon", "🎯"),
                    "difficulty": attack.get("difficulty", "Beginner"),
                    "short_description": attack.get("short_description", ""),
                    "skills_learned": summary.get("skills_learned", [])[:3],
                    "estimated_minutes": summary.get("estimated_minutes", 12),
                    "objectives_count": summary.get("objectives_count", 5),
                    "mission_title": summary.get("mission_title", attack["name"]),
                    "state": state,
                }
            )

        categories.append(
            {
                "number": index,
                "id": category_id,
                "label": label,
                "unlocked_count": len(attack_ids),
                "total": len(attack_ids),
                "missions": missions,
            }
        )

    return categories


def list_attack_ids() -> list[str]:
    try:
        from simulation_data import ATTACKS

        return list(ATTACKS.keys())
    except ImportError:
        return []


def get_user_by_verification_token(token: str):
    collection = _users_collection()
    if collection is None:
        return None

    return collection.find_one({"verification_token": token})


def update_user_by_email(email: str, updates: dict[str, Any]):
    collection = _users_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    document_updates = dict(updates)
    document_updates["updated_at"] = _utcnow()

    try:
        collection.update_one({"email": normalized_email}, {"$set": document_updates})
    except PyMongoError:
        return None

    return collection.find_one({"email": normalized_email})


def create_pending_user(
    name: str,
    email: str,
    password: str,
    role: str = "student",
    year_level: str = "",
    profile_picture: str = "",
    verification_token: str = "",
    verification_expires_at=None,
    email_verified: bool = False,
):
    collection = _users_collection()
    if collection is None:
        return None

    document = {
        "name": name.strip(),
        "email": _normalize_email(email),
        "password_hash": generate_password_hash(password),
        "role": role,
        "provider": "local",
        "year_level": year_level.strip(),
        "profile_picture": profile_picture,
        "email_verified": email_verified,
        "verification_token": verification_token,
        "verification_expires_at": verification_expires_at,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
        **_default_user_progress_fields(),
    }

    try:
        collection.insert_one(document)
    except PyMongoError:
        return None

    return document


def create_user(name: str, email: str, password: str, role: str = "student"):
    return create_pending_user(name=name, email=email, password=password, role=role)


def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None

    if not user.get("email_verified", False) and str(os.getenv("REQUIRE_EMAIL_VERIFICATION", "true")).lower() == "true":
        return None

    password_hash = user.get("password_hash")
    if not password_hash or not check_password_hash(password_hash, password):
        return None

    return user


def ensure_demo_users():
    collection = _users_collection()
    if collection is None:
        return

    for demo_user in DEFAULT_DEMO_USERS:
        if collection.find_one({"email": demo_user["email"]}):
            continue

        try:
            collection.insert_one(
                {
                    "name": demo_user["name"],
                    "email": demo_user["email"],
                    "password_hash": generate_password_hash(demo_user["password"]),
                    "role": demo_user["role"],
                    "provider": "local",
                    "email_verified": True,
                    "created_at": _utcnow(),
                    "updated_at": _utcnow(),
                }
            )
        except PyMongoError:
            continue


def upsert_firebase_user(
    *,
    email: str,
    name: str,
    profile_picture: str = "",
    firebase_uid: str = "",
    provider: str = "google",
):
    collection = _users_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    existing_user = collection.find_one({"email": normalized_email})
    updates = {
        "name": name.strip(),
        "provider": provider.strip().lower(),
        "email_verified": True,
        "firebase_uid": firebase_uid,
        "updated_at": _utcnow(),
    }
    if profile_picture:
        updates["profile_picture"] = profile_picture

    if existing_user:
        try:
            collection.update_one({"email": normalized_email}, {"$set": updates})
        except PyMongoError:
            return None
        return collection.find_one({"email": normalized_email})

    document = {
        "name": name.strip(),
        "email": normalized_email,
        "password_hash": generate_password_hash(secrets.token_urlsafe(32)),
        "role": "student",
        "provider": provider.strip().lower(),
        "year_level": "",
        "profile_picture": profile_picture,
        "email_verified": True,
        "firebase_uid": firebase_uid,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
        **_default_user_progress_fields(),
    }

    try:
        collection.insert_one(document)
    except PyMongoError:
        return None

    return document


def is_gmail_address(email: str) -> bool:
    return _is_gmail_address(email)


def ensure_upload_directory() -> Path:
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIRECTORY


def _simulation_results_collection():
    collection = _collection("simulation_results")
    if collection is None:
        return None
    try:
        collection.create_index([("email", 1), ("attack_id", 1), ("completion_stage", 1)], unique=True)
        collection.create_index([("email", 1), ("attack_id", 1), ("completed_at", -1)])
    except PyMongoError:
        pass
    return collection


def _badges_collection():
    collection = _collection("badges")
    if collection is None:
        return None
    try:
        collection.create_index("email", unique=True)
    except PyMongoError:
        pass
    return collection


def _namecards_collection():
    collection = _collection("namecards")
    if collection is None:
        return None
    try:
        collection.create_index("email", unique=True)
    except PyMongoError:
        pass
    return collection


def _certificates_collection():
    collection = _collection("certificates")
    if collection is None:
        return None
    try:
        collection.create_index("email", unique=True)
    except PyMongoError:
        pass
    return collection


def _leaderboard_collection():
    collection = _collection("leaderboard")
    if collection is None:
        return None
    try:
        collection.create_index("email", unique=True)
        collection.create_index([("rank", 1)])
    except PyMongoError:
        pass
    return collection


def _simulation_retakes_collection():
    collection = _collection("simulation_retakes")
    if collection is None:
        return None
    try:
        collection.create_index([("email", 1), ("attack_id", 1)], unique=True)
    except PyMongoError:
        pass
    return collection


def _level_for_points(points: int) -> str:
    if points >= 1300:
        return "Cyber Shield"
    if points >= 1000:
        return "Guardian"
    if points >= 600:
        return "Defender"
    if points >= 300:
        return "Aware"
    return "Rookie"


def record_simulation_completion(
    email: str,
    attack_id: str,
    *,
    simulation_score: int,
    quiz_score: int | None = None,
    points_earned: int = 0,
    mistakes: list | None = None,
    good_actions: list | None = None,
    time_spent_seconds: int = 0,
    actions_log: list | None = None,
    skills_developed: list | None = None,
    flags_found: list | None = None,
):
    collection = _users_collection()
    results = _simulation_results_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    user = collection.find_one({"email": normalized_email})
    if not user:
        return None

    completion_stage = "quiz" if quiz_score is not None else "simulation"
    if results is not None:
        try:
            existing_result = results.find_one(
                {
                    "email": normalized_email,
                    "attack_id": attack_id,
                    "completion_stage": completion_stage,
                }
            )
        except PyMongoError:
            existing_result = None
        existing_quiz_score = int(existing_result.get("quiz_score", 0) or 0) if existing_result else 0
        if existing_result and (completion_stage == "simulation" or existing_quiz_score >= 70):
            return collection.find_one({"email": normalized_email})

    current_points = int(user.get("points", 0))
    new_points = current_points + max(points_earned, 0)
    completed = list(user.get("simulations_completed", []))
    if attack_id not in completed:
        completed.append(attack_id)

    updates = {
        "points": new_points,
        "level": _level_for_points(new_points),
        "simulations_completed": completed,
        "updated_at": _utcnow(),
    }

    try:
        collection.update_one({"email": normalized_email}, {"$set": updates})
    except PyMongoError:
        return None

    module_progress_update: dict[str, Any] = {}
    if quiz_score is not None:
        module_progress_update[f"module_progress.{attack_id}.quiz_score"] = quiz_score
        if quiz_score >= 70:
            module_progress_update[f"module_progress.{attack_id}.module_complete"] = True

    if module_progress_update:
        try:
            collection.update_one({"email": normalized_email}, {"$set": module_progress_update})
        except PyMongoError:
            pass

    result_doc = {
        "email": normalized_email,
        "attack_id": attack_id,
        "completion_stage": completion_stage,
        "simulation_score": simulation_score,
        "quiz_score": quiz_score,
        "points_earned": points_earned,
        "mistakes": mistakes or [],
        "good_actions": good_actions or [],
        "time_spent_seconds": time_spent_seconds,
        "actions_log": actions_log or [],
        "skills_developed": skills_developed or [],
        "flags_found": flags_found or [],
        "completed_at": _utcnow(),
    }

    result_wins = True
    if results is not None:
        try:
            if completion_stage == "quiz" and existing_result and int(existing_result.get("quiz_score", 0) or 0) < 70 and quiz_score is not None and quiz_score >= 70:
                write_result = results.update_one(
                    {
                        "email": normalized_email,
                        "attack_id": attack_id,
                        "completion_stage": completion_stage,
                    },
                    {"$set": result_doc, "$setOnInsert": result_doc},
                    upsert=True,
                )
                result_wins = bool(write_result.upserted_id is not None or write_result.modified_count > 0)
            elif completion_stage == "quiz" and existing_result and int(existing_result.get("quiz_score", 0) or 0) < 70:
                write_result = results.update_one(
                    {
                        "email": normalized_email,
                        "attack_id": attack_id,
                        "completion_stage": completion_stage,
                    },
                    {"$set": result_doc, "$setOnInsert": result_doc},
                    upsert=True,
                )
                result_wins = False
            else:
                write_result = results.update_one(
                    {
                        "email": normalized_email,
                        "attack_id": attack_id,
                        "completion_stage": completion_stage,
                    },
                    {"$setOnInsert": result_doc},
                    upsert=True,
                )
                result_wins = bool(write_result.upserted_id)
        except PyMongoError:
            return None

    if not result_wins:
        return collection.find_one({"email": normalized_email})

    log_activity(
        normalized_email,
        "simulation_completed",
        {
            "attack_id": attack_id,
            "simulation_score": simulation_score,
            "quiz_score": quiz_score,
            "mistakes": mistakes or [],
        },
    )

    check_and_award_badges(normalized_email)
    refresh_leaderboard()
    check_and_award_namecards(normalized_email)
    generate_certificate(normalized_email, "all")

    return collection.find_one({"email": normalized_email})


def get_user_progress(email: str) -> dict[str, Any]:
    user = get_user_by_email(email)
    if not user:
        return {
            "points": 0,
            "level": "Rookie",
            "simulations_completed": [],
            "module_progress": {},
            "simulation_retakes": {},
            "active_namecard": None,
        }

    return {
        "points": int(user.get("points", 0)),
        "level": str(user.get("level", _level_for_points(int(user.get("points", 0))))),
        "simulations_completed": list(user.get("simulations_completed", [])),
        "module_progress": dict(user.get("module_progress", {})),
        "simulation_retakes": dict(user.get("simulation_retakes", {})),
        "active_namecard": user.get("active_namecard", None),
    }


def check_and_award_badges(email: str):
    """Check badge conditions for a user and award any newly earned badges."""
    collection = _users_collection()
    badges_collection = _badges_collection()
    if collection is None or badges_collection is None:
        return None

    normalized_email = _normalize_email(email)
    user = collection.find_one({"email": normalized_email})
    if not user:
        return None

    module_progress = dict(user.get("module_progress", {}))
    completed_modules = {attack_id for attack_id, entry in module_progress.items() if entry.get("module_complete")}
    if not completed_modules:
        return None

    existing_doc = badges_collection.find_one({"email": normalized_email}) or {"badges_earned": []}
    existing_badges = {str(item.get("badge_id", "")) for item in existing_doc.get("badges_earned", [])}
    earned_badges: list[dict[str, Any]] = []

    for attack_id in completed_modules:
        badge_info = MODULE_BADGES.get(attack_id)
        if not badge_info or badge_info["badge_id"] in existing_badges:
            continue
        earned_badges.append(
            {
                "badge_id": badge_info["badge_id"],
                "badge_name": badge_info["badge_name"],
                "badge_type": "module",
                "attack_id": attack_id,
                "earned_at": _utcnow(),
            }
        )

    if completed_modules and "first_step" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "first_step",
                "badge_name": "First Step",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    all_attack_ids = set(_all_attack_ids())
    if all_attack_ids and all_attack_ids.issubset(completed_modules) and "full_shield" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "full_shield",
                "badge_name": "Full Shield",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    quiz_scores = [int(row.get("quiz_score", 0)) for row in get_user_simulation_history(normalized_email, limit=100) if row.get("quiz_score") is not None]
    if any(score == 100 for score in quiz_scores) and "perfect_strike" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "perfect_strike",
                "badge_name": "Perfect Strike",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    if len(quiz_scores) >= 10 and all(score == 100 for score in quiz_scores) and "flawless" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "flawless",
                "badge_name": "Flawless",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    retakes = [int(value) for value in dict(user.get("simulation_retakes", {})).values() if str(value).isdigit()]
    if any(count >= 2 for count in retakes) and "persistent" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "persistent",
                "badge_name": "Persistent",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    if all_attack_ids and all_attack_ids.issubset(completed_modules) and retakes and all(count == 0 for count in retakes) and "unstoppable" not in existing_badges:
        earned_badges.append(
            {
                "badge_id": "unstoppable",
                "badge_name": "Unstoppable",
                "badge_type": "milestone",
                "earned_at": _utcnow(),
            }
        )

    if not earned_badges:
        return existing_doc

    try:
        badges_collection.update_one(
            {"email": normalized_email},
            {
                "$set": {"email": normalized_email, "updated_at": _utcnow()},
                "$push": {"badges_earned": {"$each": earned_badges}},
            },
            upsert=True,
        )
    except PyMongoError:
        return None

    return badges_collection.find_one({"email": normalized_email})


def check_and_award_namecards(email: str):
    """Check namecard conditions for a user and award any newly earned namecards."""
    collection = _users_collection()
    namecards_collection = _namecards_collection()
    if collection is None or namecards_collection is None:
        return None

    normalized_email = _normalize_email(email)
    user = collection.find_one({"email": normalized_email})
    if not user:
        return None

    progress = get_user_progress(normalized_email)
    module_progress = progress.get("module_progress", {})
    completed_modules = {attack_id for attack_id, entry in module_progress.items() if entry.get("module_complete")}

    existing_doc = namecards_collection.find_one({"email": normalized_email}) or {"namecards_earned": []}
    existing_namecards = {str(item.get("namecard_id", "")) for item in existing_doc.get("namecards_earned", [])}
    earned_namecards: list[dict[str, Any]] = []

    category_rewards = {
        "social_based": ("social_sentinel", "Social Sentinel"),
        "malware_based": ("malware_hunter", "Malware Hunter"),
        "network_based": ("network_warden", "Network Warden"),
        "injection_based": ("code_guardian", "Code Guardian"),
    }
    grouped_attacks = _attacks_grouped_by_category()
    for category_id, (namecard_id, namecard_name) in category_rewards.items():
        if namecard_id in existing_namecards:
            continue
        attack_ids = grouped_attacks.get(category_id, [])
        if attack_ids and all(attack_id in completed_modules for attack_id in attack_ids):
            earned_namecards.append(
                {
                    "namecard_id": namecard_id,
                    "namecard_name": namecard_name,
                    "namecard_type": "category",
                    "earned_at": _utcnow(),
                }
            )

    current_rank = get_user_rank(normalized_email)
    leaderboard_rewards = {
        1: ("cyber_throne", "Cyber Throne"),
        2: ("iron_vanguard", "Iron Vanguard"),
        3: ("bronze_bastion", "Bronze Bastion"),
    }
    if current_rank in leaderboard_rewards:
        namecard_id, namecard_name = leaderboard_rewards[current_rank]
        if namecard_id not in existing_namecards:
            earned_namecards.append(
                {
                    "namecard_id": namecard_id,
                    "namecard_name": namecard_name,
                    "namecard_type": "leaderboard",
                    "earned_at": _utcnow(),
                }
            )

    all_attack_ids = set(_all_attack_ids())
    if all_attack_ids and all_attack_ids.issubset(completed_modules) and int(user.get("points", 0)) >= 1500 and "secure_it_elite" not in existing_namecards:
        earned_namecards.append(
            {
                "namecard_id": "secure_it_elite",
                "namecard_name": "Secure-IT Elite",
                "namecard_type": "ultimate",
                "earned_at": _utcnow(),
            }
        )

    if not earned_namecards:
        return existing_doc

    active_namecard = user.get("active_namecard") or earned_namecards[0]["namecard_id"]
    try:
        collection.update_one(
            {"email": normalized_email},
            {"$set": {"active_namecard": active_namecard, "updated_at": _utcnow()}},
        )
        namecards_collection.update_one(
            {"email": normalized_email},
            {
                "$set": {"email": normalized_email, "active_namecard": active_namecard, "updated_at": _utcnow()},
                "$push": {"namecards_earned": {"$each": earned_namecards}},
            },
            upsert=True,
        )
    except PyMongoError:
        return None

    return namecards_collection.find_one({"email": normalized_email})


def generate_certificate(email: str, cert_type: str):
    """Create or update a certificate of the given type for a user."""
    collection = _users_collection()
    certificates_collection = _certificates_collection()
    if collection is None or certificates_collection is None:
        return None

    normalized_email = _normalize_email(email)
    user = collection.find_one({"email": normalized_email})
    if not user:
        return None

    progress = get_user_progress(normalized_email)
    module_progress = progress.get("module_progress", {})
    completed_modules = {attack_id for attack_id, entry in module_progress.items() if entry.get("module_complete")}
    current_rank = get_user_rank(normalized_email)
    points = int(user.get("points", 0))

    certificates_earned: list[dict[str, Any]] = []
    if cert_type in {"performance", "all"}:
        certificates_earned.append(
            {
                "certificate_id": "performance",
                "certificate_name": "Performance Certificate",
                "certificate_type": "performance",
                "description": f"Awarded with {points} points and level {user.get('level', 'Rookie')}.",
                "issued_at": _utcnow(),
            }
        )

    all_attack_ids = set(_all_attack_ids())
    if cert_type in {"completion", "all"} and all_attack_ids and all_attack_ids.issubset(completed_modules):
        certificates_earned.append(
            {
                "certificate_id": "completion",
                "certificate_name": "Completion Certificate",
                "certificate_type": "completion",
                "description": "Awarded for completing all modules.",
                "issued_at": _utcnow(),
            }
        )

    if cert_type in {"perfect_score", "all"} and points >= 1500:
        certificates_earned.append(
            {
                "certificate_id": "perfect_score",
                "certificate_name": "Perfect Score Certificate",
                "certificate_type": "perfect_score",
                "description": "Awarded for reaching maximum points.",
                "issued_at": _utcnow(),
            }
        )

    if cert_type in {"leaderboard", "all"} and current_rank is not None and current_rank <= 10:
        rank_title = LEADERBOARD_RANK_TITLES.get(current_rank, LEADERBOARD_RANK_TITLES["top_10"])
        certificates_earned.append(
            {
                "certificate_id": "leaderboard",
                "certificate_name": "Leaderboard Certificate",
                "certificate_type": "leaderboard",
                "description": f"Awarded for reaching rank {current_rank} ({rank_title}).",
                "issued_at": _utcnow(),
            }
        )

    if not certificates_earned:
        return None

    try:
        existing_doc = certificates_collection.find_one({"email": normalized_email}) or {"certificates_earned": []}
        existing_by_id = {
            str(item.get("certificate_id", "")): item
            for item in existing_doc.get("certificates_earned", [])
            if item.get("certificate_id")
        }
        for cert in certificates_earned:
            existing_by_id[str(cert.get("certificate_id", ""))] = cert

        certificates_collection.update_one(
            {"email": normalized_email},
            {
                "$set": {
                    "email": normalized_email,
                    "certificates_earned": list(existing_by_id.values()),
                    "updated_at": _utcnow(),
                },
            },
            upsert=True,
        )
    except PyMongoError:
        return None

    return certificates_collection.find_one({"email": normalized_email})


def refresh_leaderboard():
    """Re-rank all users and update leaderboard entries and rank titles."""
    users_collection = _users_collection()
    leaderboard_collection = _leaderboard_collection()
    if users_collection is None or leaderboard_collection is None:
        return None

    try:
        ranked_users = list(users_collection.find({"role": {"$ne": "admin"}}, sort=[("points", -1), ("name", 1)]))
    except PyMongoError:
        return None

    try:
        staged_entries: list[dict[str, Any]] = []
        for index, user in enumerate(ranked_users, start=1):
            rank_title = LEADERBOARD_RANK_TITLES.get(index)
            if rank_title is None:
                rank_title = LEADERBOARD_RANK_TITLES["top_10"] if index <= 10 else LEADERBOARD_RANK_TITLES["default"]

            entry = {
                "email": _normalize_email(user.get("email", "")),
                "display_name": user.get("name", user.get("email", "Learner")),
                "points": int(user.get("points", 0)),
                "rank": index,
                "rank_title": rank_title,
                "updated_at": _utcnow(),
            }
            leaderboard_collection.update_one(
                {"email": entry["email"]},
                {"$set": entry},
                upsert=True,
            )
            users_collection.update_one(
                {"email": entry["email"]},
                {"$set": {"leaderboard_rank": index, "rank_title": rank_title, "updated_at": _utcnow()}},
            )
            staged_entries.append(entry)

        if staged_entries:
            valid_emails = [entry["email"] for entry in staged_entries]
            leaderboard_collection.delete_many({"email": {"$nin": valid_emails}})
    except PyMongoError:
        return None

    return get_leaderboard()


def get_simulation_retakes(email: str, attack_id: str):
    """Return retake usage data for a user on a specific attack module."""
    normalized_email = _normalize_email(email)
    collection = _simulation_retakes_collection()
    count = 0

    if collection is not None:
        try:
            document = collection.find_one({"email": normalized_email, "attack_id": attack_id})
        except PyMongoError:
            document = None
        if document is not None:
            count = int(document.get("count", 0))
        else:
            user = get_user_by_email(normalized_email)
            count = int(dict(user.get("simulation_retakes", {})).get(attack_id, 0)) if user else 0
    else:
        user = get_user_by_email(normalized_email)
        count = int(dict(user.get("simulation_retakes", {})).get(attack_id, 0)) if user else 0

    return {
        "email": normalized_email,
        "attack_id": attack_id,
        "count": count,
        "remaining": max(2 - count, 0),
        "max_retakes": 2,
    }


def increment_simulation_retake(email: str, attack_id: str):
    """Increment the hard simulation retake count for a user on a specific attack."""
    normalized_email = _normalize_email(email)
    retakes_collection = _simulation_retakes_collection()
    users_collection = _users_collection()
    current = get_simulation_retakes(normalized_email, attack_id)
    if int(current.get("count", 0)) >= 2:
        return current

    new_count = int(current.get("count", 0))

    if retakes_collection is not None:
        try:
            result = retakes_collection.update_one(
                {"email": normalized_email, "attack_id": attack_id, "count": {"$lt": 2}},
                {
                    "$inc": {"count": 1},
                    "$setOnInsert": {
                        "email": normalized_email,
                        "attack_id": attack_id,
                        "count": 0,
                    },
                    "$set": {"updated_at": _utcnow()},
                },
                upsert=True,
            )
        except PyMongoError:
            return None

        if result.matched_count == 0 and result.upserted_id is None:
            return current

        updated = retakes_collection.find_one({"email": normalized_email, "attack_id": attack_id}) or current
        new_count = int(updated.get("count", 0))

    if users_collection is not None:
        try:
            users_collection.update_one(
                {"email": normalized_email},
                {
                    "$set": {
                        f"simulation_retakes.{attack_id}": new_count,
                        "updated_at": _utcnow(),
                    }
                },
            )
        except PyMongoError:
            return None

    return {"email": normalized_email, "attack_id": attack_id, "count": new_count, "remaining": max(2 - new_count, 0), "max_retakes": 2}


def update_module_progress(email: str, attack_id: str, updates: dict):
    """Update module_progress fields for a user on a specific attack module."""
    collection = _users_collection()
    if collection is None:
        return None

    normalized_email = _normalize_email(email)
    set_updates = {f"module_progress.{attack_id}.{key}": value for key, value in updates.items()}
    set_updates["updated_at"] = _utcnow()

    try:
        collection.update_one({"email": normalized_email}, {"$set": set_updates})
    except PyMongoError:
        return None

    return collection.find_one({"email": normalized_email})
