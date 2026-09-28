from flask import Blueprint, jsonify, g
from ..utils.decorators import login_required
from ..models import UserTopicMastery, LessonProgress, LabProgress, ProjectProgress, Project, Module

nav_bp = Blueprint("navigation", __name__, url_prefix="/api/navigation")

@nav_bp.route("/state", methods=["GET"])
@login_required
def get_navigation_state():
    """
    Returns current learning status snapshot for Dashboard:
    Where am I? What should I learn next? What am I weak at? What have I practiced? What am I building?
    """
    user = g.current_user
    
    # 1. Masteries breakdown (Weak < 40%, Medium 40-70%, Strong >= 70%)
    masteries = UserTopicMastery.query.filter_by(user_id=user.id).all()
    weak_topics = []
    medium_topics = []
    strong_topics = []

    for m in masteries:
        topic_info = {
            "topic_id": m.topic_id,
            "name": m.topic.name if m.topic else "Unknown Topic",
            "category": m.topic.category if m.topic else "General",
            "mastery": round(m.mastery, 1),
            "practice_accuracy": round(m.practice_accuracy, 1),
            "mistake_count": m.mistake_count
        }
        if m.mastery < 40.0:
            weak_topics.append(topic_info)
        elif m.mastery < 70.0:
            medium_topics.append(topic_info)
        else:
            strong_topics.append(topic_info)

    # 2. Overall Lesson Progress
    completed_lessons_count = LessonProgress.query.filter_by(user_id=user.id, completed=True).count()
    
    # 3. Recent Labs
    recent_labs = LabProgress.query.filter_by(user_id=user.id).order_by(LabProgress.updated_at.desc()).limit(3).all()
    
    # 4. Active Project
    active_project_progress = ProjectProgress.query.filter_by(user_id=user.id).first()
    active_project_data = None
    if active_project_progress and active_project_progress.project:
        active_project_data = {
            "project_id": active_project_progress.project.id,
            "title": active_project_progress.project.title,
            "track": active_project_progress.project.track,
            "status": active_project_progress.status,
            "completed_milestones": len(active_project_progress.get_completed_milestones()),
            "total_milestones": len(active_project_progress.project.get_milestones())
        }
    
    return jsonify({
        "current_path": user.current_path,
        "diagnostic_completed": user.diagnostic_completed,
        "completed_lessons_count": completed_lessons_count,
        "weak_topics": weak_topics,
        "medium_topics": medium_topics,
        "strong_topics": strong_topics,
        "recent_labs": [lab_p.to_dict() for lab_p in recent_labs],
        "active_project": active_project_data
    }), 200
