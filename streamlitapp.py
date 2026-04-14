import os
import json
import base64
import hashlib
from io import BytesIO

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI
from requests.exceptions import ChunkedEncodingError, RequestException

load_dotenv()

# API_URL = os.getenv("API_URL", "http://localhost:8000/chat/")
API_URL = os.getenv("API_URL", "https://olist-agent-181066117930.asia-southeast1.run.app/chat/")
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

    .input-help {
        color: #6B7280;
        font-size: 0.82rem;
        margin-top: 0.35rem;
        margin-bottom: 0.75rem;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        min-height: auto !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }

    div[data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    div[data-testid="stFileUploader"] small {
        display: none !important;
    }

    div[data-testid="stFileUploader"] button[kind="secondary"] {
        width: 100% !important;
        min-height: 42px !important;
        height: 42px !important;
        border-radius: 12px !important;
        padding-top: 0.45rem !important;
        padding-bottom: 0.45rem !important;
        white-space: nowrap !important;
    }

    div[data-testid="stFileUploaderFile"] {
        margin-top: 0.35rem;
    }

    div[data-testid="stAudioInput"] {
        min-height: 42px !important;
    }

    div[data-testid="stAudioInput"] > div {
        min-height: 42px !important;
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
        "title": "RAG Agent — Review Semantics & Knowledge",
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
    "Which sellers have the highest average product price?",
    "Which product categories have the highest total item value?",
    "What is the relationship between freight value and product price by seller?",
    "Which sellers are located in São Paulo and what products do they sell?",
]

RAG_SAMPLES = [
    "What are the most common complaint themes in the customer reviews?",
    "Summarize negative reviews about late delivery or products marked delivered but not received.",
    "Translate this review complaint to English and explain the sentiment.",
    "What are the most expensive product categories when combining product price and shipping cost?",
    "What do customers say about products in the 'health beauty' category?",
    "How do customers describe their experience with garden tools products?",
    "What do reviews say about delivery experience for sports and leisure products?",
]

ROOTCAUSE_SAMPLES = [
    "Why are review scores low for some sellers based on order and delivery metrics?",
    "What are the main structured drivers of late deliveries across sellers or categories?",
    "Why do some categories perform worse in review score and delay rate?",
    "What are the likely root causes behind common complaints in product reviews for electronics or accessories?",
]

RECOMMENDATION_SAMPLES = [
    "What should management do to reduce review complaints about late delivery and missing items?",
    "What actions should we prioritize for sellers with poor review sentiment and weak delivery performance?",
    "How can we improve customer satisfaction using both structured KPIs and review feedback?",
    "What should management do about common complaints in product reviews for electronics or accessories?",
]

if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "last_debug" not in st.session_state:
    st.session_state.last_debug = {}
if "question_input_box" not in st.session_state:
    st.session_state.question_input_box = ""
if "pending_input_fill" not in st.session_state:
    st.session_state.pending_input_fill = None
if "pending_input_source" not in st.session_state:
    st.session_state.pending_input_source = None
if "active_input_source" not in st.session_state:
    st.session_state.active_input_source = None
if "focus_input" not in st.session_state:
    st.session_state.focus_input = False
if "clear_input_on_next_run" not in st.session_state:
    st.session_state.clear_input_on_next_run = False
if "voice_error" not in st.session_state:
    st.session_state.voice_error = ""
if "last_audio_signature" not in st.session_state:
    st.session_state.last_audio_signature = None
if "image_error" not in st.session_state:
    st.session_state.image_error = ""
if "last_image_hash" not in st.session_state:
    st.session_state.last_image_hash = None
if "image_uploader_version" not in st.session_state:
    st.session_state.image_uploader_version = 0

def set_prompt(prompt_text: str):
    st.session_state.question_input_box = prompt_text
    st.session_state.active_input_source = None
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

def call_non_stream_api(question, history):
    payload = {"question": question, "history": history}
    response = requests.post(API_URL, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()

def stream_api(question, history):
    payload = {"question": question, "history": history}
    stream_url = API_URL.rstrip("/")
    if stream_url.endswith("/chat"):
        stream_url = stream_url + "/stream/"
    else:
        stream_url = stream_url.replace("/chat/", "/chat/stream/")
    try:
        response = requests.post(stream_url, json=payload, stream=True, timeout=180)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8")
    except (ChunkedEncodingError, RequestException, json.JSONDecodeError):
        fallback = call_non_stream_api(question, history)
        yield json.dumps(
            {
                "type": "done",
                "answer": fallback.get("answer", "No answer returned."),
                "selected_agent": fallback.get("selected_agent", "Unknown"),
                "debug": fallback.get("debug", {}),
            }
        )

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
        "question": st.session_state.get("last_display_question", prompt_text),
        "answer": streamed_text,
        "agent": selected_agent,
        "debug": debug,
    }
    st.session_state.conversations.append(completed_chat)
    st.session_state.last_debug = debug
    st.session_state.clear_input_on_next_run = True
    st.session_state.focus_input = True
    st.session_state.voice_error = ""
    st.session_state.image_error = ""
    st.session_state.active_input_source = None

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

def image_to_data_url(image_file) -> str:
    image_bytes = image_file.getvalue()
    mime_type = getattr(image_file, "type", None) or "image/png"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

def extract_text_from_review_screenshot(image_file) -> str:
    if image_file is None:
        return ""
    if openai_client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    data_url = image_to_data_url(image_file)
    response = openai_client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You extract text from e-commerce complaint or review screenshots. "
                            "Return only the readable text from the screenshot, preserving line breaks where helpful. "
                            "Do not summarize. Do not explain. Do not add labels."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract all complaint/review text from this screenshot."},
                    {"type": "input_image", "image_url": data_url},
                ],
            },
        ],
    )
    return (response.output_text or "").strip()

