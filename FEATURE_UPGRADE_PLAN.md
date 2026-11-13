# ARK — Feature Upgrade Plan

**Snapshot:** 2026-11-13

## Product/research objective

A research framework for testing whether autonomous AI agents keep following their intended goals when rewards, instructions, memory or environments change.

## P0 — correctness, scope and evidence

- [ ] Define a threat model and preregistered scenario set for goal drift, reward hacking, memory corruption and evaluator gaming.
- [ ] Run seed-separated experiments across explicit baselines and report confidence intervals, FPR and FNR.

## P1 — complete workflow

- [ ] Add benchmark manifests that version prompts, model IDs, agent configurations, seeds and monitor thresholds.
- [ ] Measure monitor bypasses, false alarms and task utility against unmonitored baselines.

## P2 — differentiation and scale

- [ ] Provide a simulator adapter API and reproducibility bundles for independent labs.
- [ ] Publish limitations and ablation studies; avoid claims of universal alignment guarantees.

## Contribution-sized work packages

1. Reproduce one defect or establish one measurable research question.
2. Implement one bounded fix or experiment with focused tests.
3. Publish commands, environment, inputs, outputs and failure modes.
4. Add a reviewer-readable explanation and update ACTIVITY_LOG.md.

## Definition of done

- [ ] Clean setup succeeds from documented instructions.
- [ ] Tests/evaluations include happy path, boundary cases and failures.
- [ ] Results are reproducible and claims match the measured evidence.
- [ ] A human reviewer can inspect the diff and approve the scope.
