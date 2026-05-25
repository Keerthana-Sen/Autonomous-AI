# ── XFLOW Configuration ───────────────────────────────────────────────────────

APP_NAME = "XFLOW"
APP_SUBTITLE = "Explainable Workflow Decisions"
APP_ICON = "⚙️"

API_BASE = "http://localhost:8000/api"
API_TIMEOUT = 60  # seconds

SAMPLE_QUESTIONS = [
    "Why was REQ003 escalated instead of rejected, given that the documentation is incomplete?",
    "What specific combination of factors caused REQ007 to receive a permanent rejection flag?",
    "Why was REQ005 approved despite being a duplicate request submitted within 30 days?",
    "Why was REQ008 escalated directly to the director level rather than following the standard escalation chain?",
    "Why was REQ009 rejected rather than sent for senior manager approval, despite having complete documentation?",
    "Why was REQ020 escalated with fast-track processing, and which policies contributed to this outcome?",
]