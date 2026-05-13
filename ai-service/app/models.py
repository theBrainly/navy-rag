"""Pydantic request/response models (mirrors PRD Section 7 AI-service API)."""
from typing import Optional
from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    document_id: str
    title: str
    text: str
    page_map: Optional[dict[int, str]] = None  # optional page_number -> text


class ProcessResponse(BaseModel):
    document_id: str
    chunks_created: int
    codes_indexed: int


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    page_number: int
    text: str
    codes: list[str] = Field(default_factory=list)


class ScoredChunk(Chunk):
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[ScoredChunk]


class CodeLookupRequest(BaseModel):
    code: str


class CodeRecord(BaseModel):
    code: str
    document_id: str
    title: str
    chunk_id: str
    page_number: int
    context: str


class CodeLookupResponse(BaseModel):
    code: str
    total_matches: int
    documents: int
    records: list[CodeRecord]


class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class Source(BaseModel):
    document_id: str
    title: str
    page_number: int
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
    confidence: float
    found: bool
