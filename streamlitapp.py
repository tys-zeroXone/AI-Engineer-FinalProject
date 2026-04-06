import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000/chat/")

st.set_page_config(page_title="Olist Multi-Agent Assistant", layout="wide")
st.title("🛒 Olist Commerce Intelligence Copilot")
st.caption("LangGraph-based supervisor routes questions to SQL, RAG, Root Cause, or Recommendation agents.")

with st.sidebar:
    st.subheader("Sample Questions")
    samples = [
        "What are the top 5 product categories by revenue?",
        "How is late delivery defined in this system?",
        "Why are review scores low for some sellers?",
        "What should management do to reduce late deliveries?",
        "Compare seller performance by review score and late delivery rate."
    ]
    for q in samples:
        if st.button(q):
            st.session_state["pending_prompt"] = q


def call_api(question, history):
    payload = {
        "question": question,
        "history": history
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "answer": f"API error: {e}",
            "selected_agent": "N/A",
            "debug": {}
        }


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.session_state.pop("pending_prompt", None)
chat_input = st.chat_input("Ask about sales, delivery, reviews, sellers, products, or business recommendations")

if chat_input:
    prompt = chat_input

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    history = st.session_state.messages[-20:]

    result = call_api(prompt, history)

    answer = result.get("answer", "No answer generated.")
    selected_agent = result.get("selected_agent", "Unknown")
    debug = result.get("debug", {})

    with st.chat_message("assistant"):
        st.markdown(answer)
        st.info(f"Selected Agent: {selected_agent}")

        with st.expander("Debug Details"):
            st.json(debug)

    st.session_state.messages.append({"role": "assistant", "content": answer})