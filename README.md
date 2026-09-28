# CyberQuest — Cybersecurity Training & Adaptive Learning Platform

CyberQuest is an independent, adaptive cybersecurity learning platform and portfolio environment designed for serious security education.

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+ (tested with Python 3.14)
- Virtual environment (`venv`)

### 2. Activate Virtual Environment
On Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Run the Backend & Command Center
```powershell
python backend/run.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

### 4. Run Automated Test Suite
```powershell
pytest backend/tests -v
```

---

## Phase 1 Capabilities Implemented
- **SOC Command Center Dashboard**: Real-time state overview, adaptive recommendation card, topic mastery cards.
- **Main Navigation**: Dashboard, Learning Path, Practice Lab, Labs, Analytics, Projects, Profile.
- **Secure Authentication & Onboarding**: Salted PBKDF2 password hashing, session fixation prevention, HttpOnly/SameSite session cookies, rate-limiting tracker, and security headers (CSP, X-Frame-Options, X-Content-Type-Options).
- **Initial Diagnostic Assessment**: Multi-topic diagnostic assessment (Networking, Linux, Windows, Web, Cryptography, Security Fundamentals, Auth, OS) establishing baseline topic masteries.
- **Flexible Specialization Switcher**: Smoothly transition between Foundations, Red Team, and Blue Team.
- **Database Schema**: Full relational model for curriculum, masteries, practice questions/attempts, labs, and portfolio projects.
