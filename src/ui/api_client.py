import requests
from src.ui.config import API_BASE, API_TIMEOUT


def query_rag(question: str) -> dict:
    """Sends question to baseline RAG endpoint."""
    return _post("rag", question)


def query_agent(question: str) -> dict:
    """Sends question to autonomous agent endpoint."""
    return _post("agent", question)


def inject_transaction(transaction: dict) -> dict:
    """Injects a transaction into the API's live TRANSACTIONS dict."""
    try:
        r = requests.post(f"{API_BASE}/inject_transaction", json=transaction, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def check_health() -> bool:
    """Returns True if FastAPI server is reachable."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def _post(endpoint: str, question: str) -> dict:
    """Internal helper — posts to API and handles errors cleanly."""
    try:
        response = requests.post(
            f"{API_BASE}/{endpoint}",
            json={"question": question},
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Is the FastAPI server running on port 8000?"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The agent may be taking too long — try again."}
    except Exception as e:
        return {"error": str(e)}