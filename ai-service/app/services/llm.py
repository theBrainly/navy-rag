"""LLM answer generation (PRD Module I).

Default provider is an *extractive fallback* that needs no API key or model: it
composes an answer from the retrieved chunks. This keeps the platform fully
functional offline and in air-gapped mode. openai/ollama providers are wired in
for richer generation when configured.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models import ScoredChunk

_SYSTEM = (
    "You are a defense-logistics knowledge assistant. Answer ONLY from the "
    "provided context. If the answer is not in the context, say you cannot find "
    "it. Always be concise and factual."
)


def _build_context(chunks: list[ScoredChunk]) -> str:
    return "\n\n".join(
        f"[Source: {c.title}, page {c.page_number}]\n{c.text}" for c in chunks
    )


def generate_answer(question: str, chunks: list[ScoredChunk]) -> str:
    if not chunks:
        return "I cannot find that information in the knowledge base."
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return _openai(question, chunks)
    if settings.llm_provider == "ollama":
        return _ollama(question, chunks)
    return _extractive(question, chunks)


def _extractive(question: str, chunks: list[ScoredChunk]) -> str:
    top = chunks[0]
    summary = top.text.strip()
    if len(summary) > 400:
        summary = summary[:400].rsplit(" ", 1)[0] + "…"
    return summary


def _openai(question: str, chunks: list[ScoredChunk]) -> str:
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": _SYSTEM},
            {"role": "user",
             "content": f"Context:\n{_build_context(chunks)}\n\nQuestion: {question}"},
        ],
        "temperature": 0.0,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    try:
        r = httpx.post("https://api.openai.com/v1/chat/completions",
                       json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return _extractive(question, chunks)


def _ollama(question: str, chunks: list[ScoredChunk]) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": f"{_SYSTEM}\n\nContext:\n{_build_context(chunks)}\n\n"
                  f"Question: {question}\nAnswer:",
        "stream": False,
    }
    try:
        r = httpx.post(f"{settings.ollama_url}/api/generate", json=payload, timeout=60)
        r.raise_for_status()
        return r.json().get("response", "").strip() or _extractive(question, chunks)
    except Exception:
        return _extractive(question, chunks)
