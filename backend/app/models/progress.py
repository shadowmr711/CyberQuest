from datetime import datetime, timezone
import json
from . import db

class UserTopicMastery(db.Model):
    """Tracks learner mastery metrics per topic for the adaptive learning engine."""
    __tablename__ = "user_topic_mastery"
    __table_args__ = (
        db.UniqueConstraint("user_id", "topic_id", name="uq_user_topic"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    
    # Adaptive metrics
    mastery = db.Column(db.Float, default=0.0)             # 0.0 to 100.0 score
    confidence = db.Column(db.Float, default=0.0)          # Model confidence in mastery
    practice_accuracy = db.Column(db.Float, default=0.0)   # percentage (0.0 to 100.0)
    mistake_count = db.Column(db.Integer, default=0)
    practice_count = db.Column(db.Integer, default=0)
    lesson_completion = db.Column(db.Float, default=0.0)   # percentage
    revision_count = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="topic_masteries")
    topic = db.relationship("Topic", back_populates="masteries")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "topic_category": self.topic.category if self.topic else None,
            "mastery": round(self.mastery, 1),
            "confidence": round(self.confidence, 1),
            "practice_accuracy": round(self.practice_accuracy, 1),
            "mistake_count": self.mistake_count,
            "practice_count": self.practice_count,
            "lesson_completion": round(self.lesson_completion, 1),
            "revision_count": self.revision_count,
            "time_spent_minutes": round(self.time_spent_seconds / 60, 1),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }

class LessonProgress(db.Model):
    """Tracks completion and study time for individual lessons."""
    __tablename__ = "lesson_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False, index=True)
    completed = db.Column(db.Boolean, default=False)
    time_spent_seconds = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="lesson_progresses")
    lesson = db.relationship("Lesson", back_populates="progresses")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "completed": self.completed,
            "time_spent_seconds": self.time_spent_seconds,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }

class StudySession(db.Model):
    """Logged duration spent by activity type (learning, practicing, lab, project)."""
    __tablename__ = "study_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_type = db.Column(db.String(32), nullable=False) # 'learning', 'practicing', 'lab', 'project'
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="study_sessions")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "duration_seconds": self.duration_seconds,
            "duration_minutes": round(self.duration_seconds / 60, 1),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }

class LearningEvent(db.Model):
    """Audit log of user learning events for analytics and behavioral pacing."""
    __tablename__ = "learning_events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    event_type = db.Column(db.String(64), nullable=False) # e.g. 'lesson_viewed', 'practice_submitted', 'lab_step'
    event_data = db.Column(db.Text, nullable=True)         # JSON-encoded payload
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="learning_events")

    def get_data(self) -> dict:
        if not self.event_data:
            return {}
        try:
            return json.loads(self.event_data)
        except Exception:
            return {}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_data": self.get_data(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
