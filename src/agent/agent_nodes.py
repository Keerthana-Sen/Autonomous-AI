import json
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage

from src.baseline_rag.llm import get_agent_llm
from src.retrieval.retriever import get_retrieval_confidence
from src.agent.agent_state import AgentState
from src.agent.agent_prompts import SYSTEM_PROMPT
from src.agent.agent_utils import extract_clean_answer
from src.agent.tools import check_transaction, retrieve_policy_context

import re


def _extract_request_id(question: str) -> str | None:
    """Pulls REQ/REQCUSTOM IDs from the question. Normalizes standard IDs to 3-digit zero-padded form."""
    match = re.search(r"\b(REQCUSTOM\d+)\b", question, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    match = re.search(r"\bREQ(\d+)\b", question, re.IGNORECASE)
    if not match:
        return None
    return f"REQ{int(match.group(1)):03d}"


def _compute_approval_tier(tx: dict) -> str:
    """Returns the correct approval tier using Python arithmetic — prevents LLM numerical errors."""
    try:
        amount = float(str(tx.get("amount", "0")).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return "tier unknown"
    req_type = tx.get("request_type", "").lower().replace(" ", "_")
    priority = tx.get("priority", "").lower()
    docs_complete = str(tx.get("documentation_complete", "TRUE")).upper() == "TRUE"
    account_status = tx.get("account_status", "active").lower()
    is_duplicate = str(tx.get("duplicate", "FALSE")).upper() == "TRUE"

    # Budget caps — always reject, checked first
    if req_type == "training" and amount > 5000:
        return f"BUDGET CAP EXCEEDED — ${amount:.0f} exceeds training max of $5000 (Approval Policy S3 R9) — reject"
    if req_type == "travel" and amount > 8000:
        return f"BUDGET CAP EXCEEDED — ${amount:.0f} exceeds travel max of $8000 (Approval Policy S3 R10) — reject"

    # Critical-priority infrastructure exception: overrides rejection → escalate with waiver
    if req_type == "infrastructure" and priority == "critical":
        if not docs_complete or account_status == "suspended" or is_duplicate:
            return (
                f"escalation via critical-priority infrastructure exception (Rejection Policy S3 R8) — "
                f"rejection conditions are present but overridden; request is escalated with waiver instead of rejected"
            )

    # Rejection conditions
    if account_status == "suspended":
        return f"rejected — suspended account status"
    if not docs_complete:
        return f"rejected — incomplete documentation"
    if is_duplicate:
        return f"rejected — duplicate request"

    # Approval tiers by amount
    if req_type in ("software_license", "training") and amount < 1000:
        return f"auto-approve eligible — ${amount:.0f} is under $1000 (Approval Policy S1 R1)"
    if req_type not in ("software_license", "training") and amount < 500:
        return f"auto-approve eligible — ${amount:.0f} is under $500 (Approval Policy S1 R2)"
    if amount < 5000:
        return f"manager approval — ${amount:.0f} is in the $1000–$4999 range (Approval Policy S1 R3)"
    if amount <= 10000:
        return f"senior manager + finance approval — ${amount:.0f} is in the $5000–$10000 range (Approval Policy S1 R4)"
    return f"director escalation — ${amount:.0f} exceeds $10000 (Approval Policy S1 R5)"


def reasoning_node(state: AgentState) -> Command:
    """
    Structured 3-step agent — works reliably with 8b models.
    Instead of asking the LLM to pick tools freely (which confuses small models),
    we always run the same fixed sequence:
      Step 1: fetch transaction details if a REQ ID is present
      Step 2: fetch relevant policy context from ChromaDB
      Step 3: generate final answer with all context in hand
    This removes the tool-selection burden from the 8b model entirely.
    """
    llm = get_agent_llm()
    question = state["question"]
    iterations = state.get("iterations", 0) + 1

    print(f"\n[REASONING] Iteration {iterations} — {question[:60]}...")

    if iterations > 3:  # 3 steps max — no open loop needed
        return Command(
            goto="end_node",
            update={
                "final_answer": "Unable to determine answer.",
                "iterations": iterations
            }
        )

    # ── Step 1: Fetch transaction if REQ ID found in question ────────────────
    transaction_context = ""
    req_id = _extract_request_id(question)
    if req_id:
        print(f"  [Step 1] Fetching transaction: {req_id}")
        tx_result = check_transaction(req_id)
        if tx_result["status"] == "found":
            details = {k: v for k, v in tx_result["details"].items() if k.lower() != "decision"}
            tier = _compute_approval_tier(tx_result["details"])
            transaction_context = (
                f"Transaction details:\n{json.dumps(details, indent=2)}\n\n"
                f"Computed approval tier (Python-verified): {tier}"
            )
            actual_decision = tx_result["details"].get("decision", "").lower()
            # Only fire mismatch if exactly one decision keyword appears in the
            # question — multiple keywords means a comparison/reasoning question
            # (e.g. "escalated instead of rejected"), not a false assumption.
            keywords_in_q = [k for k in ["rejected", "approved", "escalated"] if k in question.lower()]
            if len(keywords_in_q) == 1:
                keyword = keywords_in_q[0]
                if actual_decision and keyword not in actual_decision:
                    transaction_context += (
                        f"\n\nNOTE: The question assumes this request was {keyword}, "
                        f"but the transaction record shows the actual decision was '{actual_decision}'. "
                        f"Correct the user's assumption in your answer."
                    )
            print(f"  ✓ Found transaction")
        else:
            transaction_context = f"Transaction {req_id} not found."
            print(f"  ✗ Transaction not found")

    # ── Step 2: Fetch policy context from ChromaDB ───────────────────────────
    # Enrich the retrieval query with transaction attributes so type-specific
    # budget caps and rules (e.g. training cap, infrastructure rules) are found.
    print(f"  [Step 2] Retrieving policy context...")
    retrieval_query = question
    if req_id and tx_result.get("status") == "found":
        d = tx_result["details"]
        extras = []
        if d.get("request_type"):
            extras.append(f"request type: {d['request_type']}")
        if d.get("amount"):
            extras.append(f"amount: {d['amount']} USD")
        if d.get("priority"):
            extras.append(f"priority: {d['priority']}")
        if d.get("account_status"):
            extras.append(f"account status: {d['account_status']}")
        if extras:
            retrieval_query = f"{question}\nTransaction attributes: {', '.join(extras)}"
    policy_context = retrieve_policy_context(retrieval_query)
    confidence = get_retrieval_confidence(retrieval_query)
    print(f"  ✓ Policy context retrieved ({len(policy_context)} chars), confidence={confidence}")

    # ── Step 3: Build prompt and generate answer ─────────────────────────────
    print(f"  [Step 3] Generating answer...")

    # Combine all gathered context into one clean prompt
    full_context = ""
    if transaction_context:
        full_context += f"{transaction_context}\n\n"
    full_context += f"Policy context:\n{policy_context}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Context:\n{full_context}\n\n"
            f"Question: {question}\n\n"
            f"Write a direct explanation in 3 to 5 sentences. "
            f"Start immediately with the decision outcome — do NOT say 'I will', 'Based on the process', or narrate your steps. "
            f"Cite each applicable policy section and rule number. "
            f"Reference the exact transaction values that triggered each rule."
        ))
    ]

    max_retries = 4
    response = None
    for attempt in range(max_retries):
        try:
            response = llm.invoke(messages)
            break
        except Exception as e:
            err_str = str(e)
            if "rate_limit" in err_str.lower() or "rate limit" in err_str.lower():
                if attempt < max_retries - 1:
                    m = re.search(r"try again in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
                    wait = float(m.group(1)) + 2 if m else 60
                    print(f"  ⚠ Rate limited — waiting {wait:.0f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                return Command(
                    goto="end_node",
                    update={"final_answer": "Rate limit reached after retries.", "iterations": iterations}
                )
            raise

    raw_content = ""
    if hasattr(response, "content") and response.content:
        raw_content = response.content
    elif hasattr(response, "additional_kwargs"):
        raw_content = response.additional_kwargs.get("reasoning_content", "")
    if not raw_content:
        raw_content = str(response)
    clean = extract_clean_answer(raw_content)
    print(f"  ✓ Answer ready")

    return Command(
        goto="end_node",
        update={
            "final_answer": clean,
            "iterations": iterations,
            "retrieval_confidence": confidence
        }
    )


def end_node(state: AgentState) -> dict:
    """Returns the final answer."""
    return {"final_answer": state.get("final_answer", "")}