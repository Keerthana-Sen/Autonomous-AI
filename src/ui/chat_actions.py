import streamlit as st
from src.ui.api_client import query_rag, query_agent
from src.ui.chat_state import add_message, clear_pending


def handle_mode(mode: str):
    """
    Runs the selected mode against the pending question.
    Adds result to chat history, clears pending state, reruns.
    """
    question = st.session_state.pending_question

    if mode == "rag":
        add_message("user", "Baseline RAG")
        with st.spinner("Retrieving and generating..."):
            result = query_rag(question)
        add_message("bot", "", kind="answer", result=result, mode="rag")

    elif mode == "agent":
        add_message("user", "Autonomous Agent")
        with st.spinner("Agent reasoning..."):
            result = query_agent(question)
        add_message("bot", "", kind="answer", result=result, mode="agent")

    elif mode == "compare":
        add_message("user", "Compare Both")
        with st.spinner("Running both systems..."):
            rag_result   = query_rag(question)
            agent_result = query_agent(question)
        add_message("bot", "", kind="answer",
                    result={"rag": rag_result, "agent": agent_result},
                    mode="compare")

    clear_pending()
    st.rerun()


def render_mode_buttons():
    """3 buttons shown after user asks a question."""
    st.markdown("**How do you want this answered?**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Baseline RAG", use_container_width=True):
            handle_mode("rag")
    with col2:
        if st.button("Autonomous Agent", use_container_width=True):
            handle_mode("agent")
    with col3:
        if st.button("Compare Both", use_container_width=True):
            handle_mode("compare")