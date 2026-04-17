import os
import json
import base64
import hashlib
import textwrap
from io import BytesIO

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI
from requests.exceptions import ChunkedEncodingError, RequestException

load_dotenv()

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

    .prompt-group-label {
        color: #6B7280;
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.95rem;
        margin-bottom: 0.45rem;
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

    div[data-testid="stSelectbox"] > div {
        border-radius: 12px;
    }

    div[data-testid="stTextArea"] textarea {
        line-height: 1.35 !important;
        padding-top: 0.55rem !important;
        padding-bottom: 0.55rem !important;
        padding-left: 1.35rem !important;
        padding-right: 3.2rem !important;
        min-height: 56px !important;
        height: 56px !important;
        overflow-y: hidden !important;
        resize: none !important;
        border-radius: 28px !important;
        background: rgba(255,255,255,0.96) !important;
        vertical-align: middle !important;
    }

    div[data-testid="stTextArea"] > div {
        border-radius: 28px !important;
        background: transparent !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
        min-height: 56px !important;
        height: 56px !important;
    }

    div[data-testid="stTextArea"] [data-baseweb="textarea"] {
        border-radius: 28px !important;
        background: rgba(255,255,255,0.96) !important;
    }

    div[data-testid="stTextArea"] [data-testid="InputInstructions"] {
        display: none !important;
    }

    div[data-testid="stTextArea"] small {
        display: none !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: #111827 !important;
        color: #FFFFFF !important;
        border: 1px solid #111827 !important;
        box-shadow: none !important;
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
    min-height: 56px !important;
    height: 56px !important;
    min-width: 56px !important;

    border-radius: 18px !important;
    border: 1px solid #D1D5DB !important;
    background: rgba(255,255,255,0.96) !important;

    font-size: 0 !important;
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    }

    div[data-testid="stFileUploader"] button[kind="secondary"]::after {
        content: "+" !important;
        font-size: 34px !important;
        font-weight: 700 !important;
        color: #111827 !important;

        position: absolute !important;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    div[data-testid="stFileUploaderFile"] {
        margin-top: 0.35rem;
    }

    div[data-testid="stAudioInput"] {
        min-height: 56px !important;
        height: 56px !important;
        width: 100% !important;
    }

    div[data-testid="stAudioInput"] > div {
        min-height: 56px !important;
        height: 56px !important;
        width: 100% !important;
        background: rgba(255,255,255,0.96) !important;
        border-radius: 18px !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    div[data-testid="stAudioInput"] button,
    div[data-testid="stAudioInput"] [role="button"] {
        min-height: 56px !important;
        height: 56px !important;
        background: rgba(255,255,255,0.96) !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-testid="stAudioInput"] * {
        box-sizing: border-box !important;
    }

    div[data-testid="stAudioInput"] span,
    div[data-testid="stAudioInput"] small,
    div[data-testid="stAudioInput"] p {
        font-size: 0 !important;
    }

    div[data-testid="stAudioInput"] [aria-live],
    div[data-testid="stAudioInput"] [data-testid*="time"],
    div[data-testid="stAudioInput"] [data-testid*="counter"] {
        display: none !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #D1D5DB !important;
        border-radius: 16px !important;
        background: #FFFFFF !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
    }

    div[data-testid="stExpander"] details {
        border: none !important;
    }

    div[data-testid="stExpander"] summary {
        padding-top: 0.95rem !important;
        padding-bottom: 0.95rem !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }

    .flow-summary {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 14px;
    }

    .flow-summary-card {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 10px 12px;
    }

    .flow-summary-label {
        font-size: 0.74rem;
        color: #9CA3AF;
        font-weight: 700;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .flow-summary-value {
        font-size: 0.96rem;
        color: #111827;
        font-weight: 700;
        word-break: break-word;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        min-height: 56px !important;
        height: 56px !important;
        border-radius: 18px !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    section[data-testid="stSidebar"] hr {
        margin-top: 0.45rem !important;
        margin-bottom: 0.55rem !important;
    }

    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stSubheader {
        margin-top: 0.10rem !important;
        padding-top: 0 !important;
        margin-bottom: 0.35rem !important;
    }

    section[data-testid="stSidebar"] .element-container {
        margin-bottom: 0.28rem !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<div style="
display:flex;
align-items:center;
gap:14px;
margin-top:-18px;
margin-bottom:22px;
padding-top:0;
">

<div style="
width:52px;
height:52px;
border-radius:14px;
background: linear-gradient(135deg,#0F172A,#1E3A8A);
display:flex;
align-items:center;
justify-content:center;
color:white;
font-size:26px;
font-weight:700;
box-shadow: 0 8px 20px rgba(15,23,42,0.18);
flex-shrink:0;
">
AI
</div>

<div>
<div style="
font-size:2.05rem;
font-weight:800;
color:#111827;
line-height:1.05;
letter-spacing:-0.02em;
margin-bottom:4px;
">
Olist Commerce Intelligence Platform
</div>

<div style="
font-size:0.92rem;
color:#6B7280;
font-weight:600;
">
Enterprise AI Assistant Platform
</div>
</div>

</div>
<hr style="border:none;border-top:1px solid #E5E7EB;margin-top:14px;">
""", unsafe_allow_html=True)

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

SQL_SAMPLES = {
    "Revenue & Value": [
        "What are the top 5 product categories by revenue?",
        "Which product categories have the highest total item value?",
        "What are the most expensive product categories when combining product price and shipping cost?",
    ],
    "Seller Performance": [
        "Compare seller performance by review score and late delivery rate.",
        "Which sellers have the highest average product price?",
        "Which sellers are located in São Paulo and what products do they sell?",
    ],
    "Delivery & Logistics": [
        "What is the late delivery rate by product category?",
        "What is the relationship between freight value and product price by seller?",
    ],
}

RAG_SAMPLES = {
    "Complaint Intelligence": [
        "What are the most common complaint themes in the customer reviews?",
        "Summarize negative reviews about late delivery or products marked delivered but not received.",
    ],
    "Translation & Sentiment": [
        "Translate this review complaint to English and explain the sentiment.",
    ],
    "Category Review Insights": [
        "What do customers say about products in the 'health beauty' category?",
        "How do customers describe their experience with garden tools products?",
        "What do reviews say about delivery experience for sports and leisure products?",
    ],
}

ROOTCAUSE_SAMPLES = {
    "Seller & Score Diagnostics": [
        "Why are review scores low for some sellers based on order and delivery metrics?",
        "Why do some categories perform worse in review score and delay rate?",
    ],
    "Delivery & Review Drivers": [
        "What are the main structured drivers of late deliveries across sellers or categories?",
        "What are the likely root causes behind common complaints in product reviews for electronics or accessories?",
    ],
}

RECOMMENDATION_SAMPLES = {
    "Management Actions": [
        "What should management do to reduce review complaints about late delivery and missing items?",
        "What actions should we prioritize for sellers with poor review sentiment and weak delivery performance?",
    ],
    "Customer Experience Improvement": [
        "How can we improve customer satisfaction using both structured KPIs and review feedback?",
        "What should management do about common complaints in product reviews for electronics or accessories?",
    ],
}

defaults = {
    "conversations": [],
    "last_debug": {},
    "question_input_box": "",
    "pending_input_fill": None,
    "pending_input_source": None,
    "active_input_source": None,
    "focus_input": False,
    "clear_input_on_next_run": False,
    "voice_error": "",
    "last_audio_signature": None,
    "image_error": "",
    "last_image_hash": None,
    "image_uploader_version": 0,
    "selected_sample_prompt": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def set_prompt(prompt_text: str):
    st.session_state.question_input_box = prompt_text
    st.session_state.active_input_source = None
    st.session_state.selected_sample_prompt = prompt_text
    st.session_state.focus_input = True
    st.rerun()

def estimate_textarea_height(text: str) -> int:
    if not text:
        return 56
    wrapped_lines = 0
    for raw_line in text.splitlines() or [""]:
        chunks = textwrap.wrap(raw_line, width=96) or [raw_line]
        wrapped_lines += max(1, len(chunks))
    visible_lines = max(1, wrapped_lines)
    return min(140, max(56, 24 * visible_lines + 16))

def focus_input():
    if st.session_state.focus_input:
        components.html(
            """
            <script>
                const doc = window.parent.document;
                const input = doc.querySelector('textarea, input[type="text"]');
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
        return f"""Analyze the following review text.

Review text:
{visible_question}

Return:
1. English translation
2. Sentiment analysis based on the English translation

Keep the answer concise and clear.
"""
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

def _render_agent_pill(theme_key: str, label_text: str) -> str:
    theme = AGENT_THEME[theme_key]
    return f"""
    <span class="agent-tag" style="
        background-color: {theme['bg']};
        color: {theme['text']};
        border-color: {theme['border']};
        margin-right: 6px;
    ">
        {label_text}
    </span>
    """


def render_agent_tag(agent_name: str):
    if "RootCauseAgent" in agent_name and "RecommendationAgent" in agent_name:
        html = (
            _render_agent_pill("rootcause", AGENT_THEME["rootcause"]["label"])
            + "<span style='color:#9CA3AF;font-weight:700;margin-right:6px;'>→</span>"
            + _render_agent_pill("recommendation", AGENT_THEME["recommendation"]["label"])
        )
    elif "RecommendationAgent" in agent_name:
        html = _render_agent_pill("recommendation", AGENT_THEME["recommendation"]["label"])
    elif "RootCauseAgent" in agent_name:
        html = _render_agent_pill("rootcause", AGENT_THEME["rootcause"]["label"])
    elif "RAGAgent" in agent_name:
        html = _render_agent_pill("rag", AGENT_THEME["rag"]["label"])
    elif "SQLAgent" in agent_name:
        html = _render_agent_pill("sql", AGENT_THEME["sql"]["label"])
    else:
        html = f"""
        <span class="agent-tag" style="
            background-color: #F3F4F6;
            color: #374151;
            border-color: #E5E7EB;
        ">
            {agent_name}
        </span>
        """

    st.markdown(html, unsafe_allow_html=True)


def render_section_label(text: str):
    st.markdown(f"<div class='section-label'>{text}</div>", unsafe_allow_html=True)

def fmt_short(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)

def render_obs_cards(items, cols=2):
    grid_template = "1fr 1fr 1fr" if cols == 3 else "1fr 1fr"

    cards_html = "".join(
        f"""
        <div class="obs-inline-card">
            <div class="obs-inline-label">{label}</div>
            <div class="obs-inline-value">{fmt_short(value)}</div>
        </div>
        """
        for label, value in items
    )

    html = f"""
    <html>
    <head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            overflow: hidden;
        }}

        .obs-inline-grid {{
            display: grid;
            grid-template-columns: {grid_template};
            gap: 14px;
            padding: 0;
            margin: 0;
        }}

        .obs-inline-card {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 14px 16px;
            box-sizing: border-box;
            min-height: 92px;
        }}

        .obs-inline-label {{
            font-size: 0.74rem;
            color: #9CA3AF;
            font-weight: 700;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .obs-inline-value {{
            font-size: 0.96rem;
            color: #111827;
            font-weight: 700;
            line-height: 1.35;
            word-break: break-word;
        }}
    </style>
    </head>
    <body>
        <div class="obs-inline-grid">
            {cards_html}
        </div>
    </body>
    </html>
    """

    row_count = max(1, (len(items) + cols - 1) // cols)
    height = 96 * row_count + 14 * (row_count - 1) + 6
    components.html(html, height=height, scrolling=False)

def render_log_cards(logs):
    if not logs:
        st.info("No analytics query logs available.")
        return

    html_parts = []
    for idx, log in enumerate(logs, start=1):
        query_name = log.get("query_name", f"Query {idx}")
        fields = []

        for key, value in log.items():
            if key == "query_name":
                continue
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            safe_value = value if value not in [None, ""] else "—"

            fields.append(
                f"""
                <div>
                    <div class="obs-log-item-label">{key.replace('_', ' ')}</div>
                    <div class="obs-log-item-value">{safe_value}</div>
                </div>
                """
            )

        html_parts.append(
            f"""
            <div class="obs-log-card">
                <div class="obs-log-title">{query_name}</div>
                <div class="obs-log-grid">
                    {''.join(fields)}
                </div>
            </div>
            """
        )

    html = f"""
    <html>
    <head>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            overflow: hidden;
        }}

        .obs-log-card {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            padding: 12px 14px;
            margin: 0 0 10px 0;
            box-sizing: border-box;
        }}

        .obs-log-card:last-child {{
            margin-bottom: 0;
        }}

        .obs-log-title {{
            font-size: 0.74rem;
            color: #9CA3AF;
            font-weight: 700;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .obs-log-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .obs-log-item-label {{
            font-size: 0.72rem;
            color: #9CA3AF;
            font-weight: 700;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .obs-log-item-value {{
            font-size: 0.9rem;
            color: #111827;
            font-weight: 700;
            line-height: 1.35;
            word-break: break-word;
        }}
    </style>
    </head>
    <body>
        {''.join(html_parts)}
    </body>
    </html>
    """

    total_blocks = max(1, len(logs))
    height = total_blocks * 126 + (total_blocks - 1) * 10 + 4
    components.html(html, height=height, scrolling=False)

def timeline_step(title: str, status: str = "done", desc: str = "", pills=None):
    pills = pills or []
    dot_class = "done" if status == "done" else "active" if status == "active" else "skipped"
    badge_class = dot_class
    badge_label = "Done" if status == "done" else "Active" if status == "active" else "Skipped"

    pills_html = "".join(
        f'<span class="timeline-pill">{p}</span>' for p in pills if p not in [None, "", "—"]
    )

    return f"""
<div class="timeline-step">
    <div class="timeline-rail">
        <div class="timeline-dot {dot_class}"></div>
    </div>
    <div class="timeline-card">
        <div class="timeline-head">
            <div class="timeline-title">{title}</div>
            <div class="timeline-badge {badge_class}">{badge_label}</div>
        </div>
        {f'<div class="timeline-desc">{desc}</div>' if desc else ''}
        {f'<div class="timeline-meta">{pills_html}</div>' if pills_html else ''}
    </div>
</div>
"""

def render_flow_summary(debug):
    sup = debug.get("supervisor_telemetry", {})
    routing = sup.get("routing", {})
    request = sup.get("request", {})
    agent = debug.get("agent_telemetry", {})
    tokens = agent.get("tokens", {}) or {}

    selected_route = str(routing.get("selected_route", "Unknown")).upper()
    agent_name = agent.get("agent_name", "Unknown")
    total_req = fmt_short(request.get("total_request_latency_sec", "N/A"))
    total_tokens = fmt_short(tokens.get("total_tokens", "N/A"))

    st.markdown(
        f"""
        <div class="flow-summary">
            <div class="flow-summary-card">
                <div class="flow-summary-label">Route</div>
                <div class="flow-summary-value">{selected_route}</div>
            </div>
            <div class="flow-summary-card">
                <div class="flow-summary-label">Agent</div>
                <div class="flow-summary-value">{agent_name}</div>
            </div>
            <div class="flow-summary-card">
                <div class="flow-summary-label">Total Request</div>
                <div class="flow-summary-value">{total_req} s</div>
            </div>
            <div class="flow-summary-card">
                <div class="flow-summary-label">Total Tokens</div>
                <div class="flow-summary-value">{total_tokens}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def build_execution_timeline(debug):
    sup = debug.get("supervisor_telemetry", {})
    routing = sup.get("routing", {})
    request = sup.get("request", {})
    agent = debug.get("agent_telemetry", {}) or {}
    agent_name = agent.get("agent_name", "Unknown")
    timing = agent.get("timing", {}) or {}
    query = agent.get("query", {}) or {}
    retrieval = agent.get("retrieval", {}) or {}
    analytics = agent.get("analytics", {}) or {}
    rootcause_chain = debug.get("rootcause_chain")

    route = str(routing.get("selected_route", "")).lower()
    steps = []

    steps.append(
        timeline_step(
            "1. Input received",
            "done",
            "User submits a question from the chat interface.",
            pills=["UI → API", "Text / Audio / Image"],
        )
    )

    steps.append(
        timeline_step(
            "2. Supervisor routing",
            "done",
            f"Supervisor evaluates the question and selects the {route.upper() if route else 'UNKNOWN'} route.",
            pills=[
                f"Route: {route.upper() if route else '—'}",
                f"Routing: {fmt_short(routing.get('routing_latency_sec', 'N/A'))} s",
            ],
        )
    )

    if agent_name == "SQLAgent":
        steps.append(
            timeline_step(
                "3. SQL agent execution",
                "done",
                "Natural language is converted into a SQL query and executed on SQLite.",
                pills=[
                    f"SQL Gen: {fmt_short(timing.get('sql_generation_sec', 'N/A'))} s",
                    f"SQL Exec: {fmt_short(timing.get('sql_execution_sec', 'N/A'))} s",
                ],
            )
        )
        steps.append(
            timeline_step(
                "4. Data evidence",
                "done",
                "Structured result rows are retrieved from the database.",
                pills=[
                    "Source: SQLite",
                    f"Rows: {fmt_short(query.get('row_count', 'N/A'))}",
                ],
            )
        )
        steps.append(
            timeline_step(
                "5. Response formatting",
                "done",
                "LLM formats SQL results into a business-friendly answer.",
                pills=[
                    f"Formatting: {fmt_short(timing.get('answer_formatting_sec', 'N/A'))} s",
                ],
            )
        )
        steps.append(
            timeline_step(
                "6. Response returned",
                "done",
                "Final answer is streamed back to the user.",
                pills=[
                    f"Total: {fmt_short(request.get('total_request_latency_sec', 'N/A'))} s",
                ],
            )
        )

    elif agent_name == "RAGAgent":
        steps.append(
            timeline_step(
                "3. RAG agent execution",
                "done",
                "Question is sent for semantic retrieval and grounded generation.",
                pills=[
                    f"Retrieval: {fmt_short(timing.get('retrieval_sec', 'N/A'))} s",
                    f"Generation: {fmt_short(timing.get('generation_sec', 'N/A'))} s",
                ],
            )
        )
        steps.append(
            timeline_step(
                "4. Knowledge retrieval",
                "done",
                "Relevant review or knowledge documents are retrieved from Qdrant.",
                pills=[
                    "Source: Qdrant",
                    f"Sources: {fmt_short(retrieval.get('sources_count', 'N/A'))}",
                ],
            )
        )
        steps.append(
            timeline_step(
                "5. Response returned",
                "done",
                "Grounded answer is returned to the user.",
                pills=[
                    f"Total: {fmt_short(request.get('total_request_latency_sec', 'N/A'))} s",
                ],
            )
        )

    elif agent_name == "RootCauseAgent":
        steps.append(
            timeline_step(
                "3. Root cause diagnostics",
                "done",
                "System runs structured diagnostics and semantic evidence retrieval.",
                pills=[
                    f"Generation: {fmt_short(timing.get('rootcause_generation_sec', 'N/A'))} s",
                    f"Retrieval: {fmt_short(timing.get('retrieval_sec', 'N/A'))} s",
                ],
            )
        )
        steps.append(
            timeline_step(
                "4. Evidence combination",
                "done",
                "Structured metrics from SQLite are combined with retrieved review evidence from Qdrant.",
                pills=[
                    "Sources: SQLite + Qdrant",
                    f"Retrieved: {fmt_short(retrieval.get('sources_count', 'N/A'))}",
                ],
            )
        )
        if rootcause_chain:
            steps.append(
                timeline_step(
                    "5. Recommendation chaining",
                    "done",
                    "Root cause findings are forwarded into recommendation synthesis.",
                    pills=["Chain: Enabled"],
                )
            )
        steps.append(
            timeline_step(
                "6. Response returned",
                "done",
                "Final diagnostic response is returned to the user.",
                pills=[
                    f"Total: {fmt_short(request.get('total_request_latency_sec', 'N/A'))} s",
                ],
            )
        )

    elif agent_name == "RecommendationAgent":
        steps.append(
            timeline_step(
                "3. Recommendation analysis",
                "done",
                "System gathers analytics context and supporting knowledge for action planning.",
                pills=[
                    f"Generation: {fmt_short(timing.get('recommendation_generation_sec', 'N/A'))} s",
                    f"Retrieval: {fmt_short(timing.get('retrieval_sec', 'N/A'))} s",
                ],
            )
        )
        steps.append(
            timeline_step(
                "4. Evidence gathering",
                "done",
                "Recommendation is supported by analytics queries and retrieved knowledge context.",
                pills=[
                    f"Analytics Queries: {len(analytics.get('query_logs', []))}",
                    f"RAG Docs: {fmt_short(retrieval.get('rag_docs_count', 'N/A'))}",
                ],
            )
        )
        steps.append(
            timeline_step(
                "5. Response returned",
                "done",
                "Prioritized recommendations are returned to the user.",
                pills=[
                    f"Total: {fmt_short(request.get('total_request_latency_sec', 'N/A'))} s",
                ],
            )
        )

    else:
        steps.append(
            timeline_step(
                "3. Agent execution",
                "done",
                "Selected agent processes the request.",
                pills=[f"Agent: {agent_name}"],
            )
        )
        steps.append(
            timeline_step(
                "4. Response returned",
                "done",
                "Answer is returned to the user.",
                pills=[
                    f"Total: {fmt_short(request.get('total_request_latency_sec', 'N/A'))} s",
                ],
            )
        )

    return "".join(steps)

def render_execution_timeline(debug):
    render_flow_summary(debug)
    st.markdown(
        '<div class="section-label" style="margin-bottom:0.75rem;">Execution Flow</div>',
        unsafe_allow_html=True,
    )

    timeline_body = build_execution_timeline(debug)

    timeline_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: transparent;
        }}

        .timeline-wrap {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 14px;
        }}

        .timeline-step {{
            display: grid;
            grid-template-columns: 22px 1fr;
            gap: 12px;
            align-items: start;
        }}

        .timeline-rail {{
            position: relative;
            min-height: 72px;
            display: flex;
            justify-content: center;
        }}

        .timeline-rail::after {{
            content: "";
            position: absolute;
            top: 20px;
            bottom: -14px;
            width: 2px;
            background: #E5E7EB;
            left: 50%;
            transform: translateX(-50%);
        }}

        .timeline-step:last-child .timeline-rail::after {{
            display: none;
        }}

        .timeline-dot {{
            width: 14px;
            height: 14px;
            border-radius: 999px;
            margin-top: 2px;
            border: 2px solid #D1D5DB;
            background: #FFFFFF;
            z-index: 1;
            box-sizing: border-box;
        }}

        .timeline-dot.done {{
            background: #111827;
            border-color: #111827;
        }}

        .timeline-dot.active {{
            background: #2563EB;
            border-color: #2563EB;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.10);
        }}

        .timeline-dot.skipped {{
            background: #F9FAFB;
            border-color: #D1D5DB;
        }}

        .timeline-card {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 12px 14px;
            box-sizing: border-box;
        }}

        .timeline-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            margin-bottom: 6px;
        }}

        .timeline-title {{
            font-size: 0.94rem;
            font-weight: 700;
            color: #111827;
        }}

        .timeline-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            border-radius: 999px;
            padding: 4px 8px;
            border: 1px solid #E5E7EB;
            background: #F9FAFB;
            color: #6B7280;
            white-space: nowrap;
        }}

        .timeline-badge.done {{
            background: #F3F4F6;
            color: #111827;
            border-color: #E5E7EB;
        }}

        .timeline-badge.active {{
            background: #EFF6FF;
            color: #1D4ED8;
            border-color: #BFDBFE;
        }}

        .timeline-badge.skipped {{
            background: #F9FAFB;
            color: #9CA3AF;
            border-color: #E5E7EB;
        }}

        .timeline-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }}

        .timeline-pill {{
            font-size: 0.76rem;
            color: #374151;
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 999px;
            padding: 4px 8px;
        }}

        .timeline-desc {{
            color: #6B7280;
            font-size: 0.82rem;
            line-height: 1.5;
        }}
    </style>
    </head>
    <body>
        <div class="timeline-wrap">
            {timeline_body}
        </div>
    </body>
    </html>
    """

    step_count = timeline_body.count('class="timeline-step"')
    height = max(220, step_count * 120)
    components.html(timeline_html, height=height, scrolling=False)

def render_supervisor_telemetry(debug):
    sup = debug.get("supervisor_telemetry", {})
    routing = sup.get("routing", {})
    tokens = sup.get("tokens", {})
    request = sup.get("request", {})

    with st.expander("Supervisor", expanded=False):
        render_obs_cards([
            ("Selected Route", routing.get("selected_route", "N/A")),
            ("Total Request Latency (s)", request.get("total_request_latency_sec", "N/A")),
            ("Routing Latency (s)", routing.get("routing_latency_sec", "N/A")),
            ("Supervisor Input Tokens", tokens.get("input_tokens", "N/A")),
        ], cols=2)

def render_agent_summary(debug):
    agent = debug.get("agent_telemetry", {})
    if not agent:
        st.info("No agent telemetry available.")
        return

    timing = agent.get("timing", {})
    tokens = agent.get("tokens", {})

    with st.expander(f"Agent Summary — {agent.get('agent_name', 'Unknown')}", expanded=False):
        render_obs_cards([
            ("Total Agent Latency (s)", timing.get("total_latency_sec", "N/A")),
            ("Total Tokens", tokens.get("total_tokens", "N/A")),
            ("Input Tokens", tokens.get("input_tokens", "N/A")),
            ("Output Tokens", tokens.get("output_tokens", "N/A")),
        ], cols=2)

def render_sql_details(agent):
    timing = agent.get("timing", {})
    query = agent.get("query", {})

    with st.expander("SQL Details", expanded=False):
        render_obs_cards([
            ("SQL Generation (s)", timing.get("sql_generation_sec", "N/A")),
            ("SQL Execution (s)", timing.get("sql_execution_sec", "N/A")),
            ("Rows Returned", query.get("row_count", "N/A")),
            ("Answer Formatting (s)", timing.get("answer_formatting_sec", "N/A")),
        ], cols=2)

    if query.get("sql_query"):
        with st.expander("Generated SQL Query", expanded=False):
            st.code(query["sql_query"], language="sql")

    if query.get("preview"):
        with st.expander("Query Result Preview", expanded=False):
            st.dataframe(query["preview"], use_container_width=True)

def render_rag_details(agent):
    timing = agent.get("timing", {})
    retrieval = agent.get("retrieval", {})

    with st.expander("Knowledge Retrieval Details", expanded=False):
        render_obs_cards([
            ("Retrieval Time (s)", timing.get("retrieval_sec", "N/A")),
            ("Sources Retrieved", retrieval.get("sources_count", "N/A")),
            ("Generation Time (s)", timing.get("generation_sec", "N/A")),
            ("Status", agent.get("quality", {}).get("status", "N/A")),
        ], cols=2)

    sources = retrieval.get("sources", [])
    if sources:
        with st.expander("Retrieved Sources", expanded=False):
            st.json(sources)

def render_rootcause_details(agent):
    timing = agent.get("timing", {})
    diagnostics = agent.get("diagnostics", {})
    retrieval = agent.get("retrieval", {})
    quality = agent.get("quality", {})

    with st.expander("Diagnostic Details", expanded=False):
        render_obs_cards([
            ("Root Cause Generation (s)", timing.get("rootcause_generation_sec", "N/A")),
            ("Retrieval Time (s)", timing.get("retrieval_sec", "N/A")),
            ("Sources Retrieved", retrieval.get("sources_count", "N/A")),
            ("Successful Diagnostic Queries", quality.get("diagnostic_queries_succeeded", "N/A")),
        ], cols=2)

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

    with st.expander("Recommendation Details", expanded=False):
        render_obs_cards([
            ("Retrieval Time (s)", timing.get("retrieval_sec", "N/A")),
            ("Recommendation Generation (s)", timing.get("recommendation_generation_sec", "N/A")),
            ("RAG Docs Count", retrieval.get("rag_docs_count", "N/A")),
            ("Analytics Queries", len(analytics.get("query_logs", []))),
        ], cols=2)

    if analytics.get("query_logs"):
        with st.expander("Analytics Query Logs", expanded=False):
            render_log_cards(analytics["query_logs"])

    if retrieval.get("sources_preview"):
        with st.expander("Knowledge Sources Preview", expanded=False):
            st.json(retrieval["sources_preview"])

def render_quality(agent):
    quality = agent.get("quality", {})
    note = quality.get("accuracy_note", "No explicit quality note available.")

    with st.expander("Quality Note", expanded=False):
        st.write(note)

def render_debug_panel(debug):
    with st.expander("Execution Flow", expanded=False):
        render_execution_timeline(debug)

    render_supervisor_telemetry(debug)

    agent = debug.get("agent_telemetry", {})
    render_agent_summary(debug)
    if not agent:
        return

    agent_name = agent.get("agent_name")
    if agent_name == "SQLAgent":
        render_sql_details(agent)
    elif agent_name == "RAGAgent":
        render_rag_details(agent)
    elif agent_name == "RootCauseAgent":
        render_rootcause_details(agent)
    elif agent_name == "RecommendationAgent":
        render_recommendation_details(agent)

    render_quality(agent)

    rootcause_chain = debug.get("rootcause_chain")
    if rootcause_chain:
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
    st.caption("Choose an agent to test, then pick one of its sample prompts.")

    agent_options = {
        "SQL Agent": {
            "theme_key": "sql",
            "prompts": SQL_SAMPLES,
            "button_prefix": "sql",
            "helper": "Best for structured analytics, aggregations, rankings, and KPI questions.",
        },
        "RAG Agent": {
            "theme_key": "rag",
            "prompts": RAG_SAMPLES,
            "button_prefix": "rag",
            "helper": "Best for review semantics, customer feedback themes, and narrative evidence.",
        },
        "Root Cause Agent": {
            "theme_key": "rootcause",
            "prompts": ROOTCAUSE_SAMPLES,
            "button_prefix": "root",
            "helper": "Best for diagnosing likely drivers behind complaints, delays, or weak performance.",
        },
        "Recommendation Agent": {
            "theme_key": "recommendation",
            "prompts": RECOMMENDATION_SAMPLES,
            "button_prefix": "rec",
            "helper": "Best for actions, prioritization, and management recommendations.",
        },
    }

    selected_agent_label = st.selectbox(
        "Select agent to test",
        options=list(agent_options.keys()),
        index=0,
    )

    selected_agent_config = agent_options[selected_agent_label]

    render_sidebar_section_header(selected_agent_config["theme_key"])
    st.caption(selected_agent_config["helper"])

    st.markdown(
        """
        <div style="
            margin-top: 0.35rem;
            margin-bottom: 0.75rem;
            padding: 0.8rem 0.9rem;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: rgba(255,255,255,0.55);
        ">
            <div style="
                color: #6B7280;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.45rem;
            ">
                Sample prompts
            </div>
            <div style="color: #4B5563; font-size: 0.9rem;">
                Select one prompt below to auto-fill the input box.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    prompt_index = 1
    for group_name, grouped_prompts in selected_agent_config["prompts"].items():
        st.markdown(
            f"<div class='prompt-group-label'>{group_name}</div>",
            unsafe_allow_html=True,
        )
        for q in grouped_prompts:
            is_selected_prompt = st.session_state.selected_sample_prompt == q
            if st.button(
                q,
                key=f'{selected_agent_config["button_prefix"]}_{prompt_index}',
                use_container_width=True,
                type="primary" if is_selected_prompt else "secondary",
            ):
                set_prompt(q)
            prompt_index += 1

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

    input_col, audio_col, image_col, submit_col = st.columns([6.2, 1.7, 0.9, 1.0], gap="small")

    with input_col:
        current_input = st.session_state.get("question_input_box", "")
        question = st.text_area(
            "Ask a question",
            key="question_input_box",
            placeholder="Ask anything",
            label_visibility="collapsed",
            height=estimate_textarea_height(current_input),
        )

    with audio_col:
        audio_input = st.audio_input("Record", key="voice_question_input", label_visibility="collapsed")

    with image_col:
        image_input = st.file_uploader(
            "+",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key=f"review_screenshot_input_{st.session_state.image_uploader_version}",
            label_visibility="collapsed",
        )

    with submit_col:
        submitted = st.button("➤", key="send_prompt_button", use_container_width=True, type="primary")

    st.markdown(
        "<div class='input-help'>Type your question, use the mic to record, or click + to upload an image.</div>",
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
