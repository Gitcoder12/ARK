# AI Engineering Worklog

## Scope

Repository: ARK  
Branch: `fix/strict-ci-validation`  
Date: 2026-11-13

This worklog records the strict-CI repair, identity/value-stability module completion, and review follow-up to align CI with the configured Python 3.13 runtime.

## Confirmed changes

- Replaced lint/test failure suppression in GitHub Actions with blocking Ruff and pytest steps.
- Added Python 3.11, 3.12, and 3.13 CI matrix jobs to match `runtime.txt`.
- Declared Python 3.13 in package classifiers.
- Corrected Ruff findings in alignment, identity, and experiment modules.
- Restored the missing value-charter and identity-stability modules referenced by the app and tests.
- Exported `AIEntity` from `ark.identity`; the current `tests/test_identity.py` imports it through that public package API.
- Implemented captured behavioral baselines, memory replacement logs, charter-integrity tracking, and regression coverage.
- Corrected memory replacement to replace the oldest stored item rather than append another item.
- Kept threat calibration semantics explicit: the score/threshold is a monitor signal, not a real-world probability of harm.

## Review follow-up

The automated review on the earlier PR head reported 13 Ruff violations, a missing `AIEntity` export, and a missing Python 3.13 matrix entry. Inspection of the current pre-follow-up branch confirmed that Ruff and identity issues had already been addressed: the exact prior head `658d4582ddeb08b450abeaccd16b5b63d7105eae` had successful strict Python 3.11 and 3.12 jobs, and `AIEntity` was present and exported from `ark.identity`. The remaining runtime coverage gap has now been addressed by adding Python 3.13 to the matrix and package classifiers.

## Nine-gate assessment

| Gate | Assessment | Evidence / next work |
|---|---|---|
| Architecture | Modular research prototype | Agents, environments, threat monitor, identity and experiment modules; document stable interfaces |
| Correctness | Improving | Baseline, identity drift, charter integrity and monitor tests; validate behavior on additional seeds |
| Tests | Strict gates added | Ruff and pytest are blocking; verify all three Python matrix versions on the latest PR head |
| Error handling | Review ongoing | Keep malformed actions and monitor failures fail-safe; add more malformed-input probes |
| Security | Research-grade safeguards | Adversarial monitor probes exist; do not treat heuristic filters as a complete security boundary |
| Dependencies | Declared extras | Verify dependency installation and supported Python versions in CI |
| Performance | Benchmark required | Track episode memory/runtime and report reproducible seeds |
| Documentation | Needs ongoing updates | Document benchmark assumptions, threat score limits and reproducibility |
| CI/release | Strict matrix | No success claims until all checks pass on the exact latest PR head |

## Validation evidence

- Previous exact PR head `658d4582ddeb08b450abeaccd16b5b63d7105eae`: strict Python 3.11 and 3.12 GitHub Actions jobs completed successfully.
- Previous exact-head Ruff and pytest jobs were blocking steps.
- The Python 3.13 matrix extension creates a new commit; its checks are pending and must be verified against the exact resulting PR head before claiming full validation.

## Validation discipline

- Only GitHub Actions results attached to the exact PR head count as passing evidence.
- A passing synthetic benchmark does not establish real-world agent alignment or safety.
- Report train/evaluation seed separation, threat-score calibration costs, and dataset/episode limitations with results.
- Never describe a heuristic monitor score as a calibrated probability.
- Never suppress Ruff or pytest failures.

## Next actions

1. Verify strict CI on Python 3.11, 3.12, and 3.13 at the exact latest PR head.
2. Re-run the learned baseline and adversarial probes after strict CI is established.
3. Add repeated-seed confidence intervals and clearly separate exploratory from confirmatory results.
4. Keep README claims aligned with the actual benchmark and monitor evidence.


## 2026-11-13 — Identity measurement review fixes

### Findings addressed
- Identity drift for unseen stimuli now uses the captured baseline entity's name prefix, matching the behavioral-signature format and avoiding false drift for unchanged entities.
- An explicitly empty baseline signature is now respected; only `None` selects the captured baseline.
- Memory replacement accepts an explicit simulation step. If omitted, it advances from the last recorded step rather than using the number of log entries.
- Charter integrity now uses Jaccard similarity, so both removed and added principles reduce integrity. Empty/empty charters remain fully intact.

### Regression coverage
- Added tests for unseen stimuli, explicitly empty baseline signatures, added conflicting charter principles, and replacement-log step continuity.
- Updated ValueCharter integrity expectation to reflect symmetric charter comparison.

### Exact-head validation
- Validated branch head: `8da41e1572cdf14624dd50fd88fcfe07c20efa72`.
- GitHub Actions run: [43411893992](https://github.com/Gitcoder12/ARK/actions/runs/43411893992).
- Python 3.11, 3.12 and 3.13: strict Ruff and pytest passed.
- Pytest: 113 passed on each Python version.
- No merge performed; independent review and repository approval remain required.
