import re
import streamlit as st
from src.ui.config import SAMPLE_QUESTIONS, APP_NAME, APP_SUBTITLE, APP_ICON
from src.ui.api_client import check_health, query_rag, query_agent


def render_header():
    """Renders the XFLOW header and API status indicator."""
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_SUBTITLE}",
        page_icon=APP_ICON,
        layout="wide"
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        st.title(f"{APP_ICON} {APP_NAME} — {APP_SUBTITLE}")
        st.caption(
            "Compare a Baseline RAG pipeline against a LangGraph Autonomous Agent "
            "for explaining enterprise workflow approval decisions."
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if check_health():
            st.success("API Online")
        else:
            st.error("API Offline")


def render_sidebar() -> str:
    """
    Renders sidebar with project info and sample questions.
    Returns the selected question label.
    """
    st.sidebar.title(f"{APP_ICON} {APP_NAME}")
    st.sidebar.caption("Explainable Workflow Decisions")
    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "**How it works**\n\n"
        "1. Select a sample question or type your own\n"
        "2. The system looks up the transaction record\n"
        "3. Policy rules are retrieved and applied\n"
        "4. The agent explains the decision with citations"
    )
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sample Questions")

    selected = st.sidebar.radio(
        "Pick one or type your own below:",
        ["Custom"] + SAMPLE_QUESTIONS
    )

    return selected


def render_question_input(selected: str, key: str = "question_input") -> str:
    """Renders the question text input. Pre-fills if a sample is selected."""
    if selected == "Custom":
        return st.text_input(
            "Ask a question about a workflow decision:",
            placeholder="e.g. Why was REQ003 escalated instead of rejected?",
            key=key
        )
    return st.text_input(
        "Ask a question about a workflow decision:",
        value=selected,
        key=key
    )


def _detect_decision(text: str) -> str:
    """
    Detect the actual decision from answer text.
    Uses 'was X' patterns first so answers like 'escalated instead of rejected'
    correctly resolve to 'escalated' rather than 'rejected'.
    """
    lower = text.lower()
    for pattern, decision in [
        (r"\bwas escalated\b", "escalated"),
        (r"\bwas approved\b", "approved"),
        (r"\bwas rejected\b", "rejected"),
    ]:
        if re.search(pattern, lower):
            return decision
    if "escalated" in lower:
        return "escalated"
    if "approved" in lower:
        return "approved"
    if "rejected" in lower:
        return "rejected"
    return "unknown"


def _decision_color(answer: str):
    """Returns the appropriate st alert function based on decision keyword."""
    decision = _detect_decision(answer)
    if decision == "rejected":
        return st.error
    if decision == "escalated":
        return st.info
    return st.success


def _badge_html(text: str) -> str:
    """Returns an HTML badge for the given answer or decision string."""
    decision = _detect_decision(text)
    badges = {
        "approved":  ("badge-approved",  "APPROVED"),
        "rejected":  ("badge-rejected",  "REJECTED"),
        "escalated": ("badge-escalated", "ESCALATED"),
    }
    cls, label = badges.get(decision, ("badge-unknown", "UNKNOWN"))
    return f'<span class="badge {cls}">{label}</span>'


def render_transaction_card(req_id: str, tx: dict):
    """Renders a styled card showing transaction details and decision badge."""
    decision = tx.get("decision", "")
    badge = _badge_html(decision)
    docs = tx.get("documentation_complete", "").upper()
    dup = tx.get("duplicate", "").upper()

    st.markdown(f"""
<div class="tx-card">
  <div class="tx-card-header">
    <span class="tx-id">{req_id}</span>
    {badge}
  </div>
  <div class="tx-grid">
    <div class="tx-field"><span class="tx-label">Requester</span><span class="tx-value">{tx.get('requester','—')}</span></div>
    <div class="tx-field"><span class="tx-label">Amount</span><span class="tx-value">${tx.get('amount','—')}</span></div>
    <div class="tx-field"><span class="tx-label">Type</span><span class="tx-value">{tx.get('request_type','—').replace('_',' ').title()}</span></div>
    <div class="tx-field"><span class="tx-label">Priority</span><span class="tx-value">{tx.get('priority','—').upper()}</span></div>
    <div class="tx-field"><span class="tx-label">Approver</span><span class="tx-value">{tx.get('approver','—')} ({tx.get('approver_status','—')})</span></div>
    <div class="tx-field"><span class="tx-label">Account Status</span><span class="tx-value">{tx.get('account_status','—').replace('_',' ').title()}</span></div>
    <div class="tx-field"><span class="tx-label">Docs Complete</span><span class="tx-value">{docs}</span></div>
    <div class="tx-field"><span class="tx-label">Duplicate</span><span class="tx-value">{dup}</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_answer_card(result: dict, mode: str):
    """
    Renders an API response with a colored decision badge + answer text.
    Keeps the policy chunk expander for RAG mode.
    """
    if "error" in result:
        st.error(f"{result['error']}")
        return

    answer = result["answer"]
    badge = _badge_html(answer)
    alert_fn = _decision_color(answer)

    st.markdown(badge, unsafe_allow_html=True)
    alert_fn(answer)

    if mode == "rag" and result.get("contexts"):
        with st.expander("View Retrieved Policy Chunks"):
            for i, ctx in enumerate(result["contexts"]):
                st.markdown(f"**Chunk {i+1}:**")
                st.text(ctx)
                if i < len(result["contexts"]) - 1:
                    st.divider()


# kept for backwards compatibility — existing tabs call this
def render_answer(result: dict, mode: str):
    render_answer_card(result, mode)


def render_agent_with_steps(question: str) -> dict:
    """
    Calls the agent API while showing a 3-step progress indicator.
    Returns the API result dict.
    """
    with st.status("Agent reasoning...", expanded=True) as status:
        st.write("Step 1 — Fetching transaction details...")
        st.write("Step 2 — Retrieving policy context from ChromaDB...")
        st.write("Step 3 — Generating explanation...")
        result = query_agent(question)
        status.update(label="Reasoning Complete ✓", state="complete", expanded=False)
    return result


def render_comparison(question: str):
    """Two-column side-by-side comparison: Baseline RAG vs Autonomous Agent."""
    col_rag, col_agent = st.columns(2)

    with col_rag:
        st.markdown('<div class="system-header-rag">Baseline RAG</div>', unsafe_allow_html=True)
        with st.spinner("Retrieving and generating..."):
            rag_result = query_rag(question)
        render_answer_card(rag_result, "rag")

    with col_agent:
        st.markdown('<div class="system-header-agent">Autonomous Agent</div>', unsafe_allow_html=True)
        agent_result = render_agent_with_steps(question)
        render_answer_card(agent_result, "agent")
