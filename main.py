import os
import json
import asyncio
import re
from typing import Optional, List, Dict

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from agents.supervisor import SupervisorAgent

load_dotenv()

app = FastAPI(title="Olist Commerce Intelligence Multi-Agent API")

supervisor = SupervisorAgent(
    db_path=os.getenv("SQLITE_DB_PATH"),
    qdrant_url=os.getenv("QDRANT_URL"),
    qdrant_api_key=os.getenv("QDRANT_API_KEY"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
)


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


@app.post("/chat/")
async def chat(request: RequestBody):
    result = supervisor.run(
        question=request.question,
        history=request.history or []
    )
    return result


@app.post("/chat/stream/")
async def chat_stream(request: RequestBody):
    async def event_generator():
        result = supervisor.run(
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

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson"
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
