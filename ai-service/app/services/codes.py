"""Product-code extraction (PRD Module E).

Defense catalogs use codes like DDR333, NSN-style runs, alphanumeric SKUs, etc.
We match common patterns and normalize them for the deterministic Code Index.
"""
from __future__ import annotations

import re

# Patterns: 2-6 letters followed by 2-6 digits (DDR333), or letter/number
# groups separated by dashes (AB-1234, NSN-5310-01-234-5678).
_CODE_PATTERNS = [
    re.compile(r"\b[A-Z]{2,6}\d{2,6}\b"),
    re.compile(r"\b[A-Z]{1,4}-\d{2,6}(?:-\d{1,6}){0,4}\b"),
    re.compile(r"\b\d{4,}-[A-Z0-9]{2,}\b"),
]


def extract_codes(text: str) -> list[str]:
    found: set[str] = set()
    upper = text.upper()
    for pat in _CODE_PATTERNS:
        for m in pat.findall(upper):
            found.add(normalize_code(m))
    return sorted(found)


def normalize_code(code: str) -> str:
    return code.strip().upper().replace(" ", "")


def looks_like_code(query: str) -> bool:
    q = query.strip()
    if " " in q:
        return False
    return bool(extract_codes(q))
