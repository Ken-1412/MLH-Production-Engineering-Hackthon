def register_routes(app):
    """Register all route blueprints with the Flask app."""
    from app.routes.health import health_bp
    from app.routes.urls import urls_bp
    from app.routes.users import users_bp
    from app.routes.events import events_bp
    from app.routes.ui import ui_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(ui_bp)
