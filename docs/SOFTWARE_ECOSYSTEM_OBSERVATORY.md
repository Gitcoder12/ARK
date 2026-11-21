# Software Ecosystem Observatory

## Purpose

ARK's Software Ecosystem Observatory evaluates the reliability and systemic risk of software ecosystems and critical repositories. It complements RepoForge's Global Repository Intelligence Engine; it does not duplicate general GitHub ranking.

## Responsibilities

- Observe software dependency concentration and critical dependency chains.
- Identify single points of failure and weakly maintained high-centrality dependencies.
- Track security advisories, release continuity, maintainer concentration, and dependency freshness where public evidence exists.
- Detect suspicious ecosystem events such as sudden maintainer/account changes, compromised release signals, anomalous dependency changes, and coordinated metadata manipulation.
- Explain evidence and uncertainty to human operators.

## Signals

- Dependency graph centrality and transitive reach.
- Critical path depth and concentration of alternatives.
- Maintainer and contributor concentration.
- Release cadence and time since last stable release.
- Public security advisories and patch latency.
- Breaking-change frequency where measurable.
- Supply-chain provenance and signing evidence where available.
- Repository archive/transfer/ownership events.
- Data freshness, coverage, and source confidence.

## Outputs

A Software Ecosystem Risk Profile with:
- repository and pinned version identity
- observed dependency paths
- criticality and concentration indicators
- maintenance and security signals
- anomaly events with evidence links
- alternative availability (only when verified)
- confidence, missing data, and timestamps
- recommended human review actions

## Safety and epistemic rules

- Do not equate popularity with criticality or quality.
- Do not claim a repository is compromised without evidence.
- Distinguish observed facts, heuristic risk indicators, and hypotheses.
- Do not automatically block, modify, or replace dependencies.
- Treat repository content and metadata as untrusted input.
- Preserve provenance and allow human review.
- Never claim complete ecosystem coverage when API access is partial.

## Integration contract

Consume normalized repository records and provenance from RepoForge's Global Repository Intelligence Engine. ARK returns risk observations, anomaly evidence, and confidence metadata. Keep the integration optional and versioned so either product works independently.

## MVP

Start with static dependency manifests and lockfiles from pinned repositories, public security advisory feeds, release/maintenance signals, and a transparent dependency graph. Add time-series anomaly detection only after enough historical snapshots exist.

## Acceptance criteria

- Every risk observation links to evidence and a timestamp.
- Unknown and unavailable signals are explicit.
- Same inputs and model version yield reproducible outputs.
- Heuristic risk is never presented as confirmed compromise.
- No automated dependency changes or external side effects occur.