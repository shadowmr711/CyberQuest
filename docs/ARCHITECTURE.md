# CyberQuest Architecture & Security Documentation

## 1. Architectural Philosophy

CyberQuest is designed with a decoupled, modular architecture:
- **Presentation Layer**: HTML5 / CSS3 / Vanilla JavaScript Command Center adhering to a SOC / Terminal aesthetic. No external heavy frameworks required; blazing-fast load times, complete transparency into network calls via `fetch`.
- **Application Services Layer**: Python / Flask application factory exposing RESTful JSON APIs under `/api/`.
- **Domain & Persistence Layer**: SQLAlchemy models mapping learning trajectories, granular topic masteries, practice logs, hands-on lab workspaces, and portfolio projects. Backed by SQLite in local development and ready for seamless PostgreSQL migration.

---

## 2. Cybersecurity Controls Implemented in Phase 1

### A. Authentication vs. Authorization
* **Authentication (AuthN)**: Verifying the identity of the user. CyberQuest enforces this at `/api/auth/login` and `/api/auth/register`.
* **Authorization (AuthZ)**: Verifying what resources an authenticated identity can touch. The `@login_required` decorator validates active sessions before granting access to user profile and navigation states.

### B. Password Hashing (PBKDF2-HMAC-SHA256)
* Passwords are **never** stored in plaintext or with deprecated algorithms (like MD5, SHA-1).
* CyberQuest uses **PBKDF2** with a unique per-user cryptographically generated random salt.
* **Why this matters**: A salt prevents attackers from using precomputed rainbow tables or dictionary tables. Even if two users choose the same password, their hashes will be completely different.
* **Constant-Time Verification**: Standard string comparison (`a == b`) terminates on the first mismatch, leaking information to attackers measuring sub-millisecond network delays (timing attack). Werkzeug's `check_password_hash` uses constant-time comparison to prevent this.

### C. Session Management & Session Fixation Protection
* When an unauthenticated user transitions to an authenticated state, `session.clear()` is called before populating `session['user_id']`.
* This prevents **Session Fixation attacks**, where an attacker tricks a victim into authenticating using a pre-seeded session identifier known to the attacker.

### D. Cookie Hardening
* `HttpOnly = True`: Inaccessible to JavaScript `document.cookie`, neutralizing cookie theft via Cross-Site Scripting (XSS).
* `SameSite = 'Lax'`: Mitigates Cross-Site Request Forgery (CSRF) by preventing the cookie from being sent on cross-site requests.
* `Secure = True` (in production): Ensures cookies are only transmitted over TLS/HTTPS.

### E. HTTP Security Headers
Every HTTP response is fortified with:
* `Content-Security-Policy (CSP)`: Whitelists trusted script and style sources to prevent malicious script injection.
* `X-Frame-Options: DENY`: Blocks clickjacking attacks by preventing embedding in `<iframe>`.
* `X-Content-Type-Options: nosniff`: Prevents MIME-sniffing vulnerabilities.
* `Referrer-Policy: strict-origin-when-cross-origin`: Restricts referrer URL leakage.

---

## 3. Directory Layout

```text
CyberQuest/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory & middleware
│   │   ├── config.py            # Environment configurations
│   │   ├── models/              # SQLAlchemy schema
│   │   ├── routes/              # Blueprint endpoints
│   │   ├── services/            # Auth & Security business logic
│   │   └── utils/               # Decorators & validators
│   ├── tests/                   # Pytest test suite
│   ├── run.py                   # Dev server runner
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── css/                 # SOC styles & component cards
│   │   └── js/                  # API client, State, App controller
│   └── templates/
│       └── index.html           # Command center single-page shell
├── database/                    # SQLite storage
└── docs/
    └── ARCHITECTURE.md
```
