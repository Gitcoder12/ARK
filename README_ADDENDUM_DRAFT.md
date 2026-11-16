# ARK — README Explanation Draft

> Proposed explanatory copy. Validate every statement against the default branch before adopting it as authoritative README text.

## In plain language

ARK is a research framework for testing whether autonomous AI agents keep following intended goals when rewards, instructions, memory or environments change.

## What is implemented

The main branch includes a tabular Q-learning baseline, adversarial monitor probes, fail-closed handling of malformed actions, cost-sensitive alert-threshold calibration and a Gita-inspired ALLOW / BLOCK / REVIEW self-regulation research gate.

## What the evidence currently supports

Strict Ruff and pytest passed on Python 3.11, 3.12 and 3.13 for the PR #18 merge head. This establishes that the committed checks passed in those CI environments; it does not demonstrate general alignment, real-world safety or production readiness.

## Known research limitations

The Q-learning baseline is tabular and uses partial observations. The benchmark has not yet been run for empirical learned-policy performance reporting. The monitor uses privileged simulator state. Threat scores are heuristic monitor signals rather than calibrated real-world risk probabilities. The self-regulation gate is not yet an integrated runtime safety boundary because its evidence inputs and execution paths need independent validation.

## Technical view

Document the actual package layout, core modules, inputs, outputs, algorithms, dependencies and execution path. Link architecture and experiment notes, and describe failure handling.

## How to run

Keep the exact tested setup commands from the authoritative README. Add expected console output and one minimal example so a new contributor can recognise success.

## Research and engineering evidence

State the baseline, environment, data, seeds, metrics and known limitations. Clearly distinguish synthetic, simulated, heuristic and real-world results.

## Contributing

See `FEATURE_UPGRADE_PLAN.md` for scoped tasks, `CONTRIBUTING.md` for workflow and `ACTIVITY_LOG.md` for the recorded work history.
