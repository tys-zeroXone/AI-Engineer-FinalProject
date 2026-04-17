# Olist Commerce Intelligence Multi-Agent Platform

## 🚀 Executive Summary

Olist Commerce Intelligence Multi-Agent Platform is a production-grade AI analytics application built on the Brazilian Olist e-commerce dataset. The platform combines Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), SQL analytics, and a multi-agent orchestration framework to deliver business insights through a modern REST API and Streamlit web interface.

It is fully containerized with Docker, cloud deployable on Google Cloud Platform (GCP), and designed to demonstrate enterprise AI engineering best practices.

---

# 📘 User Instructions (Quick Start Guide)

## 1. Introduction

This application helps users analyze e-commerce data, customer reviews, seller performance, delivery operations, and business recommendations using natural language.

Users can ask:
- What are the top categories by revenue?
- Why are customer ratings low?
- What are common complaint themes?
- Which sellers have delivery issues?
- What should management improve first?

---

## 2. Main Features

| Agent | Purpose |
|------|---------|
| SQL Agent | Structured analytics from database |
| RAG Agent | Review search & semantic intelligence |
| Root Cause Agent | Diagnose business issues |
| Recommendation Agent | Suggest improvement actions |

Supported Inputs:
- Text
- Voice
- Image Upload (review screenshot)
- Prompt Library

---

## 3. Home Screen Overview

### Main Panel
- Ask questions
- Upload image
- Voice input
- Read AI responses
- View conversation history

### Telemetry Panel
- Selected agent
- Response timing
- SQL preview
- Sources retrieved
- Execution flow

---

## 4. How to Ask Questions

### Text Input
Type question then click Send.

Example:
```text
Top 5 product categories by revenue
```

### Voice Input
Click microphone, speak clearly, then send.

### Image Upload
Upload review screenshot.
System extracts text automatically.

Returns:
- English translation
- Sentiment analysis
- Complaint understanding

---

## 5. Prompt Library

Choose agent category:
- SQL Agent
- RAG Agent
- Root Cause Agent
- Recommendation Agent

Click sample prompt to auto-fill input box.

---

## 6. Example Questions by Agent

### SQL Agent
```text
Top 5 categories by revenue
Average review score by category
Worst sellers by late delivery
```

### RAG Agent
```text
What are common complaint themes?
Summarize negative delivery reviews
What do customers say about electronics?
```

### Root Cause Agent
```text
Why are ratings low for some sellers?
Why do categories underperform?
```

### Recommendation Agent
```text
What should management improve first?
How can we improve customer satisfaction?
```

---

## 7. Understanding Responses

Each response includes:
- AI answer
- Agent label used
- Chat history
- Optional telemetry panel

---

## 8. Telemetry Panel

Displays:
- Route selected
- Total latency
- SQL generated
- Sources used
- Token usage
- Execution timeline

---

## 9. Best Practices

Use specific business questions.

Good:
```text
Top 5 sellers by late delivery rate
```

Better for diagnostics:
```text
Why are electronics reviews low?
```

Better for recommendations:
```text
What should management do to reduce complaints?
```

---

## 10. Troubleshooting

### No Response
- Check internet connection
- Verify backend API running
- Verify cloud deployment active

### Voice Failed
- Allow microphone permission
- Retry recording

### OCR Failed
- Use clearer screenshot image

---

# 🏗️ High Level Architecture

```text
User
 ↓
Streamlit Frontend
 ↓
FastAPI REST API
 ↓
Supervisor Agent
 ├── SQL Agent → SQLite Database
 ├── RAG Agent → Qdrant Vector DB
 ├── Root Cause Agent → SQL + Qdrant
 └── Recommendation Agent → SQL + Qdrant
```

---

# ⚙️ Technology Stack

## Backend
- Python 3.11+
- FastAPI
- LangChain
- LangGraph
- OpenAI API

## Frontend
- Streamlit

## Databases
- SQLite
- Qdrant Cloud

## DevOps
- Docker
- Google Cloud Run

---

# 📂 Project Structure

```text
.
├── main.py
├── streamlitapp.py
├── setup_qdrant.py
├── dockerfile
├── docker-compose.yml
├── requirements.txt
├── agents/
│   ├── supervisor.py
│   ├── sql_agent.py
│   ├── rag_agent.py
│   ├── rootcause_agent.py
│   └── recommendation_agent.py
└── tools/
    ├── db_tools.py
    ├── rag_tools.py
    ├── analytics_tools.py
    └── schema_tools.py
```

---

# 🔐 Environment Variables

```env
OPENAI_API_KEY=your_key
SQLITE_DB_PATH=./Olist_Database.db
QDRANT_URL=https://cluster.qdrant.io
QDRANT_API_KEY=your_key
QDRANT_COLLECTION_NAME=olist_docs
API_URL=http://localhost:8000/chat/
```

---

# 🛠️ Local Setup

## Install
```bash
pip install -r requirements.txt
```

## Run Backend
```bash
uvicorn main:app --reload
```

## Run Frontend
```bash
streamlit run streamlitapp.py
```

---

# 🐳 Docker Deployment

```bash
docker build -t olist-agent .
docker run -p 8000:8000 --env-file .env olist-agent
```

---

# ☁️ Google Cloud Deployment

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/olist-agent

gcloud run deploy olist-agent \
--image gcr.io/PROJECT_ID/olist-agent \
--region asia-southeast1 \
--allow-unauthenticated
```

---

# 📈 Final Project Coverage

| Requirement | Status |
|------------|--------|
| Multi-Agent Architecture | ✅ |
| SQL Analytics | ✅ |
| RAG Search | ✅ |
| Dockerized App | ✅ |
| Cloud Deployment | ✅ |
| Streamlit UI | ✅ |
| Multimodal Inputs | ✅ |
| Production UX/UI | ✅ |

---

# 👨‍💻 Author Note

Built as a final capstone AI Engineering project demonstrating real-world GenAI architecture, cloud deployment, multi-agent orchestration, and business intelligence automation.