def build_backend_question(visible_question: str) -> str:
    if st.session_state.active_input_source == "image_review":
        return f'''Analyze the following review text.

Review text:
"""{visible_question}"""

Return:
1. English translation
2. Sentiment analysis based on the English translation

Keep the answer concise and clear.
'''
    return visible_question

def audio_signature(audio_file):
    if audio_file is None:
        return None
    file_name = getattr(audio_file, "name", "audio")
    file_size = len(audio_file.getvalue())
    return f"{file_name}:{file_size}"

def image_signature(image_file):
    if image_file is None:
        return None
    image_bytes = image_file.getvalue()
    return hashlib.sha256(image_bytes).hexdigest()

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
        st.session_state.pending_input_source = "audio"
        st.session_state.voice_error = ""
        st.rerun()
    except Exception as e:
        st.session_state.voice_error = f"Audio transcription failed: {e}"

def process_image_input(image_file):
    if image_file is None:
        return
    signature = image_signature(image_file)
    if signature == st.session_state.last_image_hash:
        return
    try:
        with st.spinner("Extracting text from screenshot..."):
            extracted_text = extract_text_from_review_screenshot(image_file)
        if not extracted_text:
            st.session_state.image_error = "No readable text detected in the screenshot."
            return
        st.session_state.last_image_hash = signature
        st.session_state.pending_input_fill = extracted_text
        st.session_state.pending_input_source = "image_review"
        st.session_state.image_error = ""
        st.session_state.image_uploader_version += 1
        st.rerun()
    except Exception as e:
        st.session_state.image_error = f"Image text extraction failed: {e}"

def render_sidebar_section_header(theme_key: str):
    theme = AGENT_THEME[theme_key]
    st.markdown(
        f'''
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
        ''',
        unsafe_allow_html=True,
    )

def render_agent_tag(agent_name: str):
    if "RootCauseAgent" in agent_name and "RecommendationAgent" in agent_name:
        theme_key = "rootcause_recommendation"
    elif "RecommendationAgent" in agent_name:
        theme_key = "recommendation"
    elif "RootCauseAgent" in agent_name:
        theme_key = "rootcause"
    elif "RAGAgent" in agent_name:
        theme_key = "rag"
    elif "SQLAgent" in agent_name:
        theme_key = "sql"
    else:
        theme_key = None

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
        label = agent_name

    st.markdown(
        f'''
        <div class="agent-tag" style="
            background-color: {bg};
            color: {text};
            border-color: {border};
        ">
            {label}
        </div>
        ''',
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
    retrieval = agent.get("retrieval", {})
    timing_items = {k: v for k, v in timing.items() if k.endswith("_sec") and k != "total_latency_sec"}
    st.subheader("Diagnostic Details")
    if timing_items:
        with st.expander("Diagnostic Query Timings", expanded=False):
            st.json(timing_items)
    if diagnostics:
        with st.expander("Diagnostics Output", expanded=False):
            st.json(diagnostics)
    if retrieval.get("sources"):
        with st.expander("Review Evidence Used", expanded=False):
            st.json(retrieval["sources"])

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

def render_chat_exchange(display_question_text: str, backend_question_text: str):
    st.session_state.last_display_question = display_question_text
    with st.chat_message("user"):
        st.markdown(display_question_text)
    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        status_placeholder = st.empty()
        process_prompt_streaming(
            backend_question_text,
            answer_placeholder=answer_placeholder,
            status_placeholder=status_placeholder,
        )
        render_agent_tag(st.session_state.conversations[-1].get("agent", "Unknown"))
    st.divider()

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
        st.session_state.active_input_source = st.session_state.pending_input_source
        st.session_state.pending_input_fill = None
        st.session_state.pending_input_source = None
        st.session_state.focus_input = True

    input_col, audio_col, image_col = st.columns([6.0, 1.2, 1.5], gap="small")

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
        audio_input = st.audio_input("Record", key="voice_question_input", label_visibility="collapsed")

    with image_col:
        image_input = st.file_uploader(
            "Browse files",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key=f"review_screenshot_input_{st.session_state.image_uploader_version}",
            label_visibility="collapsed",
        )

    st.markdown(
        "<div class='input-help'>Use the mic button for voice input or upload a review screenshot. The extracted text will be inserted into the input box. Press Enter to submit.</div>",
        unsafe_allow_html=True,
    )

    focus_input()

    if audio_input is not None:
        process_audio_input(audio_input)
    if image_input is not None:
        process_image_input(image_input)
    if st.session_state.voice_error:
        st.error(st.session_state.voice_error)
    if st.session_state.image_error:
        st.error(st.session_state.image_error)

    if submitted and question.strip():
        visible_question = question.strip()
        backend_question = build_backend_question(visible_question)
        render_chat_exchange(visible_question, backend_question)
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
