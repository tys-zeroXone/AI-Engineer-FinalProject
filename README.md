# 🛒 Olist Commerce Intelligence Copilot

### Multi-Agent AI System for E-commerce Analytics, Diagnostics & Decision Support

---

## 🚀 Executive Summary

This project delivers a **production-ready multi-agent AI system** that enables business users to:

* Ask natural language questions about marketplace performance
* Diagnose operational issues (e.g., late delivery, low reviews)
* Receive **data-driven, consulting-style recommendations**

The system integrates:

* **Structured analytics (SQL)**
* **Semantic retrieval (RAG via Qdrant)**
* **Diagnostic reasoning (Root Cause Agent)**
* **Strategic recommendations (LLM-driven)**

All orchestrated through a **Supervisor Agent using LangGraph**.

---

## 🎯 Business Value

| Capability                | Business Impact                         |
| ------------------------- | --------------------------------------- |
| Natural Language Querying | Eliminates dependency on SQL / BI tools |
| Root Cause Analysis       | Faster issue diagnosis                  |
| Recommendation Engine     | Actionable decision support             |
| Multi-Agent Orchestration | Scalable enterprise AI architecture     |

---

## 🎯 Key Objective

Enable stakeholders to ask:

* *“What are the top product categories by revenue?”*
* *“Why are review scores low?”*
* *“What actions should we prioritize?”*

…and receive **end-to-end insights → diagnosis → strategy**

---

## 🧠 System Architecture

```
User (Streamlit UI)
        ↓
FastAPI Backend (/chat, /chat/stream)
        ↓
Supervisor Agent (LangGraph)
        ↓
 ┌────────────┬──────────────┬──────────────┬──────────────┐
 │ SQL Agent  │ RAG Agent     │ Root Cause    │ Recommendation│
 │ (SQLite)   │ (Qdrant)      │ (Diagnostics) │ (Strategy)    │
 └────────────┴──────────────┴──────────────┴──────────────┘
        ↓
Final LLM Response (Streaming)
```

---

## 🧩 Core Components

### 1. Supervisor Agent (Orchestration & Routing)

* Routes user queries to the correct agent
* Supports multi-step reasoning:

  * **Root Cause → Recommendation**
* Built using **LangGraph**

---

### 2. SQL Agent (Structured Analytics)

* Converts natural language → SQL query
* Executes queries on SQLite
* Returns business insights

**Example:**

> “Top 5 product categories by revenue”

---

### 3. RAG Agent (Knowledge Retrieval)

* Uses **Qdrant vector database**
* Retrieves:

  * KPI definitions
  * Business glossary
  * Schema documentation

---

### 4. Root Cause Agent (Diagnostics)

* Executes multiple analytical queries
* Identifies drivers of issues

---

### 5. Recommendation Agent (Strategy Engine)

* Combines:

  * Analytics results
  * Retrieved knowledge
  * LLM reasoning

Outputs:

* Key findings
* Implications
* Prioritized actions
* Executive summary

---

## 🔊 Voice Input Feature (Latest UX)

The system supports **voice-based interaction integrated into the input box**.

### Flow:

```
🎙️ Record → Stop → Transcribe → Auto-fill input → Press Enter → Execute
```

### Implementation:

* `st.audio_input()` (Streamlit)
* OpenAI transcription (`gpt-4o-mini-transcribe`)
* Streamlit session-state lifecycle (safe pattern)

---

## ⚙️ Tech Stack

| Layer            | Technology                    |
| ---------------- | ----------------------------- |
| Frontend         | Streamlit                     |
| Backend          | FastAPI                       |
| Orchestration    | LangGraph                     |
| LLM              | OpenAI (GPT-4o / GPT-4o-mini) |
| Vector DB        | Qdrant                        |
| Database         | SQLite                        |
| Embeddings       | text-embedding-3-small        |
| Containerization | Docker                        |

---

## 📂 Project Structure

```
project/
│
├── agents/
│   ├── sql_agent.py
│   ├── rag_agent.py
│   ├── rootcause_agent.py
│   ├── recommendation_agent.py
│   └── supervisor.py
│
├── tools/
│   ├── db_tools.py
│   ├── analytics_tools.py
│   ├── rag_tools.py
│   └── schema_tools.py
│
├── data/
│   └── Olist_Database.db
│
├── docs/
│   ├── schema_docs.jsonl
│   ├── business_glossary.jsonl
│   └── kpi_docs.jsonl
│
├── setup_qdrant.py
├── main.py                # FastAPI backend
├── streamlitapp.py       # UI (text + voice input)
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🔄 API Endpoints

### Health Check

```
GET /
```

### Standard Chat

```
POST /chat/
```

### Streaming Chat (Primary)

```
POST /chat/stream/
```

Format:

```
application/x-ndjson
```

Supports real-time token streaming 

---

## 🐳 Docker Deployment (Recommended)

```bash
docker-compose up --build
```

Services:

* API → http://localhost:8000
* UI → http://localhost:8501

---

## 🛠️ Local Development Setup

### 1. Install Dependencies

```bash
poetry install
```

or

```bash
pip install -r requirements.txt
```

---

### 2. Environment Variables

Create `.env`:

```env
OPENAI_API_KEY=your_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_key
QDRANT_COLLECTION=olist_docs
SQLITE_DB_PATH=data/Olist_Database.db
API_URL=http://localhost:8000/chat/
```

---

### 3. Initialize Vector Database

```bash
python setup_qdrant.py
```

Loads documents into Qdrant

---

### 4. Run Backend

```bash
uvicorn main:app --reload --port 8000
```

---

### 5. Run Frontend

```bash
streamlit run streamlitapp.py
```

---

## 🧪 Example Queries

### 📊 SQL Agent

* “Top product categories by revenue”
* “Late delivery rate by seller”

### 📚 RAG Agent

* “What is freight ratio?”
* “Explain dataset schema”

### 🔍 Root Cause Agent

* “Why are review scores low?”
* “What drives late deliveries?”

### 🎯 Recommendation Agent

* “How to improve marketplace performance?”
* “What actions should management prioritize?”

---

## 📊 Observability & Telemetry

The system includes a **dedicated Observability Panel**:

Tracked metrics:

* Routing latency
* SQL execution time
* Token usage
* Retrieved documents
* Diagnostic outputs
* Recommendation pipeline

⚠️ Note: Accuracy shown reflects execution quality, not ground-truth evaluation.

---

## 🧠 Design Principles

### ✅ Multi-Agent Modularity

Each agent solves a specific class of problem

### ✅ Hybrid Intelligence

Combines:

* Structured data
* Unstructured knowledge
* LLM reasoning

### ✅ Streaming UX

Real-time response generation

### ✅ Production-Ready Architecture

* API layer separation
* UI layer
* Dockerized deployment
* Environment-driven configuration

---

## ⚠️ Limitations

* No ground-truth evaluation framework
* SQL generation may fail on edge cases
* RAG depends on document quality
* No long-term conversational memory

---

## 🔮 Future Enhancements

* Evaluation framework (accuracy scoring)
* Memory layer (vector conversation memory)
* Role-based UI (business vs technical mode)
* SQL validation & guardrails
* Redis caching layer
* Export to dashboard / slides

---

## 👨‍💻 Authors

**Tyson Sianipar**
**Andre Setiawan**

AI Engineering Final Project

---

## ⭐ Summary

This project demonstrates a **real-world enterprise AI pattern**:

> **Data → Insight → Diagnosis → Recommendation**

Delivered through a **multi-agent architecture with LLM orchestration**

---

⭐ If you find this useful, feel free to star the repo!
