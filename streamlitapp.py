import os
import json
from io import BytesIO

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/chat/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

st.set_page_config(page_title="Olist Multi-Agent Assistant", layout="wide")

st.markdown(
    """
    <style>
    section.main > div {
        padding-top: 1rem;
    }

    div[data-testid="stForm"] {
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 12px 14px 6px 14px;
        background: #FFFFFF;
    }

    div[data-testid="stFormSubmitButton"] {
        display: none;
    }

    .agent-tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 4px;
        border: 1px solid rgba(0,0,0,0.06);
    }

    .section-label {
        color: #6B7280;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }

    .typing {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #9CA3AF;
        font-size: 0.92rem;
        margin-top: 4px;
    }

    .dot {
        width: 6px;
        height: 6px;
        background-color: #9CA3AF;
        border-radius: 50%;
        animation: blink 1.4s infinite both;
    }

    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes blink {
        0%, 80%, 100% { opacity: 0.2; }
        40% { opacity: 1; }
    }

    .audio-help {
        color: #6B7280;
        font-size: 0.82rem;
        margin-top: 0.35rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛒 Olist Commerce Intelligence Copilot")
st.caption("Ask business questions about sales, delivery, reviews, sellers, products, and recommendations.")


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

if "question_input_box" not in st.session_state:
    st.session_state.question_input_box = ""

if "pending_input_fill" not in st.session_state:
    st.session_state.pending_input_fill = None

if "focus_input" not in st.session_state:
    st.session_state.focus_input = False

if "clear_input_on_next_run" not in st.session_state:
    st.session_state.clear_input_on_next_run = False

if "voice_error" not in st.session_state:
    st.session_state.voice_error = ""

if "last_audio_signature" not in st.session_state:
    st.session_state.last_audio_signature = None


# ----------------------------
# Helpers
# ----------------------------
def set_prompt(prompt_text: str):
    st.session_state.question_input_box = prompt_text
    st.session_state.focus_input = True
    st.rerun()


def focus_input():
    if st.session_state.focus_input:
        components.html(
            """
            <script>
                const doc = window.parent.document;
                const input = doc.querySelector('input[type="text"]');
                if (input) {
                    input.focus();
                    const len = input.value.length;
                    input.setSelectionRange(len, len);
                }
            </script>
            """,
            height=0,
        )
        st.session_state.focus_input = False


def stream_api(question, history):
    payload = {
        "question": question,
        "history": history,
    }

    stream_url = API_URL.rstrip("/")
    if stream_url.endswith("/chat"):
        stream_url = stream_url + "/stream/"
    else:
        stream_url = stream_url.replace("/chat/", "/chat/stream/")

    response = requests.post(
        stream_url,
        json=payload,
        stream=True,
        timeout=180,
    )
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            yield line.decode("utf-8")


def build_history_from_conversations(conversations, max_pairs=10):
    history = []
    for convo in conversations[-max_pairs:]:
        history.append({"role": "user", "content": convo["question"]})
        history.append({"role": "assistant", "content": convo["answer"]})
    return history


def process_prompt_streaming(prompt_text: str, answer_placeholder, status_placeholder):
    history = build_history_from_conversations(st.session_state.conversations, max_pairs=10)

    streamed_text = ""
    selected_agent = "Unknown"
    debug = {}

    try:
        status_placeholder.markdown(
            """
            <div class="typing">
                <span>Generating response</span>
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for chunk in stream_api(prompt_text, history):
            data = json.loads(chunk)

            if data.get("type") == "token":
                streamed_text = data.get("content", "")
                answer_placeholder.markdown(streamed_text + "▌")

            elif data.get("type") == "done":
                streamed_text = data.get("answer", streamed_text)
                selected_agent = data.get("selected_agent", "Unknown")
                debug = data.get("debug", {})
                answer_placeholder.markdown(streamed_text)

        status_placeholder.empty()

    except Exception as e:
        streamed_text = f"API error: {e}"
        selected_agent = "N/A"
        debug = {}
        answer_placeholder.markdown(streamed_text)
        status_placeholder.empty()

    completed_chat = {
        "question": prompt_text,
        "answer": streamed_text,
        "agent": selected_agent,
        "debug": debug,
    }

    st.session_state.conversations.append(completed_chat)
    st.session_state.last_debug = debug
    st.session_state.clear_input_on_next_run = True
    st.session_state.focus_input = True
    st.session_state.voice_error = ""


def transcribe_audio_file(audio_file) -> str:
    if audio_file is None:
        return ""

    if openai_client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    audio_bytes = audio_file.getvalue()
    file_name = getattr(audio_file, "name", "voice_input.wav")

    buffer = BytesIO(audio_bytes)
    buffer.name = file_name

    transcript = openai_client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=buffer,
    )

    return (getattr(transcript, "text", "") or "").strip()


def audio_signature(audio_file):
    if audio_file is None:
        return None

    file_name = getattr(audio_file, "name", "audio")
    file_size = len(audio_file.getvalue())
    return f"{file_name}:{file_size}"


def process_audio_input(audio_file):
    if audio_file is None:
        return

    signature = audio_signature(audio_file)
    if signature == st.session_state.last_audio_signature:
        return

    try:
        transcript_text = transcribe_audio_file(audio_file)

        if not transcript_text:
            st.session_state.voice_error = "No speech detected. Please try again."
            return

        st.session_state.last_audio_signature = signature
        st.session_state.pending_input_fill = transcript_text
        st.session_state.voice_error = ""
        st.rerun()

    except Exception as e:
        st.session_state.voice_error = f"Audio transcription failed: {e}"


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
        <div class="agent-tag" style="
            background-color: {bg};
            color: {text};
            border-color: {border};
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(text: str):
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)


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


def render_debug_panel(debug):
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


def render_chat_exchange(question_text: str):
    with st.chat_message("user"):
        st.markdown(question_text)

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        status_placeholder = st.empty()

        process_prompt_streaming(
            question_text,
            answer_placeholder=answer_placeholder,
            status_placeholder=status_placeholder,
        )

        render_agent_tag(st.session_state.conversations[-1].get("agent", "Unknown"))

    st.divider()


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

    if st.session_state.clear_input_on_next_run:
        st.session_state.question_input_box = ""
        st.session_state.clear_input_on_next_run = False

    if st.session_state.pending_input_fill is not None:
        st.session_state.question_input_box = st.session_state.pending_input_fill
        st.session_state.pending_input_fill = None
        st.session_state.focus_input = True

    input_col, audio_col = st.columns([6.2, 1.35], gap="small")

    with input_col:
        with st.form("question_form", clear_on_submit=False):
            question = st.text_input(
                "Ask a question",
                key="question_input_box",
                placeholder="Ask about sales, delivery, reviews, sellers, products, or business recommendations",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Submit")

    with audio_col:
        audio_input = st.audio_input(
            "Record",
            key="voice_question_input",
            label_visibility="collapsed",
        )

    st.markdown(
        "<div class='audio-help'>Record with the mic button. When you stop recording, the transcript will be inserted into the input box. Press Enter to submit.</div>",
        unsafe_allow_html=True,
    )

    focus_input()

    if audio_input is not None:
        process_audio_input(audio_input)

    if st.session_state.voice_error:
        st.error(st.session_state.voice_error)

    if submitted and question.strip():
        current_prompt = question.strip()
        render_chat_exchange(current_prompt)
        st.rerun()

    if st.session_state.conversations:
        render_section_label("Recent History")

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
            render_debug_panel(st.session_state.last_debug)
        else:
            st.info("Ask a question to see telemetry, SQL details, sources, and diagnostics here.")