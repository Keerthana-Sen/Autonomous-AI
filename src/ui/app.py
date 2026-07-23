import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
from src.ui.components import (
    render_header, render_sidebar, render_question_input,
    render_answer_card, render_transaction_card, render_comparison,
    render_agent_with_steps, detect_decision
)
from src.ui.api_client import query_rag, inject_transaction
from src.ui.config import TRANSACTIONS_DATA, REQ_IDS

# ── Page setup ────────────────────────────────────────────────────────────────
render_header()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    :root { --navy: #0a1628; --indigo: #3949ab; --blue: #4f8ef7; }

    footer {visibility: hidden;}

    .block-container { padding-top: 4rem; padding-bottom: 2rem; }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #1a2560 100%) !important;
        border-right: 2px solid #3949ab;
        border-radius: 0 20px 20px 0;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span { color: #c5cae9 !important; }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 { color: #e8eaf6 !important; }

    .stTabs [data-baseweb="tab"] { font-size: 0.95rem; font-weight: 600; padding: 0.6rem 1.4rem; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #4f8ef7 !important; color: #4f8ef7 !important; }

    .stButton > button {
        font-weight: 600; border-radius: 8px; padding: 0.4rem 1.8rem;
        background-color: #3949ab; color: #ffffff; border: none;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover { background-color: #4f8ef7 !important; border: none; }

    .badge {
        display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px;
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 0.5rem;
    }
    .badge-approved  { background: #1b5e20; color: #a5d6a7; }
    .badge-rejected  { background: #b71c1c; color: #ffcdd2; }
    .badge-escalated { background: #0d47a1; color: #bbdefb; }
    .badge-unknown   { background: #37474f; color: #cfd8dc; }

    .tx-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a2560 100%);
        border: 1px solid #3949ab; border-radius: 12px;
        padding: 1.2rem 1.4rem; margin-bottom: 1.2rem;
    }
    .tx-card-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; }
    .tx-id { font-size: 1.15rem; font-weight: 700; color: #e8eaf6; }
    .tx-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.6rem 1.2rem; }
    .tx-field { display: flex; flex-direction: column; }
    .tx-label { font-size: 0.72rem; color: #7986cb; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }
    .tx-value { font-size: 0.88rem; color: #c5cae9; font-weight: 500; }

    .system-header-rag {
        background: linear-gradient(90deg, #1a237e, #283593); color: #c5cae9;
        padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
        margin-bottom: 0.8rem; border-left: 4px solid #5c6bc0;
    }
    .system-header-agent {
        background: linear-gradient(90deg, #0d47a1, #1565c0); color: #bbdefb;
        padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
        margin-bottom: 0.8rem; border-left: 4px solid #42a5f5;
    }

    .notif-card {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a2560 100%);
        border: 1px solid #3949ab; border-radius: 10px;
        padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; cursor: pointer;
    }
    .notif-card:hover { border-color: #4f8ef7; }
    .notif-title { font-size: 0.88rem; font-weight: 700; color: #e8eaf6; margin-bottom: 2px; }
    .notif-sub   { font-size: 0.75rem; color: #7986cb; }

    [data-testid="stAppDeployButton"] { display: none !important; }

    /* ── Bell popover button styling ────────────────────────────────────── */
    [data-testid="stPopover"] > button {
        background: transparent !important;
        border: 1px solid #3949ab !important;
        border-radius: 20px !important;
        color: #c5cae9 !important;
        font-size: 1.05rem !important;
        padding: 3px 10px !important;
        min-height: 0 !important;
        height: 30px !important;
        font-weight: 600 !important;
    }
    [data-testid="stPopover"] > button:hover {
        background: #1a2560 !important;
        border-color: #4f8ef7 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("notifications", []),
    ("notif_viewed", set()),
    ("viewing_notif", None),
    ("custom_req_counter", 0),
    ("last_submit_result", None),
    ("rag_result", None),
    ("agent_result", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
selected = render_sidebar()

# ── Bell notification (top-right of page, styled as toolbar pill) ────────────
unread = [n for n in st.session_state.notifications if n["id"] not in st.session_state.notif_viewed]
bell_label = f"🔔 {len(unread)}" if unread else "🔔"

_spacer, _bell_col = st.columns([11, 1])
with _bell_col:
    with st.popover(bell_label, use_container_width=False):
        if not st.session_state.notifications:
            st.caption("No notifications yet.")
        else:
            decision_colors = {
                "rejected":  ("#b71c1c", "#ffcdd2"),
                "escalated": ("#0d47a1", "#bbdefb"),
                "approved":  ("#1b5e20", "#a5d6a7"),
            }
            for n in reversed(st.session_state.notifications):
                bg, fg = decision_colors.get(n["decision"], ("#37474f", "#cfd8dc"))
                st.markdown(f"""
<div class="notif-card" style="border-left: 4px solid {bg};">
  <div class="notif-title">{n['req_id']} — {n['decision'].upper()}</div>
  <div class="notif-sub">{n['requester']} · {n['request_type']} · ${n['amount']}</div>
</div>""", unsafe_allow_html=True)
                if st.button("View Details", key=f"notif_view_{n['id']}"):
                    st.session_state.viewing_notif = n["id"]
                    st.session_state.notif_viewed.add(n["id"])
                    st.rerun()

# ── Notification detail overlay ───────────────────────────────────────────────
if st.session_state.viewing_notif is not None:
    notif = next((n for n in st.session_state.notifications if n["id"] == st.session_state.viewing_notif), None)
    if notif:
        if st.button("← Back"):
            st.session_state.viewing_notif = None
            st.rerun()

        decision_label = notif["decision"].upper()
        decision_colors = {"rejected": "#b71c1c", "escalated": "#0d47a1", "approved": "#1b5e20"}
        color = decision_colors.get(notif["decision"], "#37474f")

        st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1b2a,#1a2560);border:1px solid #3949ab;
border-left:5px solid {color};border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
  <div style="font-size:1.1rem;font-weight:700;color:#e8eaf6;margin-bottom:4px;">
    Request {notif['req_id']} — {decision_label}
  </div>
  <div style="font-size:0.82rem;color:#7986cb;">
    {notif['requester']} · {notif['request_type'].replace('_',' ').title()} · ${notif['amount']}
  </div>
</div>""", unsafe_allow_html=True)

        render_transaction_card(notif["req_id"], notif["tx"])
        st.markdown("---")
        st.markdown("#### Baseline RAG vs Autonomous Agent")

        col_rag, col_agent = st.columns(2)
        with col_rag:
            st.markdown('<div class="system-header-rag">Baseline RAG</div>', unsafe_allow_html=True)
            with st.spinner("Retrieving policy chunks..."):
                rag_result = query_rag(notif["question"])
            render_answer_card(rag_result, "rag")

        with col_agent:
            st.markdown('<div class="system-header-agent">Autonomous Agent</div>', unsafe_allow_html=True)
            render_answer_card(notif["agent_result"], "agent")

        st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_submit, tab_rag, tab_agent = st.tabs([
    "Submit Request",
    "Baseline RAG",
    "Autonomous Agent",
])


# ── Tab 1: Submit Request ─────────────────────────────────────────────────────
with tab_submit:
    st.subheader("Submit a Request")
    st.caption(
        "Fill out a new request or analyze an existing transaction — "
        "then see how Baseline RAG and the Autonomous Agent explain the decision side by side."
    )

    mode = st.radio(
        "Mode",
        ["Submit a new request", "Analyze an existing transaction"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # ── Mode A: New request ───────────────────────────────────────────────
    if mode == "Submit a new request":
        with st.form("new_request_form"):
            st.markdown("**Request Details**")
            col1, col2, col3 = st.columns(3)
            with col1:
                requester = st.text_input("Your Name", value="Alex")
                amount = st.number_input("Amount (USD)", min_value=1, max_value=100000, value=2000, step=100)
                request_type = st.selectbox("Request Type", [
                    "software_license", "hardware", "infrastructure", "training", "travel"
                ])
            with col2:
                priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
                approver = st.selectbox("Approver", ["Bob", "Sarah", "John"])
                approver_status = st.radio("Approver Status", ["available", "unavailable"], horizontal=True)
            with col3:
                account_status = st.selectbox("Account Status", ["active", "suspended", "under_review"])
                employee_level = st.selectbox("Employee Level", ["3", "4", "5", "6"])
                docs_complete = st.radio("Documentation Complete", ["TRUE", "FALSE"], horizontal=True)
                duplicate = st.radio("Duplicate Request", ["FALSE", "TRUE"], horizontal=True)

            submitted = st.form_submit_button("Submit Request", type="primary")

        if submitted:
            st.session_state.custom_req_counter += 1
            custom_id = f"REQCUSTOM{st.session_state.custom_req_counter:03d}"

            tx_payload = {
                "request_id": custom_id,
                "requester": requester,
                "amount": str(amount),
                "request_type": request_type,
                "priority": priority,
                "approver": approver,
                "approver_status": approver_status,
                "documentation_complete": docs_complete,
                "duplicate": duplicate,
                "account_status": account_status,
                "employee_level": employee_level,
                "decision": "pending",
            }

            inject_result = inject_transaction(tx_payload)
            if "error" in inject_result:
                st.error(f"Failed to inject transaction: {inject_result['error']}")
            else:
                tx_display = {k: v for k, v in tx_payload.items() if k != "request_id"}
                q = (
                    f"A new {priority}-priority {request_type.replace('_', ' ')} request "
                    f"({custom_id}) for ${amount} was submitted by {requester}. "
                    f"Documentation complete: {docs_complete}. "
                    f"Account status: {account_status}. "
                    f"Approver {approver} is {approver_status}. "
                    f"What decision should be made and why?"
                )
                agent_result = render_agent_with_steps(q)
                decision = detect_decision(agent_result.get("answer", ""))
                st.session_state.notifications.append({
                    "id": custom_id,
                    "req_id": custom_id,
                    "requester": requester,
                    "request_type": request_type,
                    "amount": str(amount),
                    "decision": decision,
                    "agent_result": agent_result,
                    "question": q,
                    "tx": tx_display,
                })
                st.session_state.last_submit_result = custom_id
                st.rerun()

    # Show confirmation after rerun
    if st.session_state.last_submit_result:
        st.success(
            f"Request {st.session_state.last_submit_result} submitted — "
            f"check the 🔔 bell above for the decision.",
            icon="📬"
        )

    # ── Mode B: Analyze existing ──────────────────────────────────────────
    if mode == "Analyze an existing transaction":
        req_id = st.selectbox("Select a transaction", REQ_IDS)
        tx = TRANSACTIONS_DATA[req_id]
        render_transaction_card(req_id, tx)

        if st.button("Analyze Decision", type="primary"):
            q = f"Why was {req_id} {tx['decision']}?"
            st.markdown("---")
            render_comparison(q)


# ── Tab 2: Baseline RAG ───────────────────────────────────────────────────────
with tab_rag:
    st.subheader("Baseline RAG")
    st.caption("Retrieves relevant policy chunks from the ChromaDB vector store, then generates an answer with Groq LLM.")

    question = render_question_input(selected, key="rag_question")
    if st.button("Ask RAG", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Retrieving policy chunks and generating answer..."):
                st.session_state.rag_result = query_rag(question)

    if st.session_state.get("rag_result"):
        render_answer_card(st.session_state.rag_result, "rag")


# ── Tab 3: Autonomous Agent ───────────────────────────────────────────────────
with tab_agent:
    st.subheader("Autonomous Agent")
    st.caption("LangGraph agent reasons step-by-step: fetches transaction details, retrieves policy context, then derives the decision.")

    question = render_question_input(selected, key="agent_question")
    if st.button("Ask Agent", disabled=not question):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            st.session_state.agent_result = render_agent_with_steps(question)

    if st.session_state.get("agent_result"):
        render_answer_card(st.session_state.agent_result, "agent")
