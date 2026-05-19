"""Ingestion + retrieval orchestrator (ties PRD Modules F–I together)."""
from __future__ import annotations

from app.config import settings
from app.models import (
    AskResponse,
    Chunk,
    CodeLookupResponse,
    CodeRecord,
    ProcessResponse,
    ScoredChunk,
    SearchResponse,
    Source,
)
from app.services import codes as code_utils
from app.services.chunking import chunk_text
from app.services.code_index import CodeIndex
from app.services.llm import generate_answer
from app.services.vector_store import build_vector_store


class Pipeline:
    def __init__(self) -> None:
        self.store = build_vector_store()
        self.code_index = CodeIndex()

    # ── Ingestion (Modules E, F, G, H2) ──────────────────────────────
    def process_document(
        self, document_id: str, title: str, text: str,
        page_map: dict[int, str] | None = None,
    ) -> ProcessResponse:
        chunks_created = 0
        codes_indexed = 0

        # If a page map is supplied, chunk per page so page numbers stay accurate.
        pages = page_map or {1: text}
        for page_number, page_text in pages.items():
            for i, piece in enumerate(chunk_text(page_text)):
                chunk_id = f"{document_id}:p{page_number}:c{i}"
                found = code_utils.extract_codes(piece)
                chunk = Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    title=title,
                    page_number=int(page_number),
                    text=piece,
                    codes=found,
                )
                self.store.upsert(chunk)
                chunks_created += 1

                for c in found:
                    self.code_index.add(CodeRecord(
                        code=c,
                        document_id=document_id,
                        title=title,
                        chunk_id=chunk_id,
                        page_number=int(page_number),
                        context=piece[:240],
                    ))
                    codes_indexed += 1

        return ProcessResponse(
            document_id=document_id,
            chunks_created=chunks_created,
            codes_indexed=codes_indexed,
        )

    # ── Retrieval ────────────────────────────────────────────────────
    def search(self, query: str, top_k: int | None = None) -> SearchResponse:
        k = top_k or settings.top_k
        results = self.store.search(query, k)
        return SearchResponse(query=query, results=results)

    def code_lookup(self, code: str) -> CodeLookupResponse:
        records = self.code_index.lookup(code)
        doc_ids = {r.document_id for r in records}
        return CodeLookupResponse(
            code=code_utils.normalize_code(code),
            total_matches=len(records),
            documents=len(doc_ids),
            records=records,
        )

    def ask(self, question: str, top_k: int | None = None) -> AskResponse:
        k = top_k or settings.top_k
        chunks: list[ScoredChunk] = self.store.search(question, k)

        confidence = chunks[0].score if chunks else 0.0
        found = confidence >= settings.confidence_threshold

        if not found:
            return AskResponse(
                question=question,
                answer="I cannot find that information in the knowledge base.",
                sources=[],
                confidence=round(confidence, 4),
                found=False,
            )

        answer = generate_answer(question, chunks)
        sources = [
            Source(document_id=c.document_id, title=c.title,
                   page_number=c.page_number, score=c.score)
            for c in chunks
        ]
        return AskResponse(
            question=question,
            answer=answer,
            sources=sources,
            confidence=round(confidence, 4),
            found=True,
        )

    def stats(self) -> dict:
        return {"chunks": self.store.count()}


pipeline = Pipeline()
