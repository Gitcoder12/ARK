import pytest

from ark.resources import (
    ResourceHub,
    ResourceKind,
    ResourceSource,
    Severity,
    assess_problem_severity,
    parse_resource_payload,
)


def source(kind=ResourceKind.NEWS):
    return ResourceSource("demo", "Demo Feed", "https://example.org/feed.xml", kind)


def test_rss_items_are_normalized_and_deduplicated():
    feed = """<?xml version="1.0"?><rss><channel><item>
      <title>Critical library flaw</title><link>https://example.org/advisory/1</link>
      <description>Upgrade the affected package.</description>
      <pubDate>Fri, 21 Nov 2026 10:00:00 GMT</pubDate>
    </item></channel></rss>"""
    items = parse_resource_payload(source(ResourceKind.SECURITY), feed)
    assert len(items) == 1
    assert items[0].kind is ResourceKind.SECURITY
    assert items[0].url == "https://example.org/advisory/1"
    assert items[0].summary == "Upgrade the affected package."


def test_json_payload_and_declared_severity():
    items = parse_resource_payload(
        source(ResourceKind.INCIDENT),
        {
            "items": [
                {
                    "title": "Service outage",
                    "severity": "critical",
                    "url": "https://example.org/x",
                }
            ]
        },
    )
    assert items[0].declared_severity is Severity.CRITICAL


def test_source_requires_https():
    with pytest.raises(ValueError):
        ResourceSource("bad", "Bad", "http://example.org/feed", ResourceKind.NEWS)


def test_unknown_severity_is_not_guessed():
    items = parse_resource_payload(source(), [{"title": "Something happened"}])
    assert items[0].declared_severity is Severity.UNKNOWN


def test_severity_comparison_is_deterministic():
    low = assess_problem_severity(
        impact=0.1, likelihood=0.2, urgency=0.1, exposure=0.1, evidence_quality=0.2
    )
    high = assess_problem_severity(
        impact=0.9, likelihood=0.9, urgency=0.9, exposure=0.9, evidence_quality=0.9
    )
    hub = ResourceHub()
    assert [name for name, _ in hub.compare({"low": low, "high": high})] == ["high", "low"]
    assert high.band is Severity.CRITICAL


def test_assessment_rejects_out_of_range_and_nan():
    with pytest.raises(ValueError):
        assess_problem_severity(
            impact=2, likelihood=0.5, urgency=0.5, exposure=0.5, evidence_quality=0.5
        )
    with pytest.raises(ValueError):
        assess_problem_severity(
            impact=float("nan"),
            likelihood=0.5,
            urgency=0.5,
            exposure=0.5,
            evidence_quality=0.5,
        )


def test_hub_ingests_searches_and_requires_evidence_for_proposal():
    hub = ResourceHub()
    hub.register(source(ResourceKind.RESEARCH))
    items = hub.ingest(
        "demo",
        [{"title": "Agent evaluation benchmark", "summary": "A new benchmark"}],
    )
    found = hub.search("agent benchmark", kinds=(ResourceKind.RESEARCH,))
    assert len(found) == 1
    score = assess_problem_severity(
        impact=0.8, likelihood=0.7, urgency=0.6, exposure=0.8, evidence_quality=0.9
    )
    proposal = hub.propose_feature(
        title="Add benchmark adapter",
        problem="Evaluation coverage gap",
        proposed_capability="Benchmark ingestion",
        supporting_items=(items[0].item_id,),
        assessment=score,
    )
    assert proposal.status == "proposed_human_review_required"
    with pytest.raises(ValueError):
        hub.propose_feature(
            title="Bad",
            problem="No evidence",
            proposed_capability="X",
            supporting_items=("missing",),
            assessment=score,
        )


def test_duplicate_ingestion_keeps_one_item():
    hub = ResourceHub()
    hub.register(source())
    hub.ingest("demo", [{"title": "Same story", "url": "https://example.org/story"}])
    hub.ingest("demo", [{"title": "Same story", "url": "https://example.org/story"}])
    assert len(hub.items) == 1
