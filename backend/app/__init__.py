import os
from pathlib import Path
from flask import Flask, jsonify, request
from .config import config_by_name
from .models import db
from .services.security import apply_security_headers
from .routes import auth_bp, user_bp, nav_bp, view_bp

def create_app(config_name: str = "development") -> Flask:
    """
    Application factory for CyberQuest.
    Configures secure database connections, security headers, and API blueprints.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    frontend_dir = base_dir / "frontend"

    app = Flask(
        __name__,
        template_folder=str(frontend_dir / "templates"),
        static_folder=str(frontend_dir / "static")
    )

    # Load configuration
    selected_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(selected_config)

    # Initialize database
    db.init_app(app)

    # Security: Attach security headers to all outgoing responses
    app.after_request(apply_security_headers)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(nav_bp)
    app.register_blueprint(view_bp)

    # Global error handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found", "code": "NOT_FOUND"}), 404
        return jsonify({"error": "Page not found"}), 404

    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({"error": "Internal server error occurred", "code": "SERVER_ERROR"}), 500

    # Ensure tables exist within application context
    with app.app_context():
        db.create_all()

    return app
