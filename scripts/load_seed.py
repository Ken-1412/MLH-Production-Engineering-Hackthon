"""
Seed data loader for the MLH PE Hackathon URL shortener.

Usage:
    uv run python scripts/load_seed.py
"""

import csv
import os
import sys

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.url import Url


def load_urls(csv_path):
    """Load URLs from a CSV file into the database."""
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return 0

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "user_id": int(row["user_id"]),
                    "short_code": row["short_code"],
                    "original_url": row["original_url"],
                    "title": row["title"],
                    "is_active": row["is_active"].strip() == "True",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )

    from peewee import chunked

    with db.atomic():
        for batch in chunked(rows, 100):
            Url.insert_many(batch).execute()

    return len(rows)


def main():
    app = create_app()

    with app.app_context():
        db.create_tables([Url], safe=True)

        # Default path relative to project root
        csv_path = sys.argv[1] if len(sys.argv) > 1 else "urls.csv"

        count = load_urls(csv_path)
        print(f"[OK] Loaded {count} rows into '{Url._meta.table_name}' table")

        # Verify
        total = Url.select().count()
        print(f"   Total rows in DB: {total}")


if __name__ == "__main__":
    main()
