from typing import Dict, Any

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
    return vectorstore.similarity_search(question, k=k)


def answer_with_rag(question: str, llm, vectorstore) -> Dict[str, Any]:
    docs = vectorstore.similarity_search(question, k=4)
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
    answer = llm.invoke(prompt).content

    sources = [
        {
            "content_preview": doc.page_content[:200],
            "metadata": doc.metadata
        }
        for doc in docs
    ]

    return {
        "answer": answer,
        "sources": sources
    }