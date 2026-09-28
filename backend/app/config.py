import os
from pathlib import Path

# Resolve base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)

def resolve_sqlite_uri(uri: str) -> str:
    """Normalize SQLite URI into an absolute POSIX forward-slash path."""
    if not uri or not uri.startswith("sqlite:///"):
        return uri
    path_part = uri.replace("sqlite:///", "")
    if path_part == ":memory:":
        return uri
    p = Path(path_part)
    if not p.is_absolute():
        p = (BASE_DIR / p).resolve()
    else:
        p = p.resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{p.as_posix()}"

class Config:
    """Base configuration for CyberQuest."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "cyberquest-insecure-default-change-in-prod")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie Security
    # HttpOnly prevents client-side JavaScript from reading the session cookie (mitigating XSS theft)
    SESSION_COOKIE_HTTPONLY = True
    # SameSite=Lax prevents the browser from sending this cookie along with cross-site requests (CSRF mitigation)
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set to True in production to ensure cookies only travel over HTTPS
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
    
    # JSON response formatting
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    """Development configuration using local SQLite."""
    DEBUG = True
    default_db = f"sqlite:///{(DB_DIR / 'cyberquest.db').resolve().as_posix()}"
    raw_db_uri = os.environ.get("DATABASE_URL", default_db)
    SQLALCHEMY_DATABASE_URI = resolve_sqlite_uri(raw_db_uri)

class TestingConfig(Config):
    """Testing configuration using an in-memory database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration requiring explicit secure settings."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
