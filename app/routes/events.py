import json
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from peewee import DatabaseError, OperationalError
from playhouse.shortcuts import model_to_dict

from app.models.event import Event

events_bp = Blueprint("events", __name__)


def _event_to_dict(event_record):
    """Convert an Event model instance to a dict."""
    d = model_to_dict(event_record)
    # Ensure datetime fields are ISO format strings
    if "timestamp" in d and isinstance(d["timestamp"], datetime):
        d["timestamp"] = d["timestamp"].isoformat()
        
    # parse details back to JSON object
    if d.get("details"):
        try:
            d["details"] = json.loads(d["details"])
        except Exception:
            pass
    else:
        d["details"] = {}
        
    return d


@events_bp.route("/events", methods=["GET"])
def list_events():
    """List all events."""
    try:
        events = list(Event.select().order_by(Event.id))
        data = [_event_to_dict(e) for e in events]
        return jsonify({"data": data, "count": len(data)}), 200
    except (OperationalError, DatabaseError) as e:
        current_app.logger.error(f"DB error: {e}")
        return jsonify({"error": "Database unavailable", "code": 503}), 503
