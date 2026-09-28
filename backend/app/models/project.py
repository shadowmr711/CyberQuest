from datetime import datetime, timezone
import json
from . import db

class Project(db.Model):
    """Capstone and portfolio projects for hands-on cybersecurity building."""
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(32), default="Foundations") # 'Foundations', 'Red Team', 'Blue Team', 'Combined'
    slug = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    milestones_json = db.Column(db.Text, nullable=True) # JSON array of milestones
    deliverables_json = db.Column(db.Text, nullable=True) # JSON array of expected portfolio outputs
    order_index = db.Column(db.Integer, default=0)

    progresses = db.relationship("ProjectProgress", back_populates="project", cascade="all, delete-orphan")

    def get_milestones(self) -> list:
        if not self.milestones_json:
            return []
        try:
            return json.loads(self.milestones_json)
        except Exception:
            return []

    def get_deliverables(self) -> list:
        if not self.deliverables_json:
            return []
        try:
            return json.loads(self.deliverables_json)
        except Exception:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "track": self.track,
            "slug": self.slug,
            "title": self.title,
            "overview": self.overview,
            "objectives": self.objectives,
            "requirements": self.requirements,
            "milestones": self.get_milestones(),
            "deliverables": self.get_deliverables(),
            "order_index": self.order_index
        }

class ProjectProgress(db.Model):
    """Stores learner workspace evidence, notes, reports, and portfolio artifact metadata."""
    __tablename__ = "project_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "project_id", name="uq_user_project"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    
    status = db.Column(db.String(32), default="not_started") # 'not_started', 'in_progress', 'completed'
    notes = db.Column(db.Text, nullable=True)
    evidence_text = db.Column(db.Text, nullable=True)
    findings_text = db.Column(db.Text, nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    report_text = db.Column(db.Text, nullable=True)
    milestones_completed_json = db.Column(db.Text, nullable=True) # JSON array of completed milestone indices
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="project_progresses")
    project = db.relationship("Project", back_populates="progresses")

    def get_completed_milestones(self) -> list:
        if not self.milestones_completed_json:
            return []
        try:
            return json.loads(self.milestones_completed_json)
        except Exception:
            return []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "status": self.status,
            "notes": self.notes or "",
            "evidence_text": self.evidence_text or "",
            "findings_text": self.findings_text or "",
            "github_url": self.github_url or "",
            "report_text": self.report_text or "",
            "completed_milestones": self.get_completed_milestones(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
