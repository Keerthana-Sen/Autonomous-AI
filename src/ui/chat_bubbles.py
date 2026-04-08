import streamlit as st
from src.ui.components import render_answer


def user_bubble(text: str):
    """Right-aligned blue user bubble."""
    st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin:8px 0;">
            <div style="
                background:#2E75B6; color:white;
                padding:10px 16px;
                border-radius:18px 18px 4px 18px;
                max-width:70%; font-size:0.93rem; line-height:1.5;
            ">{text}</div>
        </div>""",
        unsafe_allow_html=True
    )


def bot_bubble(text: str):
    """Left-aligned dark bot text bubble."""
    st.markdown(f"""
        <div style="display:flex; justify-content:flex-start; margin:8px 0;">
            <div style="
                background:#2a2a2a; color:#f0f0f0;
                padding:10px 16px;
                border-radius:18px 18px 18px 4px;
                max-width:70%; font-size:0.93rem; line-height:1.5;
            ">⚡ {text}</div>
        </div>""",
        unsafe_allow_html=True
    )


def answer_bubble(result: dict, mode: str):
    """Renders an answer — side by side for compare, single for rag/agent."""
    if mode == "compare":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Baseline RAG")
            render_answer(result["rag"], "rag")
        with col2:
            st.markdown("Autonomous Agent")
            render_answer(result["agent"], "agent")
    else:
        label = "Baseline RAG" if mode == "rag" else "Autonomous Agent"
        st.markdown(f"##### {label}")
        render_answer(result, mode)


def render_history(history: list):
    """Loops through and renders all messages in chat history."""
    for msg in history:
        if msg["role"] == "user":
            user_bubble(msg["content"])
        elif msg["kind"] == "text":
            bot_bubble(msg["content"])
        elif msg["kind"] == "answer":
            answer_bubble(msg["result"], msg["mode"])