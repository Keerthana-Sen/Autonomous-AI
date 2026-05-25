import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from src.ui.components import render_header, render_sidebar, render_question_input, render_answer
from src.ui.api_client import query_rag, query_agent

# ── Page setup ────────────────────────────────────────────────────────────────
render_header()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Color scheme: navy / indigo / blue ────────────────────────────── */
    :root {
        --navy:   #0a1628;
        --indigo: #3949ab;
        --blue:   #4f8ef7;
    }

    /* ── Hide Streamlit footer ─────────────────────────────────────────── */
    footer {visibility: hidden;}

    /* ── Push main content down so title isn't flush to top ───────────── */
    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
    }

    /* ── Sidebar: navy gradient, indigo border, rounded right edge ─────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #1a2560 100%) !important;
        border-right: 2px solid #3949ab;
        border-radius: 0 20px 20px 0;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #c5cae9 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e8eaf6 !important;
    }

    /* ── Tabs: indigo accent on selected ───────────────────────────────── */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
        padding: 0.6rem 1.4rem;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #4f8ef7 !important;
        color: #4f8ef7 !important;
    }

    /* ── Buttons: indigo fill, blue on hover ───────────────────────────── */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
        padding: 0.4rem 1.8rem;
        background-color: #3949ab;
        color: #ffffff;
        border: none;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #4f8ef7 !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

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
    st.caption("Run the same question through both systems and compare how each derives its explanation.")

    if st.button("Run Both", disabled=not question, type="primary"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            col_rag, col_agent = st.columns(2)

            with col_rag:
                st.markdown("### Baseline RAG")
                with st.spinner("Retrieving and generating..."):
                    rag_result = query_rag(question)
                render_answer(rag_result, "rag")

            with col_agent:
                st.markdown("### Autonomous Agent")
                with st.spinner("Agent reasoning..."):
                    agent_result = query_agent(question)
                render_answer(agent_result, "agent")
    else:
        st.info("Select a sample question from the sidebar or type your own, then click **Run Both** to compare explanations.")


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
    st.caption("LangGraph agent reasons step-by-step: fetches transaction details, retrieves policy context, then derives the decision.")

    if st.button("Ask Agent", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Agent reasoning... (may take a few seconds)"):
                result = query_agent(question)
            render_answer(result, "agent")
