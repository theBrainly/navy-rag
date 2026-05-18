"""Deterministic exact-code index (PRD Module H2).

This is the key addition over a pure-RAG design: it guarantees *full enumeration*
of every chunk/document that references a product code, with no truncation from
semantic ranking. Backed by MongoDB in production; in-memory here.
"""
from __future__ import annotations

from collections import defaultdict

from app.models import CodeRecord


class CodeIndex:
    def __init__(self) -> None:
        self._index: dict[str, list[CodeRecord]] = defaultdict(list)

    def add(self, record: CodeRecord) -> None:
        self._index[record.code].append(record)

    def lookup(self, code: str) -> list[CodeRecord]:
        from app.services.codes import normalize_code

        return list(self._index.get(normalize_code(code), []))

    def clear(self) -> None:
        self._index.clear()
