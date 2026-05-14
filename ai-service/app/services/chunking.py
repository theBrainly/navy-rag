"""Chunking engine (PRD Module F)."""
from __future__ import annotations

from app.config import settings


def chunk_text(text: str, size: int | None = None, overlap: int | None = None) -> list[str]:
    """Split text into overlapping character windows, preferring paragraph and
    sentence boundaries so chunks stay coherent."""
    size = size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            # back off to the nearest boundary for a cleaner cut
            window = text[start:end]
            for sep in ("\n\n", "\n", ". ", " "):
                idx = window.rfind(sep)
                if idx > size * 0.5:
                    end = start + idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks
