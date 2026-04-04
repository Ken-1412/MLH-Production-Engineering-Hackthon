import random
import string
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from peewee import DatabaseError, IntegrityError, OperationalError
from playhouse.shortcuts import model_to_dict

from app.models.url import Url

urls_bp = Blueprint("urls", __name__)


def generate_short_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _validate_create(data):
    """Validate required fields for creating a URL."""
    errors = {}
    if not data.get("original_url"):
        errors["original_url"] = "required"
    if not data.get("title"):
        errors["title"] = "required"
    if "user_id" not in data or data["user_id"] is None:
        errors["user_id"] = "required"
    elif not isinstance(data["user_id"], (int, float)):
        try:
            int(data["user_id"])
        except (ValueError, TypeError):
            errors["user_id"] = "must be an integer"
    if "is_active" in data and not isinstance(data["is_active"], bool):
        errors["is_active"] = "must be a boolean"
    return errors


def _validate_update(data):
    """Validate fields for updating a URL (all optional, but types must be correct)."""
    errors = {}
    if "user_id" in data and data["user_id"] is not None:
        if not isinstance(data["user_id"], (int, float)):
            try:
                int(data["user_id"])
            except (ValueError, TypeError):
                errors["user_id"] = "must be an integer"
    if "is_active" in data and not isinstance(data["is_active"], bool):
        errors["is_active"] = "must be a boolean"
    if "short_code" in data and not data.get("short_code"):
        errors["short_code"] = "must not be empty"
    if "original_url" in data and not data.get("original_url"):
        errors["original_url"] = "must not be empty"
    if "title" in data and not data.get("title"):
        errors["title"] = "must not be empty"
    return errors


def _url_to_dict(url_record):
    """Convert a Url model instance to a dict."""
    d = model_to_dict(url_record)
    # Ensure datetime fields are ISO format strings
    for key in ("created_at", "updated_at"):
        if key in d and isinstance(d[key], datetime):
            d[key] = d[key].isoformat()
    return d


@urls_bp.route("/urls", methods=["GET"])
def list_urls():
    """List all URLs, with optional search filtering."""
    try:
        search = request.args.get("search", "").strip()
        user_id = request.args.get("user_id")
        query = Url.select()
        if search:
            query = query.where(
                (Url.title.contains(search)) | (Url.original_url.contains(search))
            )
        if user_id:
            try:
                query = query.where(Url.user_id == int(user_id))
            except ValueError:
                pass
        urls = list(query.order_by(Url.id))
        data = [_url_to_dict(u) for u in urls]
        return jsonify({"data": data, "count": len(data)}), 200
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503


@urls_bp.route("/urls", methods=["POST"])
def create_url():
    """Create a new URL."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON", "fields": {"body": "required"}, "code": 400}), 400

    errors = _validate_create(data)
    if errors:
        return (
            jsonify({"error": "Validation failed", "fields": errors, "code": 400}),
            400,
        )

    short_code = data.get("short_code")
    if not short_code:
        short_code = generate_short_code()

    try:
        record = Url.create(
            user_id=int(data["user_id"]),
            short_code=short_code,
            original_url=data["original_url"],
            title=data["title"],
            is_active=data.get("is_active", True),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return jsonify({"data": _url_to_dict(record)}), 201
    except IntegrityError:
        return jsonify({"error": "Resource already exists", "code": 409}), 409
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503


@urls_bp.route("/urls/<record_id>", methods=["GET"])
def get_url(record_id):
    """Get a single URL by ID."""
    record = Url.safe_get(record_id)
    if record is None:
        return jsonify({"error": "Not found", "code": 404}), 404
    return jsonify({"data": _url_to_dict(record)}), 200


@urls_bp.route("/urls/<record_id>", methods=["PUT"])
def update_url(record_id):
    """Update an existing URL."""
    record = Url.safe_get(record_id)
    if record is None:
        return jsonify({"error": "Not found", "code": 404}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON", "fields": {"body": "required"}, "code": 400}), 400

    errors = _validate_update(data)
    if errors:
        return (
            jsonify({"error": "Validation failed", "fields": errors, "code": 400}),
            400,
        )

    try:
        # Only update fields that are present in the request
        allowed_fields = ["user_id", "short_code", "original_url", "title", "is_active"]
        for field in allowed_fields:
            if field in data:
                value = data[field]
                if field == "user_id":
                    value = int(value)
                setattr(record, field, value)
        record.updated_at = datetime.now()
        record.save()
        return jsonify({"data": _url_to_dict(record)}), 200
    except IntegrityError:
        return jsonify({"error": "Resource already exists", "code": 409}), 409
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503


@urls_bp.route("/urls/<record_id>", methods=["DELETE"])
def delete_url(record_id):
    """Delete a URL by ID."""
    record = Url.safe_get(record_id)
    if record is None:
        return jsonify({"error": "Not found", "code": 404}), 404

    try:
        record.delete_instance()
        return "", 204
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503
