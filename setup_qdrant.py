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
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

DATA_FILE = "data/reviews_narrative_full.json"

BATCH_SIZE = 50

def load_review_documents(file_path: str):
    docs = []
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    for text in data:
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "doc_id": str(uuid4()),
                    "source": "review"
                }
            )
        )

    return docs

def main():
    documents = load_review_documents(DATA_FILE)
    print(f"Loaded {len(documents)} review documents")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=OPENAI_API_KEY
    )

    qclient = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    collections = [c.name for c in qclient.get_collections().collections]
    if COLLECTION_NAME not in collections:
        print(f"Creating new collection: {COLLECTION_NAME}")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists. Uploading new documents in batches.")

    existing_count = 0
    try:
        existing_count = qclient.count(COLLECTION_NAME).count
        print(f"{existing_count} documents already in collection. Resuming from there.")
    except Exception:
        pass

    for i in range(existing_count, len(documents), BATCH_SIZE):
        batch_docs = documents[i:i+BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1} ({len(batch_docs)} documents)")

        QdrantVectorStore.from_documents(
            documents=batch_docs,
            embedding=embeddings,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            collection_name=COLLECTION_NAME,
                prefer_grpc=True,
        )

    print(f"✅ Collection '{COLLECTION_NAME}' succesfully created")

if __name__ == "__main__":
    main()