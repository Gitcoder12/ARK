# ARK — Activity Log

**Snapshot:** 2026-11-13

## Verified portfolio work

PR #17 reports strict CI and 113 tests per Python version; PR #18 reports the learned baseline, adversarial probes, threshold calibration and 130 tests per Python version. Both remain open and unmerged. PR #19 is a draft text cleanup. Current PR-head checks were successful: https://github.com/Gitcoder12/ARK/pulls

## Current implementation and limitations

Alignment and reliability research framework. Current open PRs add strict CI, identity/value-charter measurement, a tabular Q-learning baseline, adversarial probes, fail-closed monitor behavior and alert calibration. The benchmark remains experimental; results do not establish general alignment or safety.

## Append-only record

| Date | Human / agent | Issue or PR | Scope and files | Validation command / environment | Result | Evidence and caveats |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | contributor id | link | paths | exact command | pass / fail / not run | evidence |

Record failures, regressions, reverted work and checks not run. Never overwrite historical entries or attribute changes to an agent that did not perform them. A green CI run is not proof of production readiness.
