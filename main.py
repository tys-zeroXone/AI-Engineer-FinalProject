import os
import json
import asyncio
import re
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Olist Commerce Intelligence Multi-Agent API")

supervisor = None


def get_supervisor():
    global supervisor
    if supervisor is None:
        from agents.supervisor import SupervisorAgent

        supervisor = SupervisorAgent(
            db_path=os.getenv("SQLITE_DB_PATH"),
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
        )
    return supervisor


class RequestBody(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = None


def split_markdown_blocks(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []

    raw_blocks = re.split(r"\n\s*\n", text)
    blocks: List[str] = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()

        bullet_or_numbered = True
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not (
                stripped.startswith(("-", "*", "•"))
                or re.match(r"^\d+\.", stripped)
            ):
                bullet_or_numbered = False
                break

        if bullet_or_numbered:
            blocks.append("\n".join(lines))
        else:
            blocks.append(block)

    return blocks


@app.get("/")
def root():
    return {"status": "ok", "service": "olist-langgraph-multi-agent"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat/")
async def chat(request: RequestBody):
    try:
        sup = get_supervisor()
        result = sup.run(
            question=request.question,
            history=request.history or []
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream/")
async def chat_stream(request: RequestBody):
    async def event_generator():
        try:
            sup = get_supervisor()
            result = sup.run(
                question=request.question,
                history=request.history or []
            )

            full_answer = result.get("answer", "")
            selected_agent = result.get("selected_agent", "Unknown")
            debug = result.get("debug", {})

            blocks = split_markdown_blocks(full_answer)

            if not blocks:
                yield json.dumps({
                    "type": "done",
                    "answer": full_answer,
                    "selected_agent": selected_agent,
                    "debug": debug
                }) + "\n"
                return

            accumulated = ""
            for block in blocks:
                accumulated = f"{accumulated}\n\n{block}".strip()

                yield json.dumps({
                    "type": "token",
                    "content": accumulated
                }) + "\n"

                await asyncio.sleep(0.12)

            yield json.dumps({
                "type": "done",
                "answer": full_answer,
                "selected_agent": selected_agent,
                "debug": debug
            }) + "\n"

        except Exception as e:
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"
    )

@app.get("/debug/db-check")
def debug_db_check():
    db_path = os.getenv("SQLITE_DB_PATH")
    result = {
        "db_path": db_path,
        "exists": False,
        "size": None,
        "first_bytes": None,
    }

    if db_path and os.path.exists(db_path):
        result["exists"] = True
        result["size"] = os.path.getsize(db_path)
        with open(db_path, "rb") as f:
            result["first_bytes"] = f.read(100).decode("utf-8", errors="replace")

    return result
