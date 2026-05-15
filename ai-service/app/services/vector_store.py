"""Vector store (PRD Module H1).

In-memory by default so the service runs with zero infrastructure. Set
VECTOR_BACKEND=qdrant to use a real Qdrant instance (interface kept identical).
"""
from __future__ import annotations

from app.config import settings
from app.models import Chunk, ScoredChunk
from app.services.embeddings import build_embedder, cosine


class InMemoryVectorStore:
    def __init__(self) -> None:
        self.embedder = build_embedder()
        self._chunks: dict[str, Chunk] = {}
        self._vectors: dict[str, list[float]] = {}

    def upsert(self, chunk: Chunk) -> None:
        self._chunks[chunk.chunk_id] = chunk
        self._vectors[chunk.chunk_id] = self.embedder.embed(chunk.text)

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        if not self._chunks:
            return []
        qv = self.embedder.embed(query)
        scored = [
            (cid, cosine(qv, vec)) for cid, vec in self._vectors.items()
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        out: list[ScoredChunk] = []
        for cid, score in scored[:top_k]:
            c = self._chunks[cid]
            out.append(ScoredChunk(score=round(score, 4), **c.model_dump()))
        return out

    def count(self) -> int:
        return len(self._chunks)

    def clear(self) -> None:
        self._chunks.clear()
        self._vectors.clear()


class QdrantVectorStore:
    """Thin Qdrant-backed store. Imported lazily to avoid the dependency in
    local/in-memory mode."""

    def __init__(self) -> None:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams

        self.embedder = build_embedder()
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.create_collection(
                self.collection,
                vectors_config=VectorParams(
                    size=settings.embedding_dim, distance=Distance.COSINE
                ),
            )

    def upsert(self, chunk: Chunk) -> None:
        from qdrant_client.models import PointStruct

        vec = self.embedder.embed(chunk.text)
        self.client.upsert(
            self.collection,
            points=[PointStruct(id=abs(hash(chunk.chunk_id)) % (2**63),
                                vector=vec, payload=chunk.model_dump())],
        )

    def search(self, query: str, top_k: int) -> list[ScoredChunk]:
        qv = self.embedder.embed(query)
        hits = self.client.search(self.collection, query_vector=qv, limit=top_k)
        return [ScoredChunk(score=round(h.score, 4), **h.payload) for h in hits]

    def count(self) -> int:
        return self.client.count(self.collection).count

    def clear(self) -> None:
        self.client.delete_collection(self.collection)


def build_vector_store():
    if settings.vector_backend == "qdrant":
        return QdrantVectorStore()
    return InMemoryVectorStore()
