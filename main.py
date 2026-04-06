import os
import uvicorn
from typing import Optional, List, Dict

from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.supervisor import SupervisorAgent

load_dotenv()

app = FastAPI(title="Olist Commerce Intelligence Multi-Agent API")

supervisor = SupervisorAgent(
    db_path=os.getenv("SQLITE_DB_PATH", "data/Olist_Database.db"),
    qdrant_url=os.getenv("QDRANT_URL"),
    qdrant_api_key=os.getenv("QDRANT_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    collection_name=os.getenv("QDRANT_COLLECTION", "olist_docs"),
)


class RequestBody(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = None


@app.get("/")
def root():
    return {"status": "ok", "service": "olist-langgraph-multi-agent"}


@app.post("/chat/")
async def chat(request: RequestBody):
    result = supervisor.run(
        question=request.question,
        history=request.history or []
    )
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)