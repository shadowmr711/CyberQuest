from datetime import datetime, timezone
import json
from . import db

class PracticeQuestion(db.Model):
    """Practice questions: knowledge, scenario, command, investigation, decision."""
    __tablename__ = "practice_questions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False, index=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=True, index=True)
    
    question_type = db.Column(db.String(32), nullable=False) # 'knowledge', 'scenario', 'command', 'investigation', 'decision'
    question_text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=True) # JSON array of options
    correct_answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default="medium") # 'easy', 'medium', 'hard'
    hint = db.Column(db.Text, nullable=True)

    topic = db.relationship("Topic", back_populates="practice_questions")
    lesson = db.relationship("Lesson", back_populates="practice_questions")
    attempts = db.relationship("PracticeAttempt", back_populates="question", cascade="all, delete-orphan")

    def get_options(self) -> list:
        if not self.options_json:
            return []
        try:
            return json.loads(self.options_json)
        except Exception:
            return []

    def to_dict(self, include_answer: bool = False) -> dict:
        data = {
            "id": self.id,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "lesson_id": self.lesson_id,
            "question_type": self.question_type,
            "question_text": self.question_text,
            "options": self.get_options(),
            "difficulty": self.difficulty,
            "hint": self.hint
        }
        if include_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"] = self.explanation
        return data

class PracticeAttempt(db.Model):
    """Records each practice attempt to feed mistake tracking and mastery calculation."""
    __tablename__ = "practice_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("practice_questions.id"), nullable=False, index=True)
    user_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    attempt_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="practice_attempts")
    question = db.relationship("PracticeQuestion", back_populates="attempts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question_id": self.question_id,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "attempt_number": self.attempt_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
