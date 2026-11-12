from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .llm import quick_chat


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    reply: str


app = FastAPI(title="Minimal LLM Bridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    reply = quick_chat(req.prompt)
    return ChatResponse(reply=reply)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

