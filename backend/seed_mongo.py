from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from database import DEFAULT_ATTEMPTS, DEFAULT_METRICS, DEFAULT_PROFILE, get_database


REPO_ROOT = Path(__file__).resolve().parent.parent

GAMIFICATION_COLLECTIONS = ("badges", "namecards", "certificates", "leaderboard", "simulation_retakes")


def _now():
    return datetime.now(timezone.utc)


def _ensure_collection_indexes(database, collection_name: str) -> None:
    collection = database[collection_name]
    if collection_name == "simulation_retakes":
        collection.create_index([("email", 1), ("attack_id", 1)], unique=True)
    elif collection_name == "leaderboard":
        collection.create_index("email", unique=True)
        collection.create_index([("rank", 1)])
    else:
        collection.create_index("email", unique=True)


def main() -> int:
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")

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
    else:
        metrics_collection.update_one(
            {},
            {
                "$set": {
                    "total_modules": DEFAULT_METRICS["total_modules"],
                    "active_simulations": DEFAULT_METRICS["active_simulations"],
                    "updated_at": _now(),
                }
            },
        )
        print("Updated metrics totals for 10 modules")

    if attempts_collection.count_documents({}) == 0:
        attempts_collection.insert_many([
            {"path": attempt, "created_at": _now()} for attempt in DEFAULT_ATTEMPTS
        ])
        print("Inserted default attempts")

    for collection_name in GAMIFICATION_COLLECTIONS:
        collection = database[collection_name]
        _ensure_collection_indexes(database, collection_name)
        if collection.count_documents({}) == 0:
            print(f"Ready: {collection_name} collection (empty, indexed)")

    print(f"Seeded database: {database.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
