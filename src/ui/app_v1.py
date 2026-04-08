import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from src.ui.config import SAMPLE_QUESTIONS
from src.ui.components import render_header, render_sidebar, render_question_input, render_answer
from src.ui.api_client import query_rag, query_agent
from src.ui.chat_mode import render_chat_mode

render_header()

# ── Mode toggle in header area ────────────────────────────────────────────────
col1, col2 = st.columns([6, 1])
with col2:
    chat_mode = st.toggle("Chat Mode", value=False)

st.divider()

# ── Switch between modes ──────────────────────────────────────────────────────
if chat_mode:
    render_chat_mode()
else:
    selected = render_sidebar()
    question = render_question_input(selected)
    st.divider()

    tab_compare, tab_rag, tab_agent, tab_scores = st.tabs([
        "Compare", "Baseline RAG", "Autonomous Agent", "RAGAS Scores"
    ])

    with tab_compare:
        st.subheader("RAG vs Agent — Side by Side")
        if st.button("Run Both", disabled=not question):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("Baseline RAG")
                with st.spinner("Retrieving..."):
                    rag_result = query_rag(question)
                render_answer(rag_result, "rag")
            with col2:
                st.markdown("Autonomous Agent")
                with st.spinner("Reasoning..."):
                    agent_result = query_agent(question)
                render_answer(agent_result, "agent")
        else:
            st.info("Enter a question above and click **Run Both**.")

    with tab_rag:
        st.subheader("Baseline RAG")
        if st.button("Ask RAG", disabled=not question):
            with st.spinner("Retrieving..."):
                render_answer(query_rag(question), "rag")

    with tab_agent:
        st.subheader("Autonomous Agent")
        if st.button("Ask Agent", disabled=not question):
            with st.spinner("Reasoning..."):
                render_answer(query_agent(question), "agent")

    with tab_scores:
        st.subheader("RAGAS Evaluation Scores")
        st.info("Load scores from data/results/ to display here.")