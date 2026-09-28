from flask import Blueprint, render_template, jsonify

view_bp = Blueprint("views", __name__)

@view_bp.route("/")
def index():
    """Renders the main CyberQuest Command Center application interface."""
    return render_template("index.html")

@view_bp.route("/health")
def health():
    """System health check endpoint for monitoring."""
    return jsonify({
        "status": "operational",
        "service": "CyberQuest Learning Platform",
        "version": "1.0.0"
    }), 200
