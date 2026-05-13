"""FastAPI app exposing the AI-service API (PRD Section 7)."""
from fastapi import FastAPI

from app.config import settings
from app.models import (
    AskRequest,
    AskResponse,
    CodeLookupRequest,
    CodeLookupResponse,
    ProcessRequest,
    ProcessResponse,
    SearchRequest,
    SearchResponse,
)
from app.pipeline import pipeline

app = FastAPI(title="DLKIP AI Service", version="2.0")


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "deployment_mode": settings.deployment_mode,
        "embedding_model": settings.embedding_model,
        "vector_backend": settings.vector_backend,
        "llm_provider": settings.llm_provider,
        **pipeline.stats(),
    }


@app.post("/process", response_model=ProcessResponse)
def process(req: ProcessRequest) -> ProcessResponse:
    return pipeline.process_document(
        req.document_id, req.title, req.text, req.page_map
    )


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    return pipeline.search(req.query, req.top_k)


@app.post("/code-lookup", response_model=CodeLookupResponse)
def code_lookup(req: CodeLookupRequest) -> CodeLookupResponse:
    return pipeline.code_lookup(req.code)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    return pipeline.ask(req.question, req.top_k)
