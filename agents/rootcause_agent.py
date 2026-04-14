from typing import List, Dict, Any
import time

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from tools.analytics_tools import build_root_cause_prompt
from tools.rag_tools import get_vector_store, retrieve_docs_only


class RootCauseAgent:
    def __init__(
        self,
        db_path: str,
        qdrant_url: str,
        qdrant_api_key: str,
        openai_api_key: str,
        collection_name: str,
    ):
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

        prompt, diagnostics, diagnostics_telemetry = build_root_cause_prompt(
            question=question,
            db_path=self.db_path
        )

        rag_pack = retrieve_docs_only(question=question, vectorstore=self.vectorstore, k=4)
        rag_docs = rag_pack["docs"]
        rag_context = "\n\n".join([doc.page_content for doc in rag_docs])

        prompt = f"""{prompt}

Also use the review evidence below when relevant, especially for complaint-heavy, category-specific, seller-specific,
or delivery-experience questions.

Review / Knowledge Evidence:
{rag_context}

Instructions:
- Combine structured diagnostics with review evidence.
- If the question is about complaints, summarize the most repeated complaint themes first.
- Then explain the most likely operational drivers behind those complaint themes.
- Be explicit about what comes from SQL diagnostics versus retrieved review evidence.
- Do not claim certainty when the evidence is only suggestive.
"""

        llm_start = time.perf_counter()
        response = self.llm.invoke(prompt)
        llm_elapsed = time.perf_counter() - llm_start

        usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}
        total_elapsed = time.perf_counter() - agent_start

        return {
            "selected_agent": "RootCauseAgent",
            "answer": response.content,
            "debug": {
                "agent_telemetry": {
                    "agent_name": "RootCauseAgent",
                    "timing": {
                        "total_latency_sec": round(total_elapsed, 4),
                        "rootcause_generation_sec": round(llm_elapsed, 4),
                        **diagnostics_telemetry.get("timing", {}),
                        **rag_pack["telemetry"].get("timing", {}),
                    },
                    "tokens": {
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                    "diagnostics": diagnostics,
                    "retrieval": {
                        "sources_count": len(rag_docs),
                        "sources": [
                            {
                                "content_preview": doc.page_content[:200],
                                "metadata": doc.metadata
                            }
                            for doc in rag_docs
                        ]
                    },
                    "quality": {
                        **diagnostics_telemetry.get("quality", {}),
                        **rag_pack["telemetry"].get("quality", {}),
                        "accuracy_note": "Execution-quality telemetry only. Root-cause correctness remains hypothesis-based and should be business-validated."
                    }
                }
            }
        }
