# 🛒 Olist Commerce Intelligence Copilot

## Multi-Agent Generative AI System using LangGraph, FastAPI, and Qdrant

---

# 1. Overview

This project implements a **Multi-Agent Generative AI system** designed to analyze and generate insights from e-commerce data using the **Olist dataset**.

The system integrates:

* **Large Language Models (LLM)** for reasoning and natural language interaction
* **LangGraph** for multi-agent orchestration
* **FastAPI** as a backend REST API
* **Qdrant** as a vector database for Retrieval-Augmented Generation (RAG)
* **SQLite** as a structured analytics database
* **Streamlit** for interactive user interface
* **Docker + GCP** for deployment

---

# 2. Objectives

The goal of this project is to:

* Build a **multi-agent AI system**
* Enable **natural language querying over structured + unstructured data**
* Demonstrate:

  * Text-to-SQL analytics
  * Knowledge retrieval (RAG)
  * Root cause analysis
  * Recommendation generation
* Deploy as:

  * **REST API (FastAPI)**
  * **Interactive UI (Streamlit)**
  * **Dockerized cloud-ready application**

---

# 3. System Architecture

## 🔹 High-Level Flow

```
User → Streamlit UI → FastAPI → LangGraph Supervisor → Agents → Response
```

## 🔹 Core Components

| Layer           | Component    | Description                         |
| --------------- | ------------ | ----------------------------------- |
| Frontend        | Streamlit    | Chat interface for user interaction |
| Backend         | FastAPI      | REST API handling requests          |
| Orchestration   | LangGraph    | Multi-agent workflow engine         |
| LLM             | OpenAI GPT   | Reasoning & generation              |
| Structured Data | SQLite       | Olist database                      |
| Vector DB       | Qdrant       | Knowledge retrieval                 |
| Deployment      | Docker + GCP | Cloud hosting                       |

---

# 4. Multi-Agent Architecture

## Supervisor Agent (LangGraph)

* Routes user queries to appropriate agents
* Uses LLM-based intent classification
* Supports multi-step execution

### Routing Logic

| Intent                      | Agent                |
| --------------------------- | -------------------- |
| KPI / metrics / aggregation | SQL Agent            |
| Definitions / schema        | RAG Agent            |
| "Why" / diagnosis           | Root Cause Agent     |
| "What should we do"         | Recommendation Agent |

---

## 4.1 SQL Agent (Text-to-SQL)

### Purpose

* Query structured data using natural language

### Capabilities

* Revenue analysis
* Delivery performance
* Customer metrics
* Seller rankings

### Example

> "Top 5 product categories by revenue"

---

## 4.2 RAG Agent (Knowledge Retrieval)

### Purpose

* Answer conceptual and schema-related questions

### Data Sources

* Schema documentation
* KPI definitions
* Business glossary

### Example

> "What is late delivery?"

---

## 4.3 Root Cause Agent

### Purpose

* Diagnose issues and identify drivers

### Example

> "Why are review scores low?"

### Analysis Includes

* Delivery delays
* Freight ratio
* Seller performance
* Category patterns

---

## 4.4 Recommendation Agent

### Purpose

* Generate business actions from insights

### Example

> "How to reduce late deliveries?"

### Output

* Action plan
* Prioritized recommendations
* Executive summary

---

## 4.5 LangGraph Flow

### Standard Flow

```
Router → Agent → END
```

### Advanced Flow

```
Router → RootCause → Recommendation → END
```

---

# 5. Data Architecture

## Database: SQLite (Olist)

### Key Tables

| Table         | Description                        |
| ------------- | ---------------------------------- |
| orders        | Order lifecycle & delivery metrics |
| order_items   | Revenue & logistics                |
| review_orders | Customer satisfaction              |
| payment_order | Payment behavior                   |
| products      | Product metadata                   |
| sellers       | Seller info                        |
| customers     | Customer segmentation              |

---

## Vector Database: Qdrant

Used for:

* Schema understanding
* KPI definitions
* Business glossary
* Analytical context

---

# 6. Tech Stack

## Backend

* FastAPI
* LangChain
* LangGraph

## AI / LLM

* OpenAI GPT-4o
* OpenAI Embeddings

## Data

* SQLite
* Pandas

## Vector DB

* Qdrant

## Frontend

* Streamlit

## DevOps

* Docker
* Docker Compose
* Google Cloud Platform (GCP)

---

# 7. Installation & Setup

## 7.1 Clone Repository

```bash
git clone <repo_url>
cd project
```

---

## 7.2 Create `.env`

```env
OPENAI_API_KEY=your_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
SQLITE_DB_PATH=data/Olist_Database.db
```

---

## 7.3 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 7.4 Initialize Vector Database

```bash
python setup_qdrant.py
```

---

## 7.5 Run Backend

```bash
uvicorn main:app --reload
```

---

## 7.6 Run Frontend

```bash
streamlit run streamlitapp.py
```

---

# 8. Docker Deployment

## Build & Run

```bash
docker compose up --build
```

## Access

* API → `http://localhost:8000`
* UI → `http://localhost:8501`

---

# 9. GCP Deployment

## Recommended Setup

| Component        | Service                    |
| ---------------- | -------------------------- |
| Backend + Agents | Cloud Run / Compute Engine |
| Vector DB        | Managed Qdrant             |
| LLM              | OpenAI API                 |

---

# 10. API Specification

## POST `/chat/`

### Request

```json
{
  "question": "Why are deliveries late?",
  "history": []
}
```

### Response

```json
{
  "answer": "...",
  "selected_agent": "RootCauseAgent",
  "debug": {}
}
```

---

# 11. Example Use Cases

### 1. Sales Analysis

> "Top categories by revenue"

### 2. Delivery Performance

> "Late delivery rate"

### 3. Customer Insights

> "Average review score"

### 4. Root Cause

> "Why are reviews low?"

### 5. Recommendations

> "How to improve delivery performance?"

---

# 12. Sample Demo Flow

1. Ask KPI question → SQL Agent
2. Ask definition → RAG Agent
3. Ask "why" → Root Cause
4. Ask strategy → Recommendation

---

# 13. Key Features

* Multi-agent orchestration
* Hybrid data access (SQL + RAG)
* Root cause analysis
* Business recommendation engine
* Cloud-ready deployment

---

# 14. Limitations

* LLM may generate imperfect SQL
* Depends on OpenAI API latency
* SQLite not scalable for large datasets
* RAG quality depends on document quality

---

# 15. Future Improvements

* Add SQL validation & retry
* Add dashboard visualizations
* Use BigQuery instead of SQLite
* Add caching layer
* Add user authentication
* Improve agent memory

---

# 16. Conclusion

This project demonstrates a **real-world multi-agent AI system** that:

* Translates natural language → data insights
* Combines structured + unstructured data
* Performs reasoning, diagnosis, and recommendation
* Deploys as a scalable cloud service

---

# 17. Executive Summary

> This system transforms natural language into actionable business insights using a multi-agent AI architecture powered by LangGraph, combining SQL analytics, knowledge retrieval, and intelligent reasoning into a unified decision-support platform.

---

# 18. Author

**Collaboration: Andre Setiawan & Tyson Sianipar**
AI Engineering Bootcamp – Final Project

---

# License

MIT License
