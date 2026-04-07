# 🛒 Olist Commerce Intelligence Copilot

**Multi-Agent AI System for E-commerce Analytics & Decision Support**

---

## 📌 Overview

This project implements a **multi-agent AI system** designed to help business users analyze, diagnose, and improve e-commerce marketplace performance.

It combines:

* **Structured analytics (SQL)**
* **Knowledge retrieval (RAG)**
* **Diagnostic reasoning (Root Cause)**
* **Strategic recommendations (Consulting-style AI)**

All orchestrated using a **Supervisor Agent (LangGraph)**.

---

## 🎯 Key Objective

Enable business stakeholders to ask natural language questions like:

* *“What are the top product categories by revenue?”*
* *“Why are review scores low?”*
* *“What actions should we prioritize?”*

…and receive **data-driven insights and recommendations**.

---

## 🧠 System Architecture

```
User (Streamlit UI)
        ↓
FastAPI Backend (/chat)
        ↓
Supervisor Agent (LangGraph)
        ↓
 ┌────────────┬──────────────┬──────────────┬──────────────┐
 │ SQL Agent  │ RAG Agent     │ Root Cause    │ Recommendation│
 │ (SQLite)   │ (Qdrant)      │ (Diagnostics) │ (Strategy)    │
 └────────────┴──────────────┴──────────────┴──────────────┘
        ↓
Final LLM Response
```

---

## 🧩 Core Components

### 1. Supervisor Agent (Orchestration)

* Routes user queries to the appropriate agent
* Supports multi-step flow:

  * **Root Cause → Recommendation**

---

### 2. SQL Agent (Structured Analytics)

* Converts natural language → SQL query
* Executes query on SQLite database
* Returns business insights

**Example:**

> “Top 5 categories by revenue”

---

### 3. RAG Agent (Knowledge Retrieval)

* Uses **Qdrant vector database**
* Retrieves business definitions & documentation
* Answers conceptual questions

**Example:**

> “What is late delivery?”

---

### 4. Root Cause Agent (Diagnostics)

* Runs multiple analytical queries
* Identifies drivers of business issues

**Example:**

> “Why are review scores low?”

---

### 5. Recommendation Agent (Strategy Engine)

* Combines:

  * Analytics context
  * Retrieved knowledge
  * LLM reasoning

Outputs:

* Key findings
* Implications
* Prioritized actions
* Executive summary

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
├── main.py (FastAPI)
├── streamlitapp.py
├── docker-compose.yaml
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone <repo-url>
cd <project-folder>
```

---

### 2. Setup Environment

Create `.env` file:

```env
OPENAI_API_KEY=your_api_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
DB_PATH=data/Olist_Database.db
```

---

### 3. Install Dependencies

```bash
poetry install
```

or

```bash
pip install -r requirements.txt
```

---

### 4. Setup Vector Database (Qdrant)

```bash
poetry run python setup_qdrant.py
```

This will:

* Load documents from `/docs`
* Generate embeddings
* Store into Qdrant collection

---

### 5. Run Backend (FastAPI)

```bash
poetry run uvicorn main:app --reload --port 8000
```

---

### 6. Run Frontend (Streamlit)

```bash
streamlit run streamlitapp.py
```

---

## 🐳 Docker Setup (Recommended)

```bash
docker-compose up --build
```

Services:

* FastAPI → `localhost:8000`
* Streamlit → `localhost:8501`

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

The system includes a dedicated **Observability Panel**:

### Metrics tracked:

* Latency (routing, execution, total)
* Token usage (input/output)
* SQL query & execution time
* Retrieved documents
* Diagnostic queries
* Recommendation pipeline

⚠️ Note:
“Accuracy” shown is **execution quality**, not ground-truth correctness.

---

## 🧠 Key Design Highlights

### ✅ Multi-Agent Architecture

* Specialized agents for different problem types

### ✅ Hybrid Intelligence

* Structured + Unstructured + LLM reasoning

### ✅ Chain-of-Reasoning Flow

* Root Cause → Recommendation

### ✅ Production-Ready Design

* API layer
* UI layer
* Containerization
* Observability

---

## ⚠️ Limitations

* No ground-truth accuracy evaluation
* SQL generation may fail for edge queries
* RAG depends on document quality
* No long-term memory / session learning

---

## 🔮 Future Improvements

* Add evaluation framework (accuracy scoring)
* Implement conversation memory (vector memory)
* Add role-based UI (Business vs Technical mode)
* Improve SQL validation & safety
* Add caching layer (Redis)
* Add dashboard export (PDF / slides)

---

## 👨‍💻 Author

Collaboration By: Andre Setiawan & Tyson Sianipar
AI Engineering Final Project

---

## 📌 Summary

This project demonstrates a **real-world enterprise AI pattern**:

> From data → insight → diagnosis → recommendation
> delivered through a **multi-agent system**

---

⭐ If you find this useful, feel free to star the repo!
