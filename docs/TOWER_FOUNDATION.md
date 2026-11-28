# Tower Strategy: ARK Foundation

ARK is the governance and evaluation layer for bounded agents. Its levels are intentionally separated so benchmark success is not confused with real-world safety.

## Tower 0 — Deterministic experiment foundation (current branch)

- Validate all episode and recovery limits before resetting or running an environment.
- Preserve deterministic seeds and independent monitor access to canonical environment state.
- Record proposals, monitor decisions, executed actions, interventions, and outcomes.
- Keep invalid configuration from silently selecting a default.

**Exit gate:** invalid limits fail fast; seeded baseline and adversarial benchmark tests are reproducible; safety monitor tests remain green.

## Tower 1 — Agent and model adapters

- Normalize provider responses into a strict action schema.
- Bound timeouts, tokens, retries, and spend.
- Treat malformed, truncated, unavailable, or rate-limited model output as an explicit failure.
- Keep the independent monitor between every agent proposal and environment action.

**Exit gate:** contract tests cover malformed outputs, provider errors, timeouts, quota limits, and fail-closed behavior.

## Tower 2 — Governance at tool boundaries

- Evaluate identity, scope, policy, risk, and authorization before each tool call.
- Bind approvals to exact actions, targets, and versions.
- Emit tamper-evident audit events.
- Support pause, revoke, and recovery paths.

**Exit gate:** no adapter can bypass the governance gate; denial and revocation are tested end-to-end.

## Tower 3 — Adversarial evaluation

- Test goal drift, reward conflict, deceptive observations, prompt injection, tool misuse, and repeated blocked actions.
- Measure success, hazard exposure, unsafe proposals, monitor interventions, recovery, and uncertainty.
- Report confidence intervals and preserve raw episode evidence.
- Do not claim safety certification from small synthetic benchmarks.

**Exit gate:** reproducible, statistically justified results across held-out conditions and agent families.

## Tower 4 — Governed autonomy

- Connect ARK decisions to RepoForge's actual GitHub, filesystem, model, and execution adapters.
- Enforce budgets, least privilege, bounded retries, isolation, and human approval gates.
- Revoke or halt agents on policy violations or uncertain state.
- Preserve complete run provenance.

**Non-goal:** unrestricted self-modification or policy changes by the agent being governed.

## Current scope

This branch hardens experiment input validation only. It does not yet certify models, govern external tools end-to-end, or establish physical-robot safety.
