from typing import List, Dict, Any

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
        analytics_context = build_recommendation_context(question=question, db_path=self.db_path)
        rag_docs = retrieve_docs_only(question=question, vectorstore=self.vectorstore, k=4)

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
        answer = self.llm.invoke(prompt).content

        return {
            "selected_agent": "RecommendationAgent",
            "answer": answer,
            "debug": {
                "analytics_context": analytics_context[:3000],
                "rag_docs_count": len(rag_docs),
            }
        }