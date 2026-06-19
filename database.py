from dataclasses import dataclass
from datetime import datetime, timezone
import os
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
    "total_modules": 6,
    "average_score": 78,
    "active_simulations": 5,
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

UPLOAD_DIRECTORY = Path(__file__).resolve().parent / "static" / "uploads" / "profiles"


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


def upsert_social_user(provider: str):
    collection = _users_collection()
    if collection is None:
        return None

    provider = provider.strip().lower()
    email = f"{provider}@secure-it.local"
    name = f"{provider.title()} User"
    existing_user = collection.find_one({"email": email})

    if existing_user:
        collection.update_one(
            {"email": email},
            {"$set": {"updated_at": _utcnow(), "provider": provider}},
        )
        return collection.find_one({"email": email})

    document = {
        "name": name,
        "email": _normalize_email(email),
        "password_hash": generate_password_hash(provider + "-demo-login"),
        "role": "student",
        "provider": provider,
        "email_verified": True,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
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
