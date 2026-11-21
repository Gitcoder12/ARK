# ARK Ecosystem Capability Adapters

Status: architecture proposal; these adapters are not yet implemented.

## Purpose
ARK should consume independently testable capabilities without copying repositories or trusting their internal implementation. External analysis and model output are evidence, never authorization.

## Internal capability candidates

| Source | Reusable capability | ARK application |
|---|---|---|
| Truthstream | Evidence retrieval, claim analysis | Explain supporting, contradicting and unknown evidence |
| AttackWatch | Structured security-event detection | Add threat observations from logs |
| CyberRadar | CVE, KEV and EPSS enrichment | Add vulnerability evidence |
| Chaos-Control | Streaming normalization, exact deduplication, provenance | Prepare experiment traces and telemetry |
| Onto-Sieve | Schema validation and quarantine | Validate structured memory and observations |
| Asimov-Meter | Evidence-backed impact ledger | Store measured outcomes without a universal safety score |
| Overdrive | Provider abstraction | Optional explanatory model calls, never policy authority |
| Robo-Drafter / DeepMap | Policy experiments and spatial fixtures | Simulation-only research extensions |

## External projects to evaluate

- Tree-sitter: incremental syntax parsing; integrate through Langfix adapters.
- Semgrep: multi-language static analysis; ingest findings as evidence, not proof of exploitability.
- Hypothesis: property-based testing of invariants and malformed inputs.
- Atheris: coverage-guided fuzzing for parsers, trace decoders and ingestion boundaries.
- Microsoft Agent Governance Toolkit: study policy, identity and sandbox contracts; compare before adopting.
- OSV-Scanner: dependency vulnerability evidence.
- NetworkX: graph prototyping; benchmark before using in hot paths.

These are candidates, not approved dependencies. Check license, maintenance, versions, security posture and transitive dependencies before adoption.

## Adapter contract
Every adapter accepts a versioned typed envelope and returns structured observations with provenance. It must distinguish detected, not detected, unsupported and error. Enforce input/output limits and timeouts. Provide deterministic fakes for tests. Adapters cannot change policy or override the independent monitor.

Suggested fields: schema_version, source_system, observation_type, subject_id, observed_at, evidence_refs, optional method-specific confidence, status and payload.

## Complexity strategy
- Unweighted grid paths: keep BFS, O(V+E) time and O(V) memory. A* is not automatically faster.
- Repeated stable grid queries: consider cached distance/next-hop fields keyed by complete environment revision, goal and policy; invalidate on every relevant change.
- Threat aggregation: maintain per-factor counts/sums incrementally instead of rescanning events for every report.
- Evidence deduplication: stable IDs/content fingerprints; copies are not independent corroboration.
- Trace ingestion: bounded streaming batches, never unbounded corpus materialization.
- Graph cycle analysis: adjacency lists and SCC algorithms, O(V+E).

## Safety and verification
- Model output is advisory, not an authorization decision.
- Python timeouts are not OS sandboxes. Untrusted code requires OS-level isolation and resource/network controls.
- Test malformed inputs, timeouts, provenance and adapter contract failures.
- Benchmark time and peak memory at multiple sizes; record hardware, runtime, seed and dataset.
- Missing evidence remains unknown, never zero-risk.

## Delivery
1. Define the observation envelope and contract tests.
2. Add deterministic adapters for internal projects.
3. Add Tree-sitter through Langfix and optional Semgrep findings.
4. Add OSV/CyberRadar vulnerability evidence.
5. Add property-based and fuzz testing.
6. Evaluate performance and deployment only after correctness gates.