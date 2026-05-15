"""Embedding engine (PRD Module G).

Default is a dependency-free deterministic *hashing* embedding so the service runs
offline with no model download. Swap to sentence-transformers by setting
EMBEDDING_MODEL=sentence-transformers (and installing the package).
"""
from __future__ import annotations

import math
import re

from app.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbedder:
    """Hashed bag-of-words projected into a fixed-dimension unit vector.

    This is not semantically rich like a transformer, but it is deterministic,
    fast, dependency-free, and good enough to demonstrate the full RAG pipeline
    and to keep keyword overlap meaningful for tests and local dev.
    """

    def __init__(self, dim: int) -> None:
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = _tokenize(text)
        for tok in tokens:
            h = hash((tok, "feat")) % self.dim
            sign = 1.0 if hash((tok, "sign")) % 2 == 0 else -1.0
            vec[h] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        from sentence_transformers import SentenceTransformer  # lazy import

        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


def build_embedder():
    if settings.embedding_model == "sentence-transformers":
        return SentenceTransformerEmbedder()
    return HashingEmbedder(settings.embedding_dim)


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # vectors are pre-normalized
