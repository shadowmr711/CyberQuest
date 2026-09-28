from . import db

class LearningPath(db.Model):
    """Major learning tracks: Foundations, Red Team, Blue Team."""
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, default=0)

    modules = db.relationship("Module", back_populates="learning_path", cascade="all, delete-orphan", order_by="Module.order_index")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "order_index": self.order_index,
            "module_count": len(self.modules)
        }

class Module(db.Model):
    """Educational modules (e.g. Computer Fundamentals, Networking, Linux, OWASP, SIEM)."""
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, default=0)

    learning_path = db.relationship("LearningPath", back_populates="modules")
    topics = db.relationship("Topic", back_populates="module", cascade="all, delete-orphan")
    lessons = db.relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learning_path_id": self.learning_path_id,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "order_index": self.order_index,
            "lesson_count": len(self.lessons),
            "topic_count": len(self.topics)
        }

class Topic(db.Model):
    """Granular topic for mastery tracking (e.g., DNS, TCP Handshake, Linux Permissions, SQL Injection)."""
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    slug = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, index=True)

    module = db.relationship("Module", back_populates="topics")
    lessons = db.relationship("Lesson", back_populates="topic")
    masteries = db.relationship("UserTopicMastery", back_populates="topic", cascade="all, delete-orphan")
    practice_questions = db.relationship("PracticeQuestion", back_populates="topic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "module_id": self.module_id,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "category": self.category
        }

class Lesson(db.Model):
    """Detailed lesson containing structured pedagogical breakdown."""
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    
    # 8-part pedagogical content structure required by CyberQuest
    concept = db.Column(db.Text, nullable=False)
    explanation_simple = db.Column(db.Text, nullable=False)
    explanation_technical = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=False)
    why_it_matters = db.Column(db.Text, nullable=False)
    common_mistakes = db.Column(db.Text, nullable=False)
    practical_task = db.Column(db.Text, nullable=False)
    
    difficulty = db.Column(db.String(20), default="Beginner")
    order_index = db.Column(db.Integer, default=0)
    prerequisite_lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=True)

    module = db.relationship("Module", back_populates="lessons")
    topic = db.relationship("Topic", back_populates="lessons")
    progresses = db.relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    practice_questions = db.relationship("PracticeQuestion", back_populates="lesson")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "module_id": self.module_id,
            "topic_id": self.topic_id,
            "topic_name": self.topic.name if self.topic else None,
            "slug": self.slug,
            "title": self.title,
            "concept": self.concept,
            "explanation_simple": self.explanation_simple,
            "explanation_technical": self.explanation_technical,
            "example": self.example,
            "why_it_matters": self.why_it_matters,
            "common_mistakes": self.common_mistakes,
            "practical_task": self.practical_task,
            "difficulty": self.difficulty,
            "order_index": self.order_index,
            "prerequisite_lesson_id": self.prerequisite_lesson_id
        }
