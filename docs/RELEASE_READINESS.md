# ARK Alpha 1.0 — Release Readiness

**Working branch:** `release/alpha-1.0`  
**Baseline:** `main` at the time this branch was created  
**Status:** Release preparation; not yet a release candidate

## Release policy

This branch is limited to stabilization, correctness fixes, tests, documentation, repository organization, and release evidence. Do not add new product features during this release cycle.

Do not describe ARK as a production safety system, model certification, OS sandbox, or real-world alignment guarantee. The current documented environment is a synthetic GridWorld research framework. Keep all claims tied to reproducible evidence from the exact commit.

## Initial findings

| Area | Observed state | Release implication |
|---|---|---|
| Package metadata | `pyproject.toml` reports version `0.6.0` | Do not publish a 1.0 version until acceptance gates pass |
| README version | README contains both `v0.5.0` and older dated status snapshots | Consolidate to one current, commit-specific status |
| CI | Mainline lint and Python 3.11/3.12 test jobs were reported passing in the latest audit | Re-run against this branch and record exact run URL/commit |
| Research-feed automation | Workflow attempts a direct push to protected `main`; the refresh job failed on branch protection | Fix by proposing generated changes through a pull request, then verify a manual and scheduled run |
| Open PR work | PR #74 proposes a pull-request-based research-feed workflow | Review its exact diff and checks; do not assume it is merged or validated |
| Research claims | README documents scripted baselines, heuristic threat indicators, and monitor limitations | Preserve these caveats in all public documentation |

## Required acceptance gates

- [ ] Clean clone and documented installation succeed on a supported Python version.
- [ ] Full test suite passes on the supported Python matrix.
- [ ] Lint and formatting checks pass.
- [ ] CLI help and documented baseline/reward-conflict commands execute successfully.
- [ ] Dashboard startup is verified and its supported pages are smoke-tested.
- [ ] Research-feed workflow validates generated data and opens/updates a PR; it does not push directly to protected `main`.
- [ ] README, package metadata, changelog, and release notes agree on the release identity.
- [ ] Every benchmark result identifies inputs, seed, agent, perturbation, monitor configuration, and limitations.
- [ ] No unsupported real-world safety or alignment guarantee is claimed.
- [ ] Final release is tagged only after all gates are evidenced on the exact release commit.

## Scope boundaries

Allowed: bug fixes, regression tests, safe cleanup, documentation corrections, CI reliability, reproducibility, and release packaging.

Out of scope: new research modules, new agents, new dashboards, new integrations, and roadmap expansion.

## Verification record

This file records the initial repository audit. It is not a test report. Fill in each gate with the exact commit, command, result, and CI run or reproducible evidence before calling Alpha 1.0 ready.
