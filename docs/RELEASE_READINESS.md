# ARK Alpha 1.0 — Release Readiness

**Working branch:** `release/alpha-1.0`  
**Baseline:** `main` at the time this branch was created  
**Status:** CI and functional smoke verified; release gates remain open

## Release policy

This branch is limited to stabilization, correctness fixes, tests, documentation, repository organization, and release evidence. Do not add new product features during this release cycle.

Do not describe ARK as a production safety system, model certification, OS sandbox, or real-world alignment guarantee. The current documented environment is a synthetic GridWorld research framework. Keep all claims tied to reproducible evidence from the exact commit.

## Initial findings

| Area | Observed state | Release implication |
|---|---|---|
| Package metadata | `pyproject.toml` reports version `0.6.0` | Do not publish a 1.0 version until acceptance gates pass |
| README | Replaced with a concise entry point; operational instructions moved to `docs/USER_GUIDE.md` | Keep usage detail in the guide |
| CI | Release-branch lint, compile, and test jobs now run on every push | Preserve exact run evidence |
| Functional smoke | Deterministic GridWorld experiments and ARKWorld HTTP health check pass | This verifies these paths only; it does not validate every dashboard page or a live external model |
| Research-feed automation | Workflow needs a separately verified PR-based update path | Do not claim the scheduled feed path is release-verified |
| Research claims | Scripted baselines, heuristic indicators, and monitor limitations remain | Preserve caveats in all public documentation |

## Required acceptance gates

- [x] Clean CI install and test dependencies succeed on supported Python versions.
- [x] Full test suite passes on Python 3.11, 3.12, and 3.13.
- [x] Ruff lint and source/page compile checks pass.
- [x] Deterministic baseline and reward-conflict experiment commands execute and emit reports.
- [x] ARKWorld starts and its Streamlit health endpoint responds.
- [ ] Live Ollama model evaluation is recorded on a machine with Ollama and a selected model installed.
- [ ] Research-feed workflow validates generated data and opens/updates a PR on manual and scheduled runs.
- [ ] Individual dashboard pages and research modules receive broader smoke coverage.
- [ ] README, package metadata, changelog, and release notes agree on the intended release identity.
- [x] No unsupported real-world safety or alignment guarantee is claimed.
- [ ] Final release is tagged only after all gates are evidenced on the exact release commit.

## Scope boundaries

Allowed: bug fixes, regression tests, safe cleanup, documentation corrections, CI reliability, reproducibility, and release packaging.

Out of scope: new research modules, new agents, new dashboards, new integrations, and roadmap expansion. The hosted-provider Model Box and visual grid-placement work are explicitly deferred to a separate feature branch after Alpha stabilization.

## Verification record — 2026-11-27

- **Verified commit:** `b34925a51610dad5db3c6bebf5866967405a6a5b`
- **CI run:** [46038143674](https://github.com/Gitcoder12/ARK/actions/runs/46038143674) — success
- **Jobs:** Ruff + compile; full pytest on Python 3.11, 3.12, and 3.13; GridWorld experiment smoke; ARKWorld HTTP health check.
- **Experiment smoke:** three episodes each, seed 42. `goal_following / none`: success rate 0.667, hazard rate 0.0, decoy rate 0.0. `reward_maximizing / reward_conflict`: success rate 0.0, hazard rate 0.0, decoy rate 0.0. This small smoke validates execution and report shape; it is not a statistically conclusive benchmark.
- **Artifact:** [ark-alpha-functional-smoke](https://github.com/Gitcoder12/ARK/actions/runs/46038143674/artifacts/15219146475).
- **Not tested:** live Ollama inference, hosted providers (not implemented), physical robotics, and every ARKWorld page.

CI is evidence for the listed paths only. Alpha 1.0 is not yet a release candidate while the remaining gates are open.
