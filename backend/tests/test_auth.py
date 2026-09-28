import json

def test_register_success(client):
    """Learners can register with valid credentials."""
    res = client.post("/api/auth/register", json={
        "username": "cadet_cyber",
        "email": "cadet@cyberquest.org",
        "password": "CorrectHorseBatteryStaple!2026",
        "name": "Jordan Lee",
        "experience_level": "Beginner",
        "preferred_path": "Blue Team"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["username"] == "cadet_cyber"
    assert data["user"]["current_path"] == "Foundations"
    assert "password_hash" not in data["user"]

def test_register_duplicate_username(client, sample_user):
    """System rejects registration with existing username."""
    res = client.post("/api/auth/register", json={
        "username": "analyst_zero",
        "email": "different@cyberquest.org",
        "password": "Password1234!",
        "name": "Clone User"
    })
    assert res.status_code == 400
    assert "already registered" in res.get_json()["error"]

def test_register_short_password(client):
    """System rejects passwords under 8 characters."""
    res = client.post("/api/auth/register", json={
        "username": "shortpass",
        "email": "short@cyberquest.org",
        "password": "abc",
        "name": "Short Pass User"
    })
    assert res.status_code == 400
    assert "at least 8 characters" in res.get_json()["error"]

def test_login_success(client, sample_user):
    """Authentication succeeds with valid password and sets session."""
    res = client.post("/api/auth/login", json={
        "username_or_email": "analyst_zero",
        "password": "SecureP@ssw0rd!2026"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["username"] == "analyst_zero"

    # Verify session is established by querying /api/auth/me
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["authenticated"] is True
    assert me_res.get_json()["user"]["username"] == "analyst_zero"

def test_login_invalid_password(client, sample_user):
    """Authentication fails with wrong password."""
    res = client.post("/api/auth/login", json={
        "username_or_email": "analyst_zero",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    assert "Invalid username/email or password" in res.get_json()["error"]

def test_protected_route_requires_auth(client):
    """Unauthenticated requests to protected endpoints return 401."""
    res = client.get("/api/user/profile")
    assert res.status_code == 401
    assert res.get_json()["code"] == "UNAUTHORIZED"

def test_logout(client, sample_user):
    """Logging out destroys the session."""
    client.post("/api/auth/login", json={
        "username_or_email": "analyst_zero",
        "password": "SecureP@ssw0rd!2026"
    })
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    me_res = client.get("/api/auth/me")
    assert me_res.get_json()["authenticated"] is False
