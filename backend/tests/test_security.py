def test_security_headers_present(client):
    """Verify security headers are applied to HTTP responses."""
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'self'" in res.headers.get("Content-Security-Policy", "")
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

def test_session_cookie_flags(client):
    """Verify session cookie configuration protects against script access."""
    res = client.post("/api/auth/register", json={
        "username": "cookie_tester",
        "email": "cookie@cyberquest.org",
        "password": "Password1234!",
        "name": "Cookie Cadet"
    })
    assert res.status_code == 201
    cookie_header = res.headers.get("Set-Cookie", "")
    # In Flask, session cookie contains HttpOnly and SameSite=Lax
    assert "HttpOnly" in cookie_header
    assert "SameSite=Lax" in cookie_header
