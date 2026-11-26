"""Strict adapter for TruthStream claim-verification results.

TruthStream can corroborate external factual claims. It cannot authenticate that
an agent performed an action; that requires trusted runtime telemetry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class TruthstreamAssessment:
    claim: str
    status: str
    confidence: float
    provenance_status: str
    distinct_source_host_count: int
    usable_as_context: bool
    limitations: tuple[str, ...]


def assess_truthstream_result(
    payload: dict[str, Any], *, min_source_hosts: int = 2
) -> TruthstreamAssessment:
    if min_source_hosts < 1:
        raise ValueError("min_source_hosts must be positive")
    claim_obj = payload.get("claim")
    claim = claim_obj.get("text", "") if isinstance(claim_obj, dict) else ""
    status = str(payload.get("status", "unknown"))
    confidence = payload.get("confidence_score", 0.0)
    if (
        not isinstance(confidence, (int, float))
        or isinstance(confidence, bool)
        or not 0 <= confidence <= 1
    ):
        raise ValueError("confidence_score must be between 0 and 1")

    evidence_items: list[dict[str, Any]] = []
    for key in ("supporting_evidence", "contradicting_evidence", "neutral_evidence"):
        group = payload.get(key, [])
        if isinstance(group, list):
            evidence_items.extend(item for item in group if isinstance(item, dict))

    verified_hosts: set[str] = set()
    all_complete = bool(evidence_items)
    for item in evidence_items:
        source = item.get("source")
        url = source.get("url") if isinstance(source, dict) else None
        evidence_id = item.get("evidence_id")
        retrieved_at = item.get("retrieved_at")
        host = urlparse(url).hostname if isinstance(url, str) else None
        if (
            not host
            or urlparse(url).scheme != "https"
            or not isinstance(evidence_id, str)
            or not evidence_id.strip()
            or not isinstance(retrieved_at, str)
            or not retrieved_at.strip()
        ):
            all_complete = False
        else:
            verified_hosts.add(host.lower())

    provenance = payload.get("provenance")
    declared_source_backed = (
        isinstance(provenance, dict) and provenance.get("status") == "source_backed"
    )
    host_count = len(verified_hosts)
    usable = all_complete and declared_source_backed and host_count >= min_source_hosts
    limitations = () if usable else (
        "TruthStream result is not accepted as source-backed context.",
        "Demo, incomplete, missing-provenance, or single-host results must not drive enforcement.",
    )
    return TruthstreamAssessment(
        claim=claim,
        status=status,
        confidence=float(confidence),
        provenance_status="source_backed" if usable else "unverified",
        distinct_source_host_count=host_count,
        usable_as_context=usable,
        limitations=limitations,
    )
