"""
seed_quiz_questions.py
One-time migration: insert all hardcoded quiz questions from simulation_data.py
into the MongoDB quiz_questions collection.

Run from the backend directory:
    python seed_quiz_questions.py
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from database import get_database
from simulation_data import ATTACKS


def _now():
    return datetime.now(timezone.utc)


def seed():
    db = get_database()
    if db is None:
        print("ERROR: Could not connect to MongoDB. Check DB_URI in .env")
        return 1

    col = db["quiz_questions"]

    # Create indexes
    col.create_index([("attack_id", 1)])
    col.create_index([("attack_id", 1), ("active", 1)])

    total_inserted = 0
    total_skipped  = 0

    for attack_id, attack in ATTACKS.items():
        questions = attack.get("quiz", [])
        if not questions:
            print(f"  SKIP  {attack_id} — no quiz questions")
            continue

        for q in questions:
            raw_question = str(q.get("question", "")).strip()
            if not raw_question:
                continue

            # Idempotent: skip if already seeded
            exists = col.find_one({
                "attack_id": attack_id,
                "question":  raw_question,
            })
            if exists:
                total_skipped += 1
                continue

            choices = list(q.get("options", []))
            correct_index = int(q.get("correct", 0))

            doc = {
                "attack_id":     attack_id,
                "question":      raw_question,
                "choices":       choices,
                "correct_index": correct_index,
                "explanation":   str(q.get("explanation", "")),
                "active":        True,
                "created_by":    "seed_script",
                "created_at":    _now(),
                "updated_at":    _now(),
            }
            col.insert_one(doc)
            total_inserted += 1

        count = col.count_documents({"attack_id": attack_id, "active": True})
        print(f"  OK    {attack_id:30s} — {count} active question(s) in DB")

    print(f"\nDone. Inserted: {total_inserted}  |  Skipped (already exist): {total_skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(seed())
