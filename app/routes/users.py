import csv
import json
from datetime import datetime
from io import StringIO

import peewee
from flask import Blueprint, current_app, jsonify, request
from peewee import DatabaseError, IntegrityError, OperationalError
from playhouse.shortcuts import model_to_dict

from app.models.user import User

users_bp = Blueprint("users", __name__)


def _user_to_dict(user_record):
    """Convert a User model instance to a dict."""
    d = model_to_dict(user_record)
    # Ensure datetime fields are ISO format strings
    if "created_at" in d and isinstance(d["created_at"], datetime):
        d["created_at"] = d["created_at"].isoformat()
    return d


def _validate_user(data):
    """Validate required fields for a User."""
    errors = {}
    if not data.get("username"):
        errors["username"] = "required"
    elif not isinstance(data.get("username"), str):
        errors["username"] = "must be a string"

    if not data.get("email"):
        errors["email"] = "required"
    elif not isinstance(data.get("email"), str):
        errors["email"] = "must be a string"
    return errors


@users_bp.route("/users/bulk", methods=["POST"])
def bulk_load_users():
    """Bulk load users from a CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided", "code": 400}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected", "code": 400}), 400

    try:
        content = file.read().decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        
        rows = []
        for row in reader:
            if not row.get("username") or not row.get("email"):
                continue
                
            created_at = row.get("created_at")
            if created_at:
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    created_at = datetime.now()
            else:
                created_at = datetime.now()

            rows.append({
                "username": row["username"],
                "email": row["email"],
                "created_at": created_at
            })
        
        with User._meta.database.atomic():
            for batch in peewee.chunked(rows, 100):
                User.insert_many(batch).on_conflict_ignore().execute()
                
        return jsonify({"count": len(rows)}), 201
    except Exception as e:
        current_app.logger.error(f"Bulk load error: {e}")
        return jsonify({"error": str(e), "code": 500}), 500


@users_bp.route("/users", methods=["GET"])
def list_users():
    """List all users."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        
        query = User.select().order_by(User.id)
        if page and per_page:
            query = query.paginate(page, per_page)
            
        users = list(query)
        data = [_user_to_dict(u) for u in users]
        return jsonify(data), 200
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503


@users_bp.route("/users/<record_id>", methods=["GET"])
def get_user(record_id):
    """Get a single user by ID."""
    record = User.safe_get(record_id)
    if record is None:
        return jsonify({"error": "Not found", "code": 404}), 404
    return jsonify(_user_to_dict(record)), 200


@users_bp.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON", "code": 400}), 400

    errors = _validate_user(data)
    if errors:
        # Returning 400 as per specification: return 400 Bad Request or 422 Unprocessable Entity
        return jsonify({"error": "Validation failed", "fields": errors, "code": 400}), 400

    try:
        record = User.create(
            username=data["username"],
            email=data["email"],
            created_at=datetime.now(),
        )
        return jsonify(_user_to_dict(record)), 201
    except IntegrityError:
        return jsonify({"error": "Resource already exists", "code": 409}), 409
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503


@users_bp.route("/users/<record_id>", methods=["PUT"])
def update_user(record_id):
    """Update an existing user."""
    record = User.safe_get(record_id)
    if record is None:
        return jsonify({"error": "Not found", "code": 404}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON", "code": 400}), 400

    # Only validate fields that are being updated
    errors = {}
    if "username" in data and not isinstance(data["username"], str):
        errors["username"] = "must be a string"
    if "email" in data and not isinstance(data["email"], str):
        errors["email"] = "must be a string"

    if errors:
        return jsonify({"error": "Validation failed", "fields": errors, "code": 400}), 400

    try:
        if "username" in data:
            record.username = data["username"]
        if "email" in data:
            record.email = data["email"]
            
        record.save()
        return jsonify(_user_to_dict(record)), 200
    except IntegrityError:
        return jsonify({"error": "Resource already exists", "code": 409}), 409
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503
