from .auth_routes import auth_bp
from .user_routes import user_bp
from .navigation import nav_bp
from .view_routes import view_bp

__all__ = ["auth_bp", "user_bp", "nav_bp", "view_bp"]
