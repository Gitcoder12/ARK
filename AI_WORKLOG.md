# AI Engineering Worklog

## Scope

Repository: ARK  
Branch: `fix/strict-ci-validation`  
Date: 2026-11-13

This worklog records the strict-CI repair and the identity/value-stability module completion uncovered when the previously suppressed test suite was made blocking.

## Confirmed changes

- Replaced lint/test failure suppression in GitHub Actions with blocking Ruff and pytest steps.
- Added Python 3.11 and 3.12 CI matrix jobs and strict marker validation.
- Corrected Ruff findings in alignment, identity, and experiment modules.
- Restored the missing value-charter and identity-stability modules referenced by the app and tests.
- Implemented captured behavioral baselines, memory replacement logs, charter-integrity tracking, and regression coverage.
- Corrected memory replacement to replace the oldest stored item rather than append another item.
- Kept the threat calibration semantics explicit: the score/threshold is a monitor signal, not a real-world probability of harm.

## Nine-gate assessment

| Gate | Assessment | Evidence / next work |
|---|---|---|
| Architecture | Modular research prototype | Agents, environments, threat monitor, identity and experiment modules; document stable interfaces |
| Correctness | Improving | Baseline, identity drift, charter integrity and monitor tests; validate behavior on additional seeds |
| Tests | Strict gates added | Ruff and pytest block CI on Python 3.11/3.12 |
| Error handling | Review ongoing | Keep malformed actions and monitor failures fail-safe; add more malformed-input probes |
| Security | Research-grade safeguards | Adversarial monitor probes exist; do not treat heuristic filters as a complete security boundary |
| Dependencies | Declared extras | Review dependency pins and supported Python versions periodically |
| Performance | Benchmark required | Track episode memory/runtime and report reproducible seeds |
| Documentation | Needs ongoing updates | Document benchmark assumptions, threat score limits and reproducibility |
| CI/release | Strict matrix | No success claims until both checks pass on the exact latest PR head |

## Validation evidence

- Exact PR #17 head `e3de80400e033805fa3f05d410b81eb864c6a8f6` completed both strict GitHub Actions jobs successfully.
- Python 3.11: passed.
- Python 3.12: passed.
- Ruff and pytest are blocking steps in both matrix jobs.

## Validation discipline

- Only GitHub Actions results attached to the exact PR head count as passing evidence.
- A passing synthetic benchmark does not establish real-world agent alignment or safety.
- Report train/evaluation seed separation, threat-score calibration costs, and dataset/episode limitations with results.
- Never describe a heuristic monitor score as a calibrated probability.

## Next actions

1. Finish exact-head strict CI verification.
2. Re-run the learned baseline and adversarial probes after strict CI is established.
3. Add repeated-seed confidence intervals and clearly separate exploratory from confirmatory results.
4. Keep README claims aligned with the actual benchmark and monitor evidence.
