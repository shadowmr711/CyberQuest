from functools import wraps
from flask import session, jsonify, request, g
from ..models import db, User

def login_required(f):
    """
    Authentication Guard Decorator.
    Verifies that a valid session exists and the authenticated user is stored in the database.
    Attaches the user object to flask.g.current_user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({
                "error": "Authentication required",
                "code": "UNAUTHORIZED"
            }), 401
            
        user = db.session.get(User, user_id)
        if not user:
            # Session exists but user was deleted; invalidate stale session
            session.clear()
            return jsonify({
                "error": "Session invalid or expired",
                "code": "SESSION_EXPIRED"
            }), 401
            
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def validate_json(*required_fields):
    """
    Input Validation Decorator.
    Guarantees the payload is valid JSON and contains all required non-empty fields.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    "error": "Request body must be JSON",
                    "code": "BAD_REQUEST"
                }), 400
            
            payload = request.get_json(silent=True) or {}
            missing_or_empty = [field for field in required_fields if field not in payload or str(payload[field]).strip() == ""]
            
            if missing_or_empty:
                return jsonify({
                    "error": f"Missing or empty required fields: {', '.join(missing_or_empty)}",
                    "code": "VALIDATION_ERROR",
                    "fields": missing_or_empty
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
