from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .curriculum import LearningPath, Module, Lesson, Topic
from .progress import UserTopicMastery, LessonProgress, StudySession, LearningEvent
from .practice import PracticeQuestion, PracticeAttempt
from .lab import Lab, LabProgress
from .project import Project, ProjectProgress

__all__ = [
    "db",
    "User",
    "LearningPath",
    "Module",
    "Lesson",
    "Topic",
    "UserTopicMastery",
    "LessonProgress",
    "StudySession",
    "LearningEvent",
    "PracticeQuestion",
    "PracticeAttempt",
    "Lab",
    "LabProgress",
    "Project",
    "ProjectProgress"
]
