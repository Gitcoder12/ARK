# ARK — maintainer status and merge plan

**Snapshot date:** 2026-11-22  
**Default branch:** `main` at `3692d4bf9f098d8f1454789f34723e7892c5dc9b`  
**Open PRs at audit:** 15  
**Project classification:** active research prototype; not a production agent-safety guarantee.

## What is in main

The project documentation describes a deterministic GridWorld research environment, scripted baseline and memory agents, reward/goal/evaluation perturbations, an ALLOW/BLOCK/REPLAN monitor, episode metrics and traces, prompt/adversarial experiments, and experimental governance/risk modules. Treat this as documented scope, not independent verification of every component.

The README caveats remain binding: baseline agents are scripted rather than learned; the threat meter is uncalibrated; the monitor can livelock a naive agent. Robotics transfer, robust long-horizon goal integrity, bypass probes, energy budgets and watchdog governance are not complete merely because they appear in the roadmap.

## Current CI failures confirmed from workflow logs

| PR | Feature | Latest observed CI | Finding | Action |
|---|---|---|---|---|
| [#63](https://github.com/Gitcoder12/ARK/pull/63) | Resources intelligence hub | Fail | Ruff F821: `timezone` referenced but not imported in `src/ark/resources.py` | Add correct import; rerun full CI |
| [#62](https://github.com/Gitcoder12/ARK/pull/62) | Runtime resource governor | Fail | Lint failure; inspect full Ruff output and format/fix reported lines | Fix lint; rerun CI |
| [#58](https://github.com/Gitcoder12/ARK/pull/58) | RAG + FastMCP | Fail | Test collection SyntaxError: `src/ark/rag/__init__.py` contains escaped source text instead of valid Python | Replace file with valid Python; rerun test matrix |

## Other open PRs

| PR | Feature | Audit disposition |
|---|---|---|
| [#61](https://github.com/Gitcoder12/ARK/pull/61) | Ecosystem capability adapters | CI passed on inspected head; draft. Keep draft until reviewed and dependencies are clear. |
| [#57](https://github.com/Gitcoder12/ARK/pull/57) | BABEL protocol interpreter | Draft; inspect code, threat boundaries and tests before marking ready. |
| [#56](https://github.com/Gitcoder12/ARK/pull/56) | Power governance observatory | Draft; keep assumptions and synthetic/modelled values clearly labelled. |
| [#52](https://github.com/Gitcoder12/ARK/pull/52) | Strategic failure simulator | Draft; verify scenarios and reproducibility. |
| [#51](https://github.com/Gitcoder12/ARK/pull/51) | TruthStream evidence bridge | Draft; validate timestamp parsing, provenance and duplicate evidence handling. |
| [#50](https://github.com/Gitcoder12/ARK/pull/50) | Discipline engine | Draft; research primitive, not production enforcement. |
| [#49](https://github.com/Gitcoder12/ARK/pull/49) | Tool governance MVP | Draft; requires trusted identity, durable audit storage and runtime enforcement before production claims. |
| [#47](https://github.com/Gitcoder12/ARK/pull/47) | ARKBox reproducible environments | Draft and reported non-mergeable; refresh against main and validate. |
| [#36](https://github.com/Gitcoder12/ARK/pull/36) | Branch activity documentation | Stale documentation branch; consolidate or close after status docs are accepted. |
| [#28](https://github.com/Gitcoder12/ARK/pull/28) | Benchmark input validation | CI passed on inspected head; review exact diff and current base before merge. |
| [#24](https://github.com/Gitcoder12/ARK/pull/24) | Project handbook | Existing unresolved P2 documentation findings: Q-learning baseline claim and Python-version claim need correction. |
| [#20](https://github.com/Gitcoder12/ARK/pull/20) | Project handbook/contributor workflow | Draft, stale documentation branch; consolidate with #24 or close as duplicate after comparison. |

## Merge and verification policy

1. Fix #63, #62 and #58 before considering them for merge.
2. Review each feature diff and tests; green CI is necessary, not sufficient.
3. Rebase/update stacked PRs only after their parent is integrated. Do not merge a child branch before its parent.
4. Do not present draft PR features as mainline functionality.
5. Require exact-commit test evidence for benchmark claims and all safety-related claims.
6. No agent, monitor, charter or governance module is a proof of alignment, an OS sandbox, or an inviolable safety boundary.

## Branch hygiene recommendation

Keep `main` protected and use one short-lived branch per independently reviewable feature. Keep branches that back active PRs. After a PR is merged, verify the merged commit and CI, then delete its source branch. Close duplicate/stale documentation PRs after preserving useful content in one canonical document. Do not delete a branch merely because it is old: first check whether it contains unique unmerged work. Avoid creating a new branch for every small README/status correction; batch related documentation into one documentation PR.

## Audit limits

This snapshot records GitHub PR metadata, selected diffs/review threads and the workflow runs available at audit time. It is not a fresh local test run of every branch, and CI may change after this timestamp. Recheck the PR head SHA and workflow status immediately before merge.
