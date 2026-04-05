import streamlit as st
from src.ui.config import SAMPLE_QUESTIONS, APP_NAME, APP_SUBTITLE, APP_ICON
from src.ui.api_client import check_health


def render_header():
    """Renders the XFLOW header and status indicator."""
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_SUBTITLE}",
        page_icon=APP_ICON,
        layout="wide"
    )

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"{APP_ICON} {APP_NAME}")
        st.caption(APP_SUBTITLE)
    with col2:
        # Live API health indicator
        if check_health():
            st.success("API Online")
        else:
            st.error("API Offline")


def render_sidebar() -> str:
    """
    Renders sidebar with sample questions.
    Returns the selected or typed question.
    """
    st.sidebar.title(f"{APP_ICON} {APP_NAME}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sample Questions")

    selected = st.sidebar.radio(
        "Pick one or type your own below:",
        ["Custom"] + SAMPLE_QUESTIONS
    )

    st.sidebar.markdown("---")
    st.sidebar.info("Make sure FastAPI is running on port 8000 before querying.")

    return selected


def render_question_input(selected: str) -> str:
    """Renders the question text input. Pre-fills if sample selected."""
    if selected == "Custom":
        return st.text_input(
            "Ask a question about a workflow decision:",
            placeholder="e.g. Why was REQ003 escalated?"
        )
    return st.text_input(
        "Ask a question about a workflow decision:",
        value=selected
    )


def render_answer(result: dict, mode: str):
    """
    Renders an API response consistently across all tabs.
    Shows error, answer, and optionally retrieved chunks for RAG.
    """
    if "error" in result:
        st.error(f"{result['error']}")
        return

    # Answer
    st.success(result["answer"])

    # Show retrieved chunks only for RAG mode
    if mode == "rag" and result.get("contexts"):
        with st.expander("View Retrieved Policy Chunks"):
            for i, ctx in enumerate(result["contexts"]):
                st.markdown(f"**Chunk {i+1}:**")
                st.text(ctx)
                if i < len(result["contexts"]) - 1:
                    st.divider()