from typing import List, Dict, Any
import time

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from tools.rag_tools import get_vector_store, answer_with_rag


class RAGAgent:
    def __init__(self, qdrant_url: str, qdrant_api_key: str, openai_api_key: str, collection_name: str):
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

        result = answer_with_rag(
            question=question,
            llm=self.llm,
            vectorstore=self.vectorstore
        )

        total_elapsed = time.perf_counter() - agent_start

        return {
            "selected_agent": "RAGAgent",
            "answer": result["answer"],
            "debug": {
                "agent_telemetry": {
                    "agent_name": "RAGAgent",
                    "timing": {
                        "total_latency_sec": round(total_elapsed, 4),
                        **result["telemetry"].get("timing", {})
                    },
                    "tokens": result["telemetry"].get("tokens", {}),
                    "retrieval": {
                        "sources_count": len(result["sources"]),
                        "sources": result["sources"]
                    },
                    "quality": result["telemetry"].get("quality", {})
                }
            }
        }