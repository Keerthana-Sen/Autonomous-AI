import streamlit as st


def init():
    """Initialize all chat session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    if "awaiting_mode" not in st.session_state:
        st.session_state.awaiting_mode = False


def add_message(role: str, content: str, kind: str = "text", result=None, mode: str = None):
    """Append a message to chat history."""
    st.session_state.chat_history.append({
        "role": role,       # "user" or "bot"
        "content": content,
        "kind": kind,       # "text" or "answer"
        "result": result,   # API result dict
        "mode": mode        # "rag", "agent", "compare"
    })


def set_pending(question: str):
    """Mark a question as pending mode selection."""
    st.session_state.pending_question = question
    st.session_state.awaiting_mode = True


def clear_pending():
    """Reset pending state after mode is selected."""
    st.session_state.pending_question = None
    st.session_state.awaiting_mode = False


def clear_all():
    """Wipe entire chat history and state."""
    st.session_state.chat_history = []
    st.session_state.pending_question = None
    st.session_state.awaiting_mode = False