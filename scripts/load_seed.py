"""
Seed data loader for the MLH PE Hackathon URL shortener.

Usage:
    uv run python scripts/load_seed.py urls.csv
    uv run python scripts/load_seed.py events.csv
    uv run python scripts/load_seed.py users.csv
"""

import csv
import os
import sys
from peewee import chunked

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.url import Url
from app.models.user import User
from app.models.event import Event


def load_urls(csv_path):
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return 0
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "user_id": int(row["user_id"]),
                "short_code": row["short_code"],
                "original_url": row["original_url"],
                "title": row["title"],
                "is_active": row["is_active"].strip() == "True",
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
    with db.atomic():
        for batch in chunked(rows, 100):
            Url.insert_many(batch).on_conflict_ignore().execute()
    return len(rows), Url

def load_users(csv_path):
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return 0
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "id": int(row["id"]),
                "username": row["username"],
                "email": row["email"],
                "created_at": row["created_at"],
            })
    with db.atomic():
        for batch in chunked(rows, 100):
            User.insert_many(batch).on_conflict_ignore().execute()
    return len(rows), User

def load_events(csv_path):
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return 0
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "url_id": int(row["url_id"]),
                "user_id": int(row["user_id"]),
                "event_type": row["event_type"],
                "timestamp": row["timestamp"],
                "details": row["details"],
            })
    with db.atomic():
        for batch in chunked(rows, 100):
            Event.insert_many(batch).on_conflict_ignore().execute()
    return len(rows), Event

def main():
    app = create_app()

    with app.app_context():
        db.create_tables([Url, User, Event], safe=True)

        csv_path = sys.argv[1] if len(sys.argv) > 1 else "urls.csv"
        
        if "urls" in csv_path:
            count, model = load_urls(csv_path)
        elif "users" in csv_path:
            count, model = load_users(csv_path)
        elif "events" in csv_path:
            count, model = load_events(csv_path)
        else:
            print("Unrecognized csv. Expected urls.csv, users.csv, or events.csv")
            return

        print(f"[OK] Loaded {count} rows into '{model._meta.table_name}' table")

        # Verify
        total = model.select().count()
        print(f"   Total rows in DB: {total}")

if __name__ == "__main__":
    main()
