from typing import List, Dict, Any

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
        result = answer_with_rag(
            question=question,
            llm=self.llm,
            vectorstore=self.vectorstore
        )
        return {
            "selected_agent": "RAGAgent",
            "answer": result["answer"],
            "debug": {
                "sources": result["sources"]
            }
        }