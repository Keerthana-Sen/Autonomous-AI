# ── XFLOW Configuration ───────────────────────────────────────────────────────

APP_NAME = "XFLOW"
APP_SUBTITLE = "Explainable Workflow Decisions"
APP_ICON = "⚙️"

API_BASE = "http://localhost:8000/api"
API_TIMEOUT = 120  # seconds

SAMPLE_QUESTIONS = [
    "Why was REQ003 escalated instead of rejected, given that the documentation is incomplete?",
    "What specific combination of factors caused REQ007 to receive a permanent rejection flag?",
    "Why was REQ005 approved despite being a duplicate request submitted within 30 days?",
    "Why was REQ008 escalated directly to the director level rather than following the standard escalation chain?",
    "Why was REQ009 rejected rather than sent for senior manager approval, despite having complete documentation?",
    "Why was REQ020 escalated with fast-track processing, and which policies contributed to this outcome?",
]

TRANSACTIONS_DATA = {
    "REQ001": {"requester": "John", "amount": "400", "request_type": "software_license", "priority": "low", "approver": "Bob", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "approved"},
    "REQ002": {"requester": "Priya", "amount": "12000", "request_type": "hardware", "priority": "medium", "approver": "Sarah", "approver_status": "unavailable", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "suspended", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ003": {"requester": "Ann", "amount": "3500", "request_type": "infrastructure", "priority": "critical", "approver": "John", "approver_status": "unavailable", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ004": {"requester": "Neha", "amount": "800", "request_type": "training", "priority": "low", "approver": "Bob", "approver_status": "available", "documentation_complete": "FALSE", "duplicate": "TRUE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "incomplete_documentation", "decision": "rejected"},
    "REQ005": {"requester": "David", "amount": "700", "request_type": "training", "priority": "medium", "approver": "Sarah", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "TRUE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "budget_exceeded", "decision": "approved"},
    "REQ006": {"requester": "Ewin", "amount": "15000", "request_type": "hardware", "priority": "medium", "approver": "Sarah", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ007": {"requester": "Jefin", "amount": "2000", "request_type": "infrastructure", "priority": "high", "approver": "Bob", "approver_status": "available", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "suspended", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ008": {"requester": "Kriss", "amount": "11000", "request_type": "travel", "priority": "high", "approver": "John", "approver_status": "unavailable", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ009": {"requester": "Janet", "amount": "8000", "request_type": "training", "priority": "high", "approver": "Bob", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ010": {"requester": "Emma", "amount": "4000", "request_type": "hardware", "priority": "medium", "approver": "Sarah", "approver_status": "unavailable", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "5", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ011": {"requester": "Anna", "amount": "9000", "request_type": "software_license", "priority": "medium", "approver": "John", "approver_status": "available", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ012": {"requester": "Marcus", "amount": "7000", "request_type": "infrastructure", "priority": "high", "approver": "Bob", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ013": {"requester": "Lily", "amount": "750", "request_type": "training", "priority": "low", "approver": "Sarah", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "under_review", "employee_level": "3", "previous_rejection_reason": "none", "decision": "approved"},
    "REQ014": {"requester": "Tom", "amount": "4500", "request_type": "infrastructure", "priority": "critical", "approver": "John", "approver_status": "available", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ015": {"requester": "Zara", "amount": "3500", "request_type": "travel", "priority": "high", "approver": "Bob", "approver_status": "unavailable", "documentation_complete": "FALSE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "rejected"},
    "REQ016": {"requester": "Felix", "amount": "2500", "request_type": "hardware", "priority": "high", "approver": "Sarah", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "TRUE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "suspended_account", "decision": "approved"},
    "REQ017": {"requester": "Nina", "amount": "6500", "request_type": "infrastructure", "priority": "medium", "approver": "John", "approver_status": "unavailable", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "escalated"},
    "REQ018": {"requester": "Oscar", "amount": "450", "request_type": "software_license", "priority": "low", "approver": "Bob", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "under_review", "employee_level": "3", "previous_rejection_reason": "none", "decision": "approved"},
    "REQ019": {"requester": "Paula", "amount": "2000", "request_type": "travel", "priority": "high", "approver": "Sarah", "approver_status": "available", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "3", "previous_rejection_reason": "none", "decision": "approved"},
    "REQ020": {"requester": "Quinn", "amount": "4800", "request_type": "infrastructure", "priority": "critical", "approver": "John", "approver_status": "unavailable", "documentation_complete": "TRUE", "duplicate": "FALSE", "account_status": "active", "employee_level": "5", "previous_rejection_reason": "none", "decision": "escalated"},
}

REQ_IDS = list(TRANSACTIONS_DATA.keys())