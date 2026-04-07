import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/chat/")

st.set_page_config(page_title="Olist Multi-Agent Assistant", layout="wide")
st.title("🛒 Olist Commerce Intelligence Copilot")
st.caption("Ask business questions about sales, delivery, reviews, sellers, products, and recommendations.")


# ----------------------------
# Theme
# ----------------------------
AGENT_THEME = {
    "sql": {
        "bg": "#E8F1FB",
        "text": "#1D4ED8",
        "border": "#BFDBFE",
        "label": "SQL Agent",
        "title": "SQL Agent — Analytics & KPIs",
    },
    "rag": {
        "bg": "#ECFDF5",
        "text": "#047857",
        "border": "#A7F3D0",
        "label": "RAG Agent",
        "title": "RAG Agent — Definitions & Knowledge",
    },
    "rootcause": {
        "bg": "#FFF7ED",
        "text": "#C2410C",
        "border": "#FED7AA",
        "label": "Root Cause Agent",
        "title": "Root Cause Agent — Diagnostics",
    },
    "recommendation": {
        "bg": "#F5F3FF",
        "text": "#6D28D9",
        "border": "#DDD6FE",
        "label": "Recommendation Agent",
        "title": "Recommendation Agent — Actions & Strategy",
    },
    "rootcause_recommendation": {
        "bg": "#FDF2F8",
        "text": "#BE185D",
        "border": "#FBCFE8",
        "label": "Root Cause → Recommendation",
        "title": "Root Cause → Recommendation",
    },
}


# ----------------------------
# Sample prompts
# ----------------------------
SQL_SAMPLES = [
    "What are the top 5 product categories by revenue?",
    "Compare seller performance by review score and late delivery rate.",
    "What is the late delivery rate by product category?",
]

RAG_SAMPLES = [
    "How is late delivery defined in this system?",
    "What does freight ratio mean?",
    "Explain the relationship between orders, order_items, and products.",
]

ROOTCAUSE_SAMPLES = [
    "Why are review scores low for some sellers?",
    "What are the main drivers of late deliveries?",
    "Why do some product categories have lower customer satisfaction?",
]

RECOMMENDATION_SAMPLES = [
    "What should management do to reduce late deliveries?",
    "How can we improve customer satisfaction for low-performing sellers?",
    "What actions should we prioritize to improve marketplace performance?",
]


# ----------------------------
# Session state
# ----------------------------
if "conversations" not in st.session_state:
    st.session_state.conversations = []

if "last_debug" not in st.session_state:
    st.session_state.last_debug = {}

if "draft_prompt" not in st.session_state:
    st.session_state.draft_prompt = ""


# ----------------------------
# Helpers
# ----------------------------
def set_prompt(prompt_text: str):
    st.session_state.draft_prompt = prompt_text


def call_api(question, history):
    payload = {
        "question": question,
        "history": history,
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "answer": f"API error: {e}",
            "selected_agent": "N/A",
            "debug": {},
        }


def build_history_from_conversations(conversations, max_pairs=10):
    history = []
    for convo in conversations[-max_pairs:]:
        history.append({"role": "user", "content": convo["question"]})
        history.append({"role": "assistant", "content": convo["answer"]})
    return history


def process_prompt(prompt_text: str):
    history = build_history_from_conversations(st.session_state.conversations, max_pairs=10)

    with st.spinner("Generating response..."):
        result = call_api(prompt_text, history)

    answer = result.get("answer", "No answer generated.")
    selected_agent = result.get("selected_agent", "Unknown")
    debug = result.get("debug", {})

    st.session_state.conversations.append(
        {
            "question": prompt_text,
            "answer": answer,
            "agent": selected_agent,
            "debug": debug,
        }
    )
    st.session_state.last_debug = debug
    st.session_state.draft_prompt = ""


