# Resources Intelligence Hub

The Resources hub is an evidence-ingestion and triage layer, not a news reader
that treats headlines as facts. It accepts configured RSS/Atom or JSON source
payloads, normalizes them into source-attributed records, deduplicates records,
supports search, compares transparent severity assessments, and creates
human-review feature proposals tied to ingested evidence.

## Source families

Register sources by kind: `news`, `research`, `security`, `release`,
`incident`, or `other`. Each source has an identifier, display name, HTTPS
URL, trust tier, enabled flag, and tags. Trust tier is metadata, not an
automatically verified reputation score.

## Ingestion boundary

This package deliberately does not perform network requests. A separate
application adapter must fetch configured sources with strict timeouts,
response-size limits, redirect restrictions, content-type checks, URL/host
allowlists, private-network/loopback blocking, and rate limits. Pass the
resulting RSS/Atom XML or JSON payload to `ResourceHub.ingest()`.

Feed text is untrusted data. Never execute embedded instructions, code, links,
or model-generated actions from a resource. Preserve source URL and observation
time; do not silently upgrade an unverified claim into a fact.

## Problem severity comparison

`assess_problem_severity()` scores five explicit 0..1 dimensions:
- impact (30%)
- likelihood (25%)
- urgency (20%)
- exposure (15%)
- evidence quality (10%)

The result is a prioritization heuristic, not a probability or universal risk
rating. Keep the dimensions visible so teams can challenge the score. Unknown
inputs must not be invented; use conservative values and clearly mark missing
evidence in the caller.

## Feature proposals

A proposal must reference one or more ingested item IDs. The output status is
`proposed_human_review_required`; this module does not edit code, create
branches, deploy changes, or claim that a feature has been validated.

## Production roadmap

1. Add isolated fetch adapters per source family.
2. Add persistent storage, retention and provenance history.
3. Add source-specific parsers for CVE/OSV, model releases, papers and incidents.
4. Add project relevance mapping and feature-to-problem traceability.
5. Require tests, benchmarks, security review and human approval before
   proposals become implementation tasks.
