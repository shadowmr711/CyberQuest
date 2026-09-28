from app.models import db, User, LearningPath, Module, Topic, Lesson, UserTopicMastery

def test_user_and_mastery_relationship(app, sample_user):
    """Verify relationships between user and topic mastery records."""
    with app.app_context():
        user = User.query.filter_by(username="analyst_zero").first()
        
        path = LearningPath(slug="foundations", name="Foundations", description="Cyber Fundamentals")
        db.session.add(path)
        db.session.commit()

        mod = Module(learning_path_id=path.id, slug="networking", title="Networking", description="Computer Networks")
        db.session.add(mod)
        db.session.commit()

        topic = Topic(module_id=mod.id, slug="tcp-handshake", name="TCP Handshake", category="Networking")
        db.session.add(topic)
        db.session.commit()

        mastery = UserTopicMastery(
            user_id=user.id,
            topic_id=topic.id,
            mastery=65.5,
            practice_accuracy=60.0,
            mistake_count=3
        )
        db.session.add(mastery)
        db.session.commit()

        assert len(user.topic_masteries) == 1
        assert user.topic_masteries[0].topic.name == "TCP Handshake"
        assert user.topic_masteries[0].mastery == 65.5
