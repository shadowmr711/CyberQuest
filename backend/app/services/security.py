import time
from collections import defaultdict
from flask import Response

"""
CYBERSECURITY CONCEPT: Defense in Depth & HTTP Security Headers
==============================================================
HTTP headers are instructions sent by the server telling the client browser
how to safely interpret and handle responses.

1. Content-Security-Policy (CSP): Restricts origins from which scripts, styles,
   and media can be loaded. This is the primary defense against Cross-Site Scripting (XSS).
2. X-Frame-Options: Prevents the page from being embedded inside an <iframe>,
   neutralizing Clickjacking (UI redressing) attacks.
3. X-Content-Type-Options: Blocks the browser from 'MIME-sniffing' an untrusted file
   as executable script when declared as plain text/image.
4. Referrer-Policy: Prevents sensitive URLs and parameters from leaking to external sites.
"""

# Simple in-memory sliding window rate tracker for brute-force protection
# Key: client_ip, Value: list of attempt timestamps
_login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 10
ATTEMPT_WINDOW_SECONDS = 300  # 5 minutes

def is_rate_limited(ip_address: str) -> bool:
    """Check if an IP address has exceeded the failed login threshold."""
    now = time.time()
    # Filter attempts within the active time window
    recent_attempts = [t for t in _login_attempts[ip_address] if now - t < ATTEMPT_WINDOW_SECONDS]
    _login_attempts[ip_address] = recent_attempts
    return len(recent_attempts) >= MAX_LOGIN_ATTEMPTS

def record_failed_attempt(ip_address: str) -> None:
    """Record a failed login attempt for rate limiting."""
    _login_attempts[ip_address].append(time.time())

def clear_attempts(ip_address: str) -> None:
    """Clear failed attempts upon successful authentication."""
    if ip_address in _login_attempts:
        del _login_attempts[ip_address]

def apply_security_headers(response: Response) -> Response:
    """Applies secure HTTP headers to every outgoing HTTP response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    return response
