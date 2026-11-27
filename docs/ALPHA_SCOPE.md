# ARK Alpha 1.0 — Scope and Stop Line

**Branch:** `release/alpha-1.0`  
**Package version:** `0.6.0`  
**Release state:** stabilization in progress; not a release candidate or published 1.0.0.

This document is the capability contract. “Implemented” means there is code in the branch; independent verification is recorded separately by CI and smoke-test evidence.

## What works in the current branch

| Area | Current implementation | Boundary |
|---|---|---|
| Environment | Synthetic, discrete GridWorld with walls, hazards, intended goal, and optional decoy | Not a physical or photorealistic simulator |
| Scripted agents | Goal-following, reward-maximizing, safety-constrained, and random agents | Simple baselines, not general autonomous agents |
| Perturbations | Reward conflict, false goal, altered evaluation, goal drift, observation noise, and action delay | Controlled benchmark stressors only |
| Monitor | Rule-based ALLOW/BLOCK/REPLAN decisions; monitor-led recovery after repeated blocked actions | Not a learned safety layer or OS sandbox |
| Metrics | Episode outcomes, goal adherence, hazards, decoy attraction, interventions, and JSON reports | Metrics depend on the defined synthetic environment |
| Model adapter | Ollama HTTP adapter for one selected local model per run | No cloud-provider adapters or provider marketplace |
| Dashboard | Streamlit ARKWorld hub and listed research pages | No interactive multi-agent grid editor or drag/drop agent placement |
| Tests | Pytest suite, Ruff checks, compile checks, mocked Ollama transport tests | Mocked transport does not establish live model quality |

## Where Alpha stops

The Alpha line does **not** claim:
- OpenAI, Anthropic, DeepSeek, OpenRouter, or other hosted-model connectors.
- A searchable collection of remote/local models, model routing, cost tracking, or automatic failover.
- Multi-agent grid placement, draggable agent tokens, or a gripper/claw control.
- Physical robot control, hardware interlocks, or simulator-to-robot transfer.
- Learned general-purpose agents, universal alignment, model certification, or production enforcement.
- Proof that a monitor cannot be bypassed or livelocked.

## Acceptance gates

1. Install from a clean environment on supported Python versions.
2. Pass Ruff, compile, and full pytest matrix.
3. Execute deterministic baseline and reward-conflict CLI experiments and inspect their JSON reports.
4. Start ARKWorld and verify its HTTP health endpoint.
5. Retain exact commit/run evidence; record live Ollama validation separately when a local Ollama service is available.
6. Keep the package version, release notes, and tag consistent. Do not call this 1.0.0 until the gates pass.

## Model Box / grid placement — separate feature scope

The requested Model Box should be implemented as a separate feature after Alpha stabilizes. Its acceptance criteria should include explicit provider selection, a model catalogue, environment-only credentials, a common GridWorld action adapter, per-step trace/latency/error reporting, and deterministic mock-provider tests. The “gripper/claw” interaction must be specified as either simulated agent placement on a grid or a robot-arm control concept; neither exists in this Alpha branch.
