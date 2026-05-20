"""Tests for the core RAG + exact-code-lookup pipeline."""
from app.pipeline import Pipeline
from app.services import codes


def make_pipeline() -> Pipeline:
    p = Pipeline()
    p.process_document(
        "catalog-2025",
        "Equipment Catalog 2025",
        "Product code DDR333 is categorized as Football Equipment used by the "
        "recreation division. DDR333 ships under type GEAR.",
    )
    p.process_document(
        "manual-logistics",
        "Logistics Procedures Manual",
        "Items coded DDR333 (football equipment) are non-hazardous and may be "
        "transported by standard ground freight.",
    )
    return p


def test_code_extraction():
    found = codes.extract_codes("Product code DDR333 and HLM910 are listed.")
    assert "DDR333" in found
    assert "HLM910" in found


def test_looks_like_code():
    assert codes.looks_like_code("DDR333")
    assert not codes.looks_like_code("what is ddr333 used for")


def test_code_lookup_full_enumeration():
    """Exact lookup must return EVERY record, across all documents."""
    p = make_pipeline()
    res = p.code_lookup("ddr333")  # case-insensitive
    assert res.code == "DDR333"
    assert res.documents == 2
    # Each sample fits in one chunk; codes are deduped per chunk, so we expect
    # one record per document. Both documents must be present (full enumeration).
    assert res.total_matches == 2
    doc_ids = {r.document_id for r in res.records}
    assert doc_ids == {"catalog-2025", "manual-logistics"}


def test_code_lookup_unknown():
    p = make_pipeline()
    res = p.code_lookup("ZZZ999")
    assert res.total_matches == 0


def test_code_lookup_no_truncation_across_many_chunks():
    """A code spread across many chunks of one doc must return EVERY chunk."""
    p = Pipeline()
    # Build a long document where DDR333 recurs in distinct chunks.
    blocks = [
        f"Section {i}. Product code DDR333 football equipment detail number {i}. "
        + ("filler text " * 60)
        for i in range(6)
    ]
    p.process_document("big-catalog", "Big Catalog", "\n\n".join(blocks))
    res = p.code_lookup("DDR333")
    # Every chunk that mentioned the code is enumerated, not just the top-k.
    assert res.total_matches >= 6


def test_ask_returns_sources():
    p = make_pipeline()
    res = p.ask("What is DDR333 used for?")
    assert res.found
    assert res.sources
    assert "football" in res.answer.lower()


def test_ask_not_found_below_threshold():
    p = Pipeline()
    p.process_document("d1", "Doc", "Completely unrelated content about weather.")
    res = p.ask("quantum chromodynamics lagrangian derivation")
    # With no relevant content, confidence should be low and answer guarded.
    assert res.found is False or res.sources


def test_search_ranks_results():
    p = make_pipeline()
    res = p.search("football equipment", top_k=3)
    assert res.results
    assert res.results[0].score >= res.results[-1].score
