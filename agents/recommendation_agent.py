from typing import List, Dict, Any
import time

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from tools.analytics_tools import build_recommendation_context
from tools.rag_tools import get_vector_store, retrieve_docs_only


class RecommendationAgent:
    def __init__(self, db_path: str, qdrant_url: str, qdrant_api_key: str, openai_api_key: str, collection_name: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai_api_key
        )
        self.vectorstore = get_vector_store(
            embeddings=self.embeddings,
            collection_name=collection_name,
            qdrant_url=qdrant_url,
            qdrant_api_key=qdrant_api_key
        )

    def run(self, question: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        agent_start = time.perf_counter()

        analytics_pack = build_recommendation_context(question=question, db_path=self.db_path)
        analytics_context = analytics_pack["context"]

        rag_pack = retrieve_docs_only(question=question, vectorstore=self.vectorstore, k=4)
        rag_docs = rag_pack["docs"]
        rag_context = "\n\n".join([doc.page_content for doc in rag_docs])

        prompt = f"""
You are a commerce strategy assistant.

Use the business analytics context and supporting knowledge context below to answer the user's question.
Provide:
1. Key findings
2. Likely implications
3. Prioritized recommendations
4. Short executive summary

User Question:
{question}

Analytics Context:
{analytics_context}

Knowledge Context:
{rag_context}
"""
        llm_start = time.perf_counter()
        response = self.llm.invoke(prompt)
        llm_elapsed = time.perf_counter() - llm_start

        usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}
        total_elapsed = time.perf_counter() - agent_start

        return {
            "selected_agent": "RecommendationAgent",
            "answer": response.content,
            "debug": {
                "agent_telemetry": {
                    "agent_name": "RecommendationAgent",
                    "timing": {
                        "total_latency_sec": round(total_elapsed, 4),
                        "recommendation_generation_sec": round(llm_elapsed, 4),
                        **analytics_pack["telemetry"].get("timing", {}),
                        **rag_pack["telemetry"].get("timing", {})
                    },
                    "tokens": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "analytics": {
                        "query_logs": analytics_pack["query_logs"],
                        "analytics_context_preview": analytics_context[:3000],
                    },
                    "retrieval": {
                        "rag_docs_count": len(rag_docs),
                        "sources_preview": [
                            {
                                "content_preview": doc.page_content[:200],
                                "metadata": doc.metadata
                            }
                            for doc in rag_docs
                        ]
                    },
                    "quality": {
                        **analytics_pack["telemetry"].get("quality", {}),
                        **rag_pack["telemetry"].get("quality", {}),
                        "accuracy_note": "Execution-quality telemetry only. Recommendation quality should be validated by business review."
                    }
                }
            }
        }