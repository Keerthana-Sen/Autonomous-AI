import re
import streamlit as st
from src.ui.config import SAMPLE_QUESTIONS, APP_NAME, APP_SUBTITLE, APP_ICON
from src.ui.api_client import query_rag, query_agent


def render_header():
    """Renders the XFLOW header and API status indicator."""
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_SUBTITLE}",
        page_icon=APP_ICON,
        layout="wide"
    )

    st.title(f"{APP_ICON} {APP_NAME} — {APP_SUBTITLE}")
    st.caption(
        "Compare a Baseline RAG pipeline against a LangGraph Autonomous Agent "
        "for explaining enterprise workflow approval decisions."
    )



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
    Negation-aware: 'would not have been approved' does not badge as approved.
    """
    lower = text.lower()
    for pattern, decision in [
        (r"\bwould (?:\w+ )?(?:have )?(?:\w+ )?been escalated\b", "escalated"),
        (r"\bwould (?:\w+ )?(?:have )?(?:\w+ )?been approved\b", "approved"),
        (r"\bwould (?:\w+ )?(?:have )?(?:\w+ )?been rejected\b", "rejected"),
        (r"\bwas escalated\b", "escalated"),
        (r"\bwas approved\b", "approved"),
        (r"\bwas rejected\b", "rejected"),
    ]:
        m = re.search(pattern, lower)
        if m:
            preceding = lower[max(0, m.start() - 30):m.start()]
            matched_text = m.group(0)
            if "not" not in preceding and "never" not in preceding and "not" not in matched_text and "never" not in matched_text:
                return decision
    for keyword, decision in [("escalated", "escalated"), ("approved", "approved"), ("approval", "approved"), ("rejected", "rejected")]:
        for m in re.finditer(rf"\b{keyword}\b", lower):
            preceding = lower[max(0, m.start() - 30):m.start()]
            if "not" not in preceding and "never" not in preceding:
                return decision
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


def detect_decision(text: str) -> str:
    return _detect_decision(text)


def render_transaction_card(req_id: str, tx: dict):
    decision = tx.get("decision", "")
    badge = _badge_html(decision) if decision and decision != "pending" else ""
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


def _donut_html(pct: float, decision: str) -> str:
    """CSS conic-gradient donut whose color matches the decision badge."""
    palette = {
        "approved":  ("#a5d6a7", "#1b5e20"),
        "rejected":  ("#ffcdd2", "#b71c1c"),
        "escalated": ("#bbdefb", "#0d47a1"),
    }
    fg, track = palette.get(decision, ("#cfd8dc", "#37474f"))
    return f"""
<div style="display:inline-flex;flex-direction:column;align-items:center;gap:3px;vertical-align:middle;">
  <div style="
    width:56px;height:56px;border-radius:50%;
    background:conic-gradient({fg} {pct}%, {track} 0%);
    display:flex;align-items:center;justify-content:center;">
    <div style="
      width:40px;height:40px;border-radius:50%;background:#0d1b2a;
      display:flex;align-items:center;justify-content:center;
      font-size:0.75rem;font-weight:700;color:{fg};">{pct:.0f}%</div>
  </div>
  <span style="font-size:0.62rem;color:{fg};letter-spacing:0.04em;opacity:0.8;">CONFIDENCE</span>
</div>"""


def render_answer_card(result: dict, mode: str):
    """
    Renders an API response with a colored decision badge + answer text.
    Keeps the policy chunk expander for RAG mode.
    """
    if "error" in result:
        st.error(f"{result['error']}")
        return

    answer = result["answer"]
    confidence = result.get("confidence", 0.0)
    decision = _detect_decision(answer)
    badge = _badge_html(answer)
    donut = _donut_html(confidence, decision)
    alert_fn = _decision_color(answer)
    safe_answer = answer.replace("$", r"\$")

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">'
        f'{badge}{donut}</div>',
        unsafe_allow_html=True
    )
    alert_fn(safe_answer)

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
        st.write("Step 2 — Retrieving policy context from the ChromaDB vector store...")
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
