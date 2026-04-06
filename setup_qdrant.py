import os
import json
from uuid import uuid4
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "olist_docs")

DOC_FILES = [
    "docs/schema_docs.jsonl",
    "docs/business_glossary.jsonl",
    "docs/kpi_docs.jsonl",
]


def load_jsonl_documents(file_path: str):
    docs = []
    path = Path(file_path)
    if not path.exists():
        print(f"Skipping missing file: {file_path}")
        return docs

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            row = json.loads(line.strip())
            content = row.get("content", "")
            metadata = row.get("metadata", {})
            metadata["doc_id"] = str(uuid4())
            docs.append(Document(page_content=content, metadata=metadata))
    return docs


def main():
    all_docs = []
    for file_path in DOC_FILES:
        all_docs.extend(load_jsonl_documents(file_path))

    print(f"Loaded {len(all_docs)} documents")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )

    qclient = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    collections = [c.name for c in qclient.get_collections().collections]

    if COLLECTION_NAME in collections:
        qclient.delete_collection(collection_name=COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")

    QdrantVectorStore.from_documents(
        documents=all_docs,
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=True,
        collection_name=COLLECTION_NAME,
    )

    print(f"Qdrant collection '{COLLECTION_NAME}' created successfully.")


if __name__ == "__main__":
    main()