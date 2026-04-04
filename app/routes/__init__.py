def register_routes(app):
    """Register all route blueprints with the Flask app."""
    from app.routes.health import health_bp
    from app.routes.urls import urls_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(urls_bp)
