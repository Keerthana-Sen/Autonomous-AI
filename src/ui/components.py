import streamlit as st
from src.ui.config import SAMPLE_QUESTIONS, APP_NAME, APP_SUBTITLE, APP_ICON
from src.ui.api_client import check_health


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


def render_question_input(selected: str) -> str:
    """Renders the question text input. Pre-fills if a sample is selected."""
    if selected == "Custom":
        return st.text_input(
            "Ask a question about a workflow decision:",
            placeholder="e.g. Why was REQ003 escalated instead of rejected?"
        )
    return st.text_input(
        "Ask a question about a workflow decision:",
        value=selected
    )


def _decision_color(answer: str):
    """Returns the appropriate st alert function based on decision keyword."""
    lower = answer.lower()
    if "rejected" in lower or "rejection" in lower:
        return st.error
    if "escalated" in lower or "escalation" in lower:
        return st.info
    return st.success


def render_answer(result: dict, mode: str):
    """
    Renders an API response consistently across all tabs.
    Color-codes by decision type: approved=green, escalated=orange, rejected=red.
    Shows retrieved chunks in an expander for RAG mode.
    """
    if "error" in result:
        st.error(f"{result['error']}")
        return

    answer = result["answer"]
    alert_fn = _decision_color(answer)
    alert_fn(answer)

    if mode == "rag" and result.get("contexts"):
        with st.expander("View Retrieved Policy Chunks"):
            for i, ctx in enumerate(result["contexts"]):
                st.markdown(f"**Chunk {i+1}:**")
                st.text(ctx)
                if i < len(result["contexts"]) - 1:
                    st.divider()
