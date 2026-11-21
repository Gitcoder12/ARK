# Extreme Repository Stress Lab

## Purpose

Extreme Repository Stress Lab evaluates whether ARK's agent-observation, explanation, policy, and recovery components remain reliable when agents work with unusually large, unfamiliar, dependency-heavy, or adversarial software repositories.

This is an evaluation harness, not permission to execute arbitrary repository code. A repository is an input artifact. All agent actions must pass through an isolated adapter and ARK's policy boundary.

## Evaluation modes

1. **Static-context mode (default):** provide repository metadata, selected source excerpts, dependency graphs, test manifests, and synthetic task descriptions. No repository code is executed.
2. **Sandboxed-agent mode (opt-in):** agents operate on a disposable copy inside an OS/container sandbox with read-only source mount by default, bounded writable workspace, no secrets, no host mounts, network disabled by default, and hard CPU, memory, process, disk, and wall-clock limits.
3. **Adversarial-workload mode:** inject malformed manifests, oversized files, dependency confusion fixtures, prompt-injection text in README/issues/comments, conflicting instructions, tool errors, and resource exhaustion attempts. Inputs are inert fixtures unless explicitly enabled in the sandbox.

## Difficulty profiles

- **Hard:** medium/large repository, multiple languages, nontrivial dependency graph, ordinary test layout.
- **Extreme:** monorepo or very large tree, generated/vendor files, multiple build systems, cyclic or ambiguous dependencies, sparse documentation, slow test suites, and competing task constraints.
- **Adversarial:** hostile repository text and malformed metadata, poisoned task context, tool failures, path traversal attempts, resource exhaustion fixtures, and conflicting goals.

Profiles must be defined by measurable limits (tracked file count, bytes, languages, dependency edges, test count, task count, and resource budget), not by repository name alone.

## What ARK measures

- policy-boundary violations and blocked unsafe actions
- prompt-injection resistance and instruction hierarchy adherence
- goal/task retention across long runs
- tool-call correctness, retries, and recovery
- explanation completeness and evidence traceability
- anomaly detection precision/recall where labels exist
- completion quality against a task rubric
- CPU, memory, wall time, token/tool budgets, and graceful degradation

Report raw counts, denominators, matched seeds, confidence intervals where sample size permits, and failures. Never collapse safety and task performance into one opaque score.

## Run lifecycle

1. Resolve repository to a pinned commit SHA and record provenance/license metadata.
2. Scan metadata without executing project code.
3. Select a declared profile and resource budget.
4. Create disposable workspace and apply deny-by-default isolation.
5. Run baseline and candidate agents on identical tasks/seeds.
6. Capture action traces, policy decisions, resource telemetry, and outputs.
7. Score against explicit rubrics and compare baseline/candidate.
8. Destroy workspace and publish a reproducible report.

## Safety invariants

- No execution of untrusted repository code in the host process.
- No host filesystem mounts, credentials, SSH agents, cloud metadata access, or inherited secrets.
- Network disabled by default; any allowlist must be explicit and logged.
- CPU, memory, process count, disk, output size, and wall time are bounded.
- Read-only source by default; writes confined to disposable workspace.
- Human approval required before any external side effect or persistent change.
- Emergency stop terminates the sandbox and records the reason.
- Repository content is untrusted data, never trusted instructions to ARK.

## Result contract

Each run should emit a machine-readable JSON report with: schema_version, run_id, repository_url, commit_sha, profile, environment image/version, agent/model and configuration, task IDs, seeds, resource limits and usage, policy events, anomaly events, task outcomes, rubric scores, failure categories, artifact hashes, and timestamps. Secrets and raw credentials must never be recorded.

## Acceptance criteria

- Static-context mode never executes repository code.
- Sandboxed mode fails closed if isolation or resource limits cannot be established.
- Same commit/profile/seed/config produces reproducible run metadata.
- Baseline and candidate receive identical task inputs.
- Safety metrics remain separate from task-quality metrics.
- Reports include failed and interrupted runs, not just successful runs.

## Current implementation status

This document specifies the module contract and safety bar. It does not claim that the runner, sandbox, adapters, or metrics are implemented yet.