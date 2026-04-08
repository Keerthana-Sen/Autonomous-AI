import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from src.ui.components import render_header, render_sidebar, render_question_input, render_answer
from src.ui.api_client import query_rag, query_agent

# ── Page setup ────────────────────────────────────────────────────────────────
render_header()

# ── Sidebar + question input ──────────────────────────────────────────────────
selected = render_sidebar()
question = render_question_input(selected)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_compare, tab_rag, tab_agent = st.tabs([
    "Compare RAG vs Agent",
    "Baseline RAG",
    "Autonomous Agent"
])


# ── Tab 1: Side by side comparison ───────────────────────────────────────────
with tab_compare:
    st.subheader("Compare RAG vs Agent — Side by Side")
    st.caption("Run the same question through both systems and compare explanations.")

    if st.button("Run Both", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            col_rag, col_agent = st.columns(2)

            with col_rag:
                st.markdown("Baseline RAG")
                with st.spinner("Retrieving and generating..."):
                    rag_result = query_rag(question)
                render_answer(rag_result, "rag")

            with col_agent:
                st.markdown("Autonomous Agent")
                with st.spinner("Agent reasoning..."):
                    agent_result = query_agent(question)
                render_answer(agent_result, "agent")
    else:
        st.info("Enter a question above and click **Run Both** to compare.")


# ── Tab 2: Baseline RAG ───────────────────────────────────────────────────────
with tab_rag:
    st.subheader("Baseline RAG")
    st.caption("Retrieves relevant policy chunks from ChromaDB, then generates an answer with Groq LLM.")

    if st.button("Ask RAG", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Retrieving policy chunks and generating answer..."):
                result = query_rag(question)
            render_answer(result, "rag")


# ── Tab 3: Autonomous Agent ───────────────────────────────────────────────────
with tab_agent:
    st.subheader("Autonomous Agent")
    st.caption("LangGraph agent reasons step-by-step using tools to explain the decision.")

    if st.button("Ask Agent", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Agent reasoning... (may take a few seconds)"):
                result = query_agent(question)
            render_answer(result, "agent")