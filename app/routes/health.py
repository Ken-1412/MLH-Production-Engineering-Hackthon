from flask import Blueprint, jsonify

from app.database import db

health_bp = Blueprint("health", __name__)


@health_bp.route("/health")
def health():
    db_status = "disconnected"
    try:
        db.execute_sql("SELECT 1")
        db_status = "connected"
    except Exception:
        pass
    # ALWAYS 200 — /health is a liveness probe, not a readiness probe.
    # The process is alive even if DB is temporarily down.
    return jsonify({"status": "ok", "db": db_status}), 200
