import pytest
import sys
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app import create_app
from app.models import db, User

@pytest.fixture
def app():
    """Create test application instance using in-memory database."""
    app_instance = create_app("testing")
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test HTTP client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI test runner."""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Creates and returns a sample learner user."""
    with app.app_context():
        user = User(
            username="analyst_zero",
            email="analyst@cyberquest.local",
            name="Alex Turner",
            experience_level="Beginner",
            linux_exp="Beginner",
            networking_exp="Beginner",
            programming_exp="Some experience",
            security_exp="None",
            preferred_path="Red Team",
            current_path="Foundations"
        )
        user.set_password("SecureP@ssw0rd!2026")
        db.session.add(user)
        db.session.commit()
        return user
