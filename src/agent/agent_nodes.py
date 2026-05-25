import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from langgraph.types import Command
from langchain_core.messages import HumanMessage, SystemMessage

from src.baseline_rag.llm import get_llm
from src.baseline_rag.llm import get_agent_llm
from src.agent.agent_state import AgentState
from src.agent.agent_prompts import SYSTEM_PROMPT
from src.agent.agent_utils import extract_clean_answer
from src.agent.tools import check_transaction, retrieve_policy_context, lookup_policy

import re


def _extract_request_id(question: str) -> str | None:
    """Pulls REQ001-style IDs from the question string."""
    match = re.search(r"REQ\d+", question, re.IGNORECASE)
    return match.group(0).upper() if match else None


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
            transaction_context = f"Transaction details:\n{json.dumps(details, indent=2)}"
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
    print(f"  ✓ Policy context retrieved ({len(policy_context)} chars)")

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
            f"Using ONLY the information explicitly stated in the context above, explain the decision. "
            f"Cite the specific policy section and rule number for each reason. "
            f"Do not introduce any amounts, conditions, or rules that do not appear verbatim in the context."
        ))
    ]

    try:
        response = llm.invoke(messages)  # plain invoke — no tools bound
    except Exception as e:
        if "rate_limit" in str(e).lower():
            return Command(
                goto="end_node",
                update={"final_answer": "Rate limit reached.", "iterations": iterations}
            )
        raise

    clean = extract_clean_answer(
        response.content if hasattr(response, "content") else str(response)
    )
    print(f"  ✓ Answer ready")

    return Command(
        goto="end_node",
        update={
            "final_answer": clean,
            "iterations": iterations
        }
    )


def tool_execution_node(state: AgentState) -> Command:
    """Not used in structured mode — kept for graph compatibility."""
    return Command(goto="reasoning_node", update={})


def end_node(state: AgentState) -> dict:
    """Returns the final answer."""
    return {"final_answer": state.get("final_answer", "")}