from ark.governance.truthstream_bridge import assess_truthstream_result


def payload():
    return {
        "claim": {"text": "A factual claim"},
        "status": "likely_true",
        "confidence_score": 0.91,
        "provenance": {"status": "source_backed"},
        "supporting_evidence": [
            {"evidence_id": "a", "retrieved_at": "2026-11-20T08:00:00Z",
             "source": {"url": "https://alpha.example/report"}},
            {"evidence_id": "b", "retrieved_at": "2026-11-20T08:01:00Z",
             "source": {"url": "https://beta.example/report"}},
        ],
        "contradicting_evidence": [],
        "neutral_evidence": [],
    }


def test_two_provenanced_sources_can_be_used_as_context():
    result = assess_truthstream_result(payload())
    assert result.usable_as_context
    assert result.distinct_source_host_count == 2


def test_demo_or_missing_provenance_is_rejected():
    item = payload()
    item["provenance"] = {"status": "demo_or_incomplete"}
    assert not assess_truthstream_result(item).usable_as_context


def test_single_source_is_not_enough():
    item = payload()
    item["supporting_evidence"].pop()
    assert not assess_truthstream_result(item).usable_as_context


def test_truthstream_context_never_authenticates_runtime_events():
    result = assess_truthstream_result(payload())
    assert "runtime" not in result.__dataclass_fields__
    assert result.usable_as_context