def render_sidebar_section_header(theme_key: str):
    theme = AGENT_THEME[theme_key]
    st.markdown(
        f"""
        <div style="
            padding: 8px 12px;
            border-radius: 10px;
            background-color: {theme['bg']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 8px;
        ">
            {theme['title']}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_agent_tag(agent_name: str):
    agent_to_theme = {
        "SQLAgent": "sql",
        "RAGAgent": "rag",
        "RootCauseAgent": "rootcause",
        "RecommendationAgent": "recommendation",
        "RootCauseAgent -> RecommendationAgent": "rootcause_recommendation",
    }

    theme_key = agent_to_theme.get(agent_name)

    if theme_key is None:
        bg = "#F3F4F6"
        text = "#374151"
        border = "#E5E7EB"
        label = agent_name
    else:
        theme = AGENT_THEME[theme_key]
        bg = theme["bg"]
        text = theme["text"]
        border = theme["border"]
        label = theme["label"]

    st.markdown(
        f"""
        <div style="
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            background-color: {bg};
            color: {text};
            border: 1px solid {border};
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 8px;
            margin-bottom: 4px;
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.header("Prompt Library")
    st.caption("Choose a sample question by capability.")

    render_sidebar_section_header("sql")
    with st.expander("Show prompts", expanded=True):
        for q in SQL_SAMPLES:
            if st.button(q, key=f"sql_{q}"):
                set_prompt(q)

    render_sidebar_section_header("rag")
    with st.expander("Show prompts", expanded=False):
        for q in RAG_SAMPLES:
            if st.button(q, key=f"rag_{q}"):
                set_prompt(q)

    render_sidebar_section_header("rootcause")
    with st.expander("Show prompts", expanded=False):
        for q in ROOTCAUSE_SAMPLES:
            if st.button(q, key=f"root_{q}"):
                set_prompt(q)

    render_sidebar_section_header("recommendation")
    with st.expander("Show prompts", expanded=False):
        for q in RECOMMENDATION_SAMPLES:
            if st.button(q, key=f"rec_{q}"):
                set_prompt(q)

    st.divider()
    st.subheader("View Options")
    show_debug_panel = st.toggle("Show telemetry panel", value=True)
    show_full_debug = st.toggle("Show raw debug JSON", value=False)


# ----------------------------
# Telemetry renderers
# ----------------------------
def render_supervisor_telemetry(debug):
    sup = debug.get("supervisor_telemetry", {})
    routing = sup.get("routing", {})
    tokens = sup.get("tokens", {})
    request = sup.get("request", {})

    st.subheader("Supervisor")
    c1, c2 = st.columns(2)
    c1.metric("Selected Route", routing.get("selected_route", "N/A"))
    c2.metric("Total Request Latency (s)", request.get("total_request_latency_sec", "N/A"))

    c3, c4 = st.columns(2)
    c3.metric("Routing Latency (s)", routing.get("routing_latency_sec", "N/A"))
    c4.metric("Supervisor Input Tokens", tokens.get("input_tokens", "N/A"))


def render_agent_summary(debug):
    agent = debug.get("agent_telemetry", {})
    if not agent:
        st.info("No agent telemetry available.")
        return

    timing = agent.get("timing", {})
    tokens = agent.get("tokens", {})

    st.subheader(f"Agent Summary — {agent.get('agent_name', 'Unknown')}")
    c1, c2 = st.columns(2)
    c1.metric("Total Agent Latency (s)", timing.get("total_latency_sec", "N/A"))
    c2.metric("Total Tokens", tokens.get("total_tokens", "N/A"))

    c3, c4 = st.columns(2)
    c3.metric("Input Tokens", tokens.get("input_tokens", "N/A"))
    c4.metric("Output Tokens", tokens.get("output_tokens", "N/A"))


def render_sql_details(agent):
    timing = agent.get("timing", {})
    query = agent.get("query", {})

    st.subheader("SQL Details")
    c1, c2, c3 = st.columns(3)
    c1.metric("SQL Generation (s)", timing.get("sql_generation_sec", "N/A"))
    c2.metric("SQL Execution (s)", timing.get("sql_execution_sec", "N/A"))
    c3.metric("Rows Returned", query.get("row_count", "N/A"))

    if query.get("sql_query"):
        with st.expander("Generated SQL Query", expanded=True):
            st.code(query["sql_query"], language="sql")

    if query.get("preview"):
        with st.expander("Query Result Preview", expanded=True):
            st.dataframe(query["preview"], use_container_width=True)


def render_rag_details(agent):
    timing = agent.get("timing", {})
    retrieval = agent.get("retrieval", {})

    st.subheader("Knowledge Retrieval Details")
    c1, c2 = st.columns(2)
    c1.metric("Retrieval Time (s)", timing.get("retrieval_sec", "N/A"))
    c2.metric("Sources Retrieved", retrieval.get("sources_count", "N/A"))

    sources = retrieval.get("sources", [])
    if sources:
        with st.expander("Retrieved Sources", expanded=False):
            st.json(sources)


def render_rootcause_details(agent):
    timing = agent.get("timing", {})
    diagnostics = agent.get("diagnostics", {})
    timing_items = {
        k: v for k, v in timing.items()
        if k.endswith("_sec") and k != "total_latency_sec"
    }

    st.subheader("Diagnostic Details")

    if timing_items:
        with st.expander("Diagnostic Query Timings", expanded=False):
            st.json(timing_items)

    if diagnostics:
        with st.expander("Diagnostics Output", expanded=False):
            st.json(diagnostics)


def render_recommendation_details(agent):
    timing = agent.get("timing", {})
    analytics = agent.get("analytics", {})
    retrieval = agent.get("retrieval", {})

    st.subheader("Recommendation Details")
    c1, c2, c3 = st.columns(3)
    c1.metric("Retrieval Time (s)", timing.get("retrieval_sec", "N/A"))
    c2.metric("RAG Docs Count", retrieval.get("rag_docs_count", "N/A"))
    c3.metric("Generation Time (s)", timing.get("recommendation_generation_sec", "N/A"))

    if analytics.get("query_logs"):
        with st.expander("Analytics Query Logs", expanded=False):
            st.json(analytics["query_logs"])

    if retrieval.get("sources_preview"):
        with st.expander("Knowledge Sources Preview", expanded=False):
            st.json(retrieval["sources_preview"])


def render_quality(agent):
    quality = agent.get("quality", {})
    note = quality.get("accuracy_note", "No explicit quality note available.")
    st.subheader("Quality Note")
    st.write(note)


def render_debug_panel(debug, show_full_debug=False):
    render_supervisor_telemetry(debug)

    st.divider()

    agent = debug.get("agent_telemetry", {})
    render_agent_summary(debug)

    if not agent:
        return

    agent_name = agent.get("agent_name")

    st.divider()

    if agent_name == "SQLAgent":
        render_sql_details(agent)
    elif agent_name == "RAGAgent":
        render_rag_details(agent)
    elif agent_name == "RootCauseAgent":
        render_rootcause_details(agent)
    elif agent_name == "RecommendationAgent":
        render_recommendation_details(agent)

    st.divider()
    render_quality(agent)

    rootcause_chain = debug.get("rootcause_chain")
    if rootcause_chain:
        st.divider()
        with st.expander("Root Cause Chain Details", expanded=False):
            st.json(rootcause_chain)

    if show_full_debug:
        st.divider()
        with st.expander("Full Debug JSON", expanded=False):
            st.json(debug)


# ----------------------------
# Layout
# ----------------------------
if show_debug_panel:
    chat_col, debug_col = st.columns([1.6, 1], gap="large")
else:
    chat_col = st.container()
    debug_col = None


with chat_col:
    st.subheader("Conversation")

    with st.form("question_form", clear_on_submit=False):
        col_input, col_button = st.columns([10, 1])
        with col_input:
            question = st.text_input(
                "Ask a question",
                value=st.session_state.draft_prompt,
                placeholder="Ask about sales, delivery, reviews, sellers, products, or business recommendations",
                label_visibility="collapsed",
            )
        with col_button:
            submitted = st.form_submit_button("Ask", use_container_width=True)

    if submitted and question.strip():
        process_prompt(question.strip())
        st.rerun()

    for convo in reversed(st.session_state.conversations):
        with st.chat_message("user"):
            st.markdown(convo["question"])

        with st.chat_message("assistant"):
            st.markdown(convo["answer"])
            render_agent_tag(convo.get("agent", "Unknown"))

        st.divider()


if show_debug_panel and debug_col is not None:
    with debug_col:
        st.subheader("Observability Panel")
        st.caption("Technical telemetry is separated from the main conversation for a cleaner end-user experience.")

        if st.session_state.last_debug:
            render_debug_panel(
                st.session_state.last_debug,
                show_full_debug=show_full_debug,
            )
        else:
            st.info("Ask a question to see telemetry, SQL details, sources, and diagnostics here.")