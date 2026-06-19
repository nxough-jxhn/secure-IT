from datetime import datetime, timezone
from pathlib import Path
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from database import DEFAULT_ATTEMPTS, DEFAULT_METRICS, DEFAULT_PROFILE, get_database


BASE_DIR = Path(__file__).resolve().parent


def _now():
    return datetime.now(timezone.utc)


def main() -> int:
    if load_dotenv is not None:
        load_dotenv(BASE_DIR / ".env")

    database = get_database()
    if database is None:
        print("MongoDB connection not available. Check DB_URI and network access.")
        return 1

    profile_collection = database["profiles"]
    metrics_collection = database["metrics"]
    attempts_collection = database["attempts"]

    if profile_collection.count_documents({}) == 0:
        profile_collection.insert_one({
            "name": DEFAULT_PROFILE.name,
            "level": DEFAULT_PROFILE.level,
            "points": DEFAULT_PROFILE.points,
            "badges": DEFAULT_PROFILE.badges,
            "completion": DEFAULT_PROFILE.completion,
            "created_at": _now(),
            "updated_at": _now(),
        })
        print("Inserted default profile")

    if metrics_collection.count_documents({}) == 0:
        metrics_document = DEFAULT_METRICS.copy()
        metrics_document.update({"created_at": _now(), "updated_at": _now()})
        metrics_collection.insert_one(metrics_document)
        print("Inserted default metrics")

    if attempts_collection.count_documents({}) == 0:
        attempts_collection.insert_many([
            {"path": attempt, "created_at": _now()} for attempt in DEFAULT_ATTEMPTS
        ])
        print("Inserted default attempts")

    print(f"Seeded database: {database.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())