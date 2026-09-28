from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    """User account model for CyberQuest learners."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Self-assessed onboarding background
    experience_level = db.Column(db.String(32), default="Complete beginner")
    linux_exp = db.Column(db.String(32), default="None")
    networking_exp = db.Column(db.String(32), default="None")
    programming_exp = db.Column(db.String(32), default="None")
    security_exp = db.Column(db.String(32), default="None")
    preferred_path = db.Column(db.String(32), default="Undecided")
    current_path = db.Column(db.String(32), default="Foundations")
    
    # Diagnostic assessment completion status
    diagnostic_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    topic_masteries = db.relationship("UserTopicMastery", back_populates="user", cascade="all, delete-orphan")
    lesson_progresses = db.relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    practice_attempts = db.relationship("PracticeAttempt", back_populates="user", cascade="all, delete-orphan")
    lab_progresses = db.relationship("LabProgress", back_populates="user", cascade="all, delete-orphan")
    project_progresses = db.relationship("ProjectProgress", back_populates="user", cascade="all, delete-orphan")
    study_sessions = db.relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    learning_events = db.relationship("LearningEvent", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        """Hash the plain text password using PBKDF2 with SHA-256 and a random salt."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        """Verify password against the stored hash in constant time to prevent timing attacks."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Serialize user into a safe dictionary."""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "experience_level": self.experience_level,
            "linux_exp": self.linux_exp,
            "networking_exp": self.networking_exp,
            "programming_exp": self.programming_exp,
            "security_exp": self.security_exp,
            "preferred_path": self.preferred_path,
            "current_path": self.current_path,
            "diagnostic_completed": self.diagnostic_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        return data

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}'>"
