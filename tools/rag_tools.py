from typing import Dict, Any
import time

from langchain_qdrant import QdrantVectorStore


def get_vector_store(embeddings, collection_name: str, qdrant_url: str, qdrant_api_key: str):
    return QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=collection_name,
        url=qdrant_url,
        api_key=qdrant_api_key,
        check_compatibility=False,
    )


def retrieve_docs_only(question: str, vectorstore, k: int = 4):
    start = time.perf_counter()
    docs = vectorstore.similarity_search(question, k=k)
    elapsed = time.perf_counter() - start
    return {
        "docs": docs,
        "telemetry": {
            "timing": {
                "retrieval_sec": round(elapsed, 4)
            },
            "quality": {
                "status": "success",
                "docs_retrieved": len(docs)
            }
        }
    }


def answer_with_rag(question: str, llm, vectorstore) -> Dict[str, Any]:
    retrieval = retrieve_docs_only(question, vectorstore, k=4)
    docs = retrieval["docs"]
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are a helpful e-commerce analytics knowledge assistant.

Answer the user's question only using the context below.
If the context is insufficient, say that clearly.

User Question:
{question}

Context:
{context}
"""
    start = time.perf_counter()
    response = llm.invoke(prompt)
    elapsed = time.perf_counter() - start

    usage = getattr(response, "response_metadata", {}).get("token_usage", {}) or {}

    sources = [
        {
            "content_preview": doc.page_content[:200],
            "metadata": doc.metadata
        }
        for doc in docs
    ]

    return {
        "answer": response.content,
        "sources": sources,
        "telemetry": {
            "timing": {
                **retrieval["telemetry"].get("timing", {}),
                "generation_sec": round(elapsed, 4),
            },
            "tokens": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            "quality": {
                "status": "success",
                "docs_retrieved": len(docs),
                "has_sources": len(sources) > 0,
                "accuracy_note": "Execution-quality telemetry only. RAG accuracy needs benchmark evaluation."
            }
        }
    }