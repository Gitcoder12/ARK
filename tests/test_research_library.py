"""Integrity checks for the structured ARK research library."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "data" / "research_library.json"


def load_library() -> dict:
    return json.loads(LIBRARY.read_text(encoding="utf-8"))


def test_library_schema_and_unique_ids() -> None:
    data = load_library()
    assert data["schema_version"] == 1
    assert data["index_name"] == "ARK Research Priority Index (ARPI)"
    papers = data["papers"]
    ids = [paper["id"] for paper in papers]
    assert len(ids) == len(set(ids))
    assert papers


def test_each_record_has_attribution_and_relevance_metadata() -> None:
    for paper in load_library()["papers"]:
        for field in ("id", "title", "authors", "year", "venue",
                      "publication_status", "url", "category", "priority",
                      "rationale", "metadata_source", "metadata_verified"):
            assert field in paper, (paper.get("id"), field)
        assert isinstance(paper["authors"], list)
        assert paper["url"].startswith("https://")
        assert paper["priority"] in {"P1", "P2", "P3"}
        assert paper["rationale"].strip()
        if not paper["metadata_verified"]:
            assert paper.get("metadata_note", "").strip()


def test_priority_weights_sum_to_one_hundred() -> None:
    weights = load_library()["scoring"]["weights"]
    assert sum(item["weight"] for item in weights) == 100


def test_candidate_records_are_not_mislabeled_as_verified() -> None:
    candidates = [
        paper for paper in load_library()["papers"]
        if paper["id"].endswith("-candidate")
    ]
    assert candidates
    assert all(not paper["metadata_verified"] for paper in candidates)
