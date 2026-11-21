"""Tests for ARK's source-cited knowledge store."""

import pytest

from ark.rag.store import LocalKnowledgeBase, RetrievalError


def test_policy_and_research_collections_are_separate(tmp_path):
    root = tmp_path / "knowledge"
    root.mkdir()
    (root / "policy.md").write_text("Human approval required for irreversible actions.", encoding="utf-8")
    store = LocalKnowledgeBase(tmp_path / "ark.sqlite3", allowed_roots=[root])
    store.index_directory(root, "ark-policies")
    assert store.search("human approval irreversible", "ark-policies")
    assert store.search("human approval irreversible", "ark-research") == []


def test_search_returns_traceable_untrusted_evidence(tmp_path):
    root = tmp_path / "knowledge"
    root.mkdir()
    (root / "monitor.md").write_text("A safety monitor must independently verify constraints.", encoding="utf-8")
    store = LocalKnowledgeBase(tmp_path / "ark.sqlite3", allowed_roots=[root])
    store.index_directory(root, "ark-policies")
    hit = store.search("independently verify constraints", "ark-policies")[0]
    assert hit["citation"].startswith("monitor.md:")
    assert hit["trust"] == "untrusted_source_material"
    assert hit["sha256"]


def test_unapproved_path_is_rejected(tmp_path):
    allowed = tmp_path / "allowed"
    denied = tmp_path / "denied"
    allowed.mkdir()
    denied.mkdir()
    store = LocalKnowledgeBase(tmp_path / "ark.sqlite3", allowed_roots=[allowed])
    with pytest.raises(RetrievalError):
        store.index_directory(denied, "ark-policies")
