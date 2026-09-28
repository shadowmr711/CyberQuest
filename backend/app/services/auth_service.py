import re
from typing import Tuple, Optional
from flask import session
from ..models import db, User, LearningEvent
from .security import is_rate_limited, record_failed_attempt, clear_attempts

"""
CYBERSECURITY CONCEPT: Authentication & Credential Storage
==========================================================
1. Authentication (AuthN) is verifying the claimed identity of a principal ("Who are you?").
   Authorization (AuthZ) is determining what that authenticated principal can do ("What are you allowed to touch?").
2. Passwords should NEVER be stored in plain text or using simple fast hashes (e.g. MD5, SHA1).
   CyberQuest uses PBKDF2 with SHA-256 and an automatic per-user cryptographically random salt.
   The salt prevents pre-computed dictionary / rainbow table attacks.
3. Timing Attacks: String comparisons like `a == b` can leak information by returning early on the first mismatched
   character. Werkzeug's `check_password_hash` uses HMAC-based constant-time comparison.
4. Session Fixation: When a user authenticates, CyberQuest clears the previous anonymous session to prevent an attacker
   from hijacking a pre-seeded session identifier.
"""

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{3,32}$")

def validate_registration_input(username: str, email: str, password: str, name: str) -> Optional[str]:
    """Validates user registration input for format, length, and sanity."""
    if not username or not USERNAME_REGEX.match(username):
        return "Username must be 3-32 characters long and contain only letters, numbers, underscores, dashes, or dots."
    
    if not email or not EMAIL_REGEX.match(email):
        return "Invalid email address format."
        
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
        
    if not name or len(name.strip()) < 2:
        return "Please provide your full or display name."
        
    return None

def register_user(
    username: str,
    email: str,
    password: str,
    name: str,
    experience_level: str = "Complete beginner",
    linux_exp: str = "None",
    networking_exp: str = "None",
    programming_exp: str = "None",
    security_exp: str = "None",
    preferred_path: str = "Undecided"
) -> Tuple[Optional[User], Optional[str]]:
    """Registers a new user account with hashed password and initial profile."""
    val_error = validate_registration_input(username, email, password, name)
    if val_error:
        return None, val_error

    # Check for existing user or email
    clean_username = username.strip().lower()
    clean_email = email.strip().lower()

    if User.query.filter_by(username=clean_username).first():
        return None, "Username is already registered."

    if User.query.filter_by(email=clean_email).first():
        return None, "Email is already registered."

    user = User(
        username=clean_username,
        email=clean_email,
        name=name.strip(),
        experience_level=experience_level,
        linux_exp=linux_exp,
        networking_exp=networking_exp,
        programming_exp=programming_exp,
        security_exp=security_exp,
        preferred_path=preferred_path,
        current_path="Foundations"
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Log learning event for onboarding
    event = LearningEvent(
        user_id=user.id,
        event_type="user_registered",
        event_data='{"track": "Foundations"}'
    )
    db.session.add(event)
    db.session.commit()

    return user, None

def authenticate_user(username_or_email: str, password: str, client_ip: str = "127.0.0.1") -> Tuple[Optional[User], Optional[str]]:
    """
    Authenticates a user against stored hash, enforcing rate limits and session fixation defense.
    """
    if is_rate_limited(client_ip):
        return None, "Too many failed login attempts. Please wait 5 minutes before trying again."

    clean_identifier = username_or_email.strip().lower()
    user = User.query.filter(
        (User.username == clean_identifier) | (User.email == clean_identifier)
    ).first()

    if not user or not user.check_password(password):
        record_failed_attempt(client_ip)
        return None, "Invalid username/email or password."

    # Successful authentication: clear failure history
    clear_attempts(client_ip)

    # Mitigate Session Fixation: Reset session and bind fresh user_id
    session.clear()
    session["user_id"] = user.id
    session.permanent = True

    # Log successful login event
    event = LearningEvent(
        user_id=user.id,
        event_type="user_login",
        event_data=f'{{"ip": "{client_ip}"}}'
    )
    db.session.add(event)
    db.session.commit()

    return user, None
