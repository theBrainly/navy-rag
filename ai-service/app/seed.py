"""Seed the running AI service with sample defense-catalog documents.

Usage (service must be running on :8000):
    python -m app.seed
"""
from __future__ import annotations

import os

import httpx

AI_URL = os.environ.get("AI_SERVICE_URL", "http://localhost:8000")

SAMPLE_DOCS = [
    {
        "document_id": "catalog-2025",
        "title": "Equipment Catalog 2025",
        "text": (
            "Product code DDR333 is categorized as Football Equipment used by "
            "the recreation and morale division. It ships under shipment type "
            "GEAR and is sourced from the United States. Effective date 2025-01-01.\n\n"
            "Product code HLM910 is a Tactical Helmet, category Protective Gear, "
            "department Field Operations, shipment type ARMOR.\n\n"
            "Product code DDR333 also appears in the recreation supplies appendix, "
            "confirming its use as football equipment for unit fitness programs."
        ),
    },
    {
        "document_id": "manual-logistics",
        "title": "Logistics Procedures Manual",
        "text": (
            "Section 4.2 Shipping classifications. Items coded DDR333 (football "
            "equipment) are non-hazardous and may be transported by standard "
            "ground freight. Items coded ARM450, a propellant component, are "
            "hazardous class 1.3 and require specialized handling.\n\n"
            "All product codes must be verified against the master catalog before "
            "a shipment manifest is generated."
        ),
    },
    {
        "document_id": "inventory-q1",
        "title": "Q1 Inventory Report",
        "text": (
            "On-hand inventory: DDR333 football equipment, 1,240 units, warehouse "
            "B. HLM910 tactical helmets, 320 units, warehouse A. ARM450 propellant "
            "components, 80 units, secure depot."
        ),
    },
]


def main() -> None:
    for doc in SAMPLE_DOCS:
        r = httpx.post(f"{AI_URL}/process", json=doc, timeout=30)
        r.raise_for_status()
        print(f"processed {doc['document_id']}: {r.json()}")
    print("\nseed complete.")


if __name__ == "__main__":
    main()
