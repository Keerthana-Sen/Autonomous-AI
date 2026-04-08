import streamlit as st
from src.ui.chat_state import init, add_message, set_pending, clear_all
from src.ui.chat_bubbles import render_history
from src.ui.chat_actions import render_mode_buttons
from src.ui.config import SAMPLE_QUESTIONS


def render_chat_mode():
    """Entry point for chat mode — called by app.py."""
    init()

    st.markdown("### ⚡ XFLOW Chat")
    st.caption("Ask a question — then choose how you want it answered.")
    st.divider()

    # Chat history
    render_history(st.session_state.chat_history)

    # Mode buttons appear after question is asked
    if st.session_state.awaiting_mode:
        render_mode_buttons()

    st.divider()

    # Sample question picker
    picked = st.selectbox(
        "Sample questions:",
        [""] + SAMPLE_QUESTIONS,
        index=0,
        label_visibility="collapsed"
    )

    # Chat input box
    typed = st.chat_input("Ask about a workflow decision...")
    question = typed or picked or ""

    # Handle new question
    if question and not st.session_state.awaiting_mode:
        add_message("user", question)
        add_message("bot", f'Got it! How would you like this answered?')
        set_pending(question)
        st.rerun()

    # Clear chat
    if st.session_state.chat_history:
        if st.button("Clear Chat"):
            clear_all()
            st.rerun()