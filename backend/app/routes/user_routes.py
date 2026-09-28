from flask import Blueprint, request, jsonify, g
from ..utils.decorators import login_required, validate_json
from ..models import db, User, LearningEvent, Topic, UserTopicMastery

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """Retrieve full profile of the authenticated learner."""
    return jsonify({
        "user": g.current_user.to_dict()
    }), 200

@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """Update user experience levels or display name."""
    data = request.get_json() or {}
    user = g.current_user

    if "name" in data and len(data["name"].strip()) >= 2:
        user.name = data["name"].strip()
    if "experience_level" in data:
        user.experience_level = data["experience_level"]
    if "linux_exp" in data:
        user.linux_exp = data["linux_exp"]
    if "networking_exp" in data:
        user.networking_exp = data["networking_exp"]
    if "programming_exp" in data:
        user.programming_exp = data["programming_exp"]
    if "security_exp" in data:
        user.security_exp = data["security_exp"]
    if "preferred_path" in data and data["preferred_path"] in ["Red Team", "Blue Team", "Undecided"]:
        user.preferred_path = data["preferred_path"]

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully.",
        "user": user.to_dict()
    }), 200

@user_bp.route("/path", methods=["POST"])
@login_required
@validate_json("path")
def switch_path():
    """Switch active specialization (Foundations, Red Team, Blue Team)."""
    data = request.get_json()
    new_path = data["path"]
    
    valid_paths = ["Foundations", "Red Team", "Blue Team"]
    if new_path not in valid_paths:
        return jsonify({
            "error": f"Invalid path. Valid options are: {', '.join(valid_paths)}",
            "code": "INVALID_PATH"
        }), 400

    user = g.current_user
    old_path = user.current_path
    user.current_path = new_path

    # Log specialization switch event
    event = LearningEvent(
        user_id=user.id,
        event_type="path_switched",
        event_data=f'{{"from": "{old_path}", "to": "{new_path}"}}'
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": f"Learning specialization updated to {new_path}.",
        "current_path": user.current_path
    }), 200

@user_bp.route("/diagnostic", methods=["POST"])
@login_required
def submit_diagnostic():
    """Record diagnostic assessment completion and establish baseline topic mastery."""
    data = request.get_json() or {}
    topic_scores = data.get("scores", {}) # e.g. {"Networking": 30.0, "Linux": 15.0, ...}
    
    user = g.current_user
    user.diagnostic_completed = True

    # Record baseline topic masteries if topics exist
    for topic_name, score in topic_scores.items():
        topic = Topic.query.filter((Topic.name == topic_name) | (Topic.category == topic_name)).first()
        if topic:
            mastery_record = UserTopicMastery.query.filter_by(user_id=user.id, topic_id=topic.id).first()
            if not mastery_record:
                mastery_record = UserTopicMastery(
                    user_id=user.id,
                    topic_id=topic.id,
                    mastery=float(score),
                    confidence=50.0
                )
                db.session.add(mastery_record)
            else:
                mastery_record.mastery = float(score)

    event = LearningEvent(
        user_id=user.id,
        event_type="diagnostic_completed",
        event_data=str(topic_scores)
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({
        "message": "Initial cybersecurity diagnostic recorded.",
        "diagnostic_completed": True
    }), 200
