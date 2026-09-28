from datetime import datetime, timezone
import json
from . import db

class Lab(db.Model):
    """Hands-on cybersecurity labs scoped strictly to authorized environments."""
    __tablename__ = "labs"

    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(32), default="Foundations") # 'Foundations', 'Red Team', 'Blue Team'
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True, index=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    
    # 8-part lab specification from CyberQuest design
    objective = db.Column(db.Text, nullable=False)
    environment = db.Column(db.Text, nullable=False)
    prerequisites = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    hints_json = db.Column(db.Text, nullable=True) # JSON array of hints
    expected_outcome = db.Column(db.Text, nullable=False)
    evidence_instructions = db.Column(db.Text, nullable=False)
    
    difficulty = db.Column(db.String(20), default="Medium")
    order_index = db.Column(db.Integer, default=0)

    topic = db.relationship("Topic")
    progresses = db.relationship("LabProgress", back_populates="lab", cascade="all, delete-orphan")

    def get_hints(self) -> list:
        if not self.hints_json:
            return []
        try:
            return json.loads(self.hints_json)
        except Exception:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "track": self.track,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "slug": self.slug,
            "title": self.title,
            "objective": self.objective,
            "environment": self.environment,
            "prerequisites": self.prerequisites,
            "instructions": self.instructions,
            "hints": self.get_hints(),
            "expected_outcome": self.expected_outcome,
            "evidence_instructions": self.evidence_instructions,
            "difficulty": self.difficulty,
            "order_index": self.order_index
        }

class LabProgress(db.Model):
    """Tracks learner execution, evidence, and self-reflection for each lab."""
    __tablename__ = "lab_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "lab_id", name="uq_user_lab"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False, index=True)
    
    status = db.Column(db.String(32), default="not_started") # 'not_started', 'in_progress', 'completed'
    evidence_text = db.Column(db.Text, nullable=True)
    reflection_text = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="lab_progresses")
    lab = db.relationship("Lab", back_populates="progresses")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "lab_id": self.lab_id,
            "status": self.status,
            "evidence_text": self.evidence_text,
            "reflection_text": self.reflection_text,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
