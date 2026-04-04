from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes


def create_app():
    load_dotenv()

    app = Flask(__name__)

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee
    from app.database import db
    from app.models.url import Url
    from app.models.user import User
    from app.models.event import Event
    
    try:
        db.create_tables([Url, User, Event], safe=True)
    except Exception as e:
        app.logger.warning(f"Could not create tables on startup: {e}")

    register_routes(app)

    # --- Error Handlers (last-resort safety net) ---

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": getattr(e, 'description', 'Bad request'), "code": 400}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "code": 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed", "code": 405}), 405

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({"error": "Conflict", "code": 409}), 409

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "code": 500}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal server error", "code": 500}), 500

    return app
