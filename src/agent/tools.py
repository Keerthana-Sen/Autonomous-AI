import sys
import os
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.retrieval.retriever import get_retriever

# ── Load transactions ─────────────────────────────────────────────────────────
def load_transactions():
    """Load transactions from CSV into a dict keyed by request_id."""
    transactions = {}
    csv_path = "data/transactions.csv"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions[row["Request_id"]] = row
    return transactions

TRANSACTIONS = load_transactions()

POLICIES = {
    "auto_approval_limit": 1000,
    "manager_approval_limit": 5000,
    "duplicate_window_days": 30,
    "required_approvers": ["Bob", "Sarah", "John"],
}

REJECTION_REASONS = [
    "Account is suspended",
    "Incomplete documentation",
    "Duplicate request within 30 days",
    "Missing required approvals",
]


# ── Tool functions ────────────────────────────────────────────────────────────
def lookup_policy(policy_name: str) -> dict:
    """Lookup a specific policy rule by name."""
    if policy_name in POLICIES:
        return {
            "policy": policy_name,
            "value": POLICIES[policy_name],
            "description": f"Policy rule: {policy_name} = {POLICIES[policy_name]}"
        }
    return {
        "policy": policy_name,
        "value": None,
        "description": f"Policy '{policy_name}' not found. Available: {list(POLICIES.keys())}"
    }


def check_transaction(request_id: str) -> dict:
    """Check details of a specific transaction/request by ID."""
    if request_id in TRANSACTIONS:
        return {
            "request_id": request_id,
            "status": "found",
            "details": TRANSACTIONS[request_id]
        }
    return {
        "request_id": request_id,
        "status": "not_found",
        "details": None
    }


def retrieve_policy_context(query: str) -> str:
    """
    FIX 2: RAG retriever exposed as a tool.
    Agent now queries ChromaDB during reasoning — not just for RAGAS collection.
    This grounds answers in actual policy documents → fixes Faithfulness + Context scores.
    """
    retriever = get_retriever(k=3)
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant policy context found."

    # Join chunks into a single readable string for the LLM
    return "\n\n".join([doc.page_content for doc in docs])


# ── Tool registry ─────────────────────────────────────────────────────────────
TOOLS = [lookup_policy, check_transaction, retrieve_policy_context]