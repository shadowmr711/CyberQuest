from flask import Blueprint, request, jsonify, session, g
from ..services.auth_service import register_user, authenticate_user
from ..utils.decorators import login_required, validate_json
from ..models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
@validate_json("username", "email", "password", "name")
def register():
    """Register a new learner account."""
    data = request.get_json()
    user, error = register_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        name=data["name"],
        experience_level=data.get("experience_level", "Complete beginner"),
        linux_exp=data.get("linux_exp", "None"),
        networking_exp=data.get("networking_exp", "None"),
        programming_exp=data.get("programming_exp", "None"),
        security_exp=data.get("security_exp", "None"),
        preferred_path=data.get("preferred_path", "Undecided")
    )
    if error:
        return jsonify({"error": error, "code": "REGISTRATION_FAILED"}), 400

    # Auto-login after registration
    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "message": "Learner profile initialized successfully.",
        "user": user.to_dict()
    }), 201

@auth_bp.route("/login", methods=["POST"])
@validate_json("username_or_email", "password")
def login():
    """Authenticate learner credentials and establish a secure session."""
    data = request.get_json()
    client_ip = request.remote_addr or "127.0.0.1"
    
    user, error = authenticate_user(
        username_or_email=data["username_or_email"],
        password=data["password"],
        client_ip=client_ip
    )
    if error:
        return jsonify({"error": error, "code": "AUTH_FAILED"}), 401

    return jsonify({
        "message": f"Welcome back to CyberQuest, {user.name}.",
        "user": user.to_dict()
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Terminate the active session."""
    session.clear()
    return jsonify({"message": "Successfully logged out of command center."}), 200

@auth_bp.route("/me", methods=["GET"])
def me():
    """Retrieve the current authenticated user's session profile."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False, "user": None}), 200
        
    user = db.session.get(User, user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False, "user": None}), 200

    return jsonify({
        "authenticated": True,
        "user": user.to_dict()
    }), 200
