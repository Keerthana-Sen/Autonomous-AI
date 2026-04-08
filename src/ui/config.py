# ── XFLOW Configuration ───────────────────────────────────────────────────────

APP_NAME = "XFLOW"
APP_SUBTITLE = "Explainable Workflow Decisions"
APP_ICON = "⚙️"

API_BASE = "http://localhost:8000/api"
API_TIMEOUT = 60  # seconds

SAMPLE_QUESTIONS = [
    "Why was REQ001 approved?",
    "Why was REQ002 escalated?",
    "Why was REQ004 rejected?",
    "Why was REQ007 escalated?",
    "What happens when a request exceeds 10000 USD?",
    "Under what condition is a request auto-approved?",
]