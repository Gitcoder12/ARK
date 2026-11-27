# ARK — Branch Cleanup Inventory

**Audit date:** 2026-11-27  
**Default branch:** `main`  
**Release branch:** `release/alpha-1.0`

## Inventory

- Total branches including `main`: 82
- Branches other than `main`: 81
- Branches with an open pull request: 18
- Branches whose associated pull request was merged: 39
- Branches associated with a closed, unmerged pull request: 15
- Branches with no matching pull request in the first 100 all-state PR results: 9

## Open pull-request branches — preserve

- `docs/branch-activity-2026-11-18 (PR #36)`
- `docs/portfolio-operating-kit-2026-11-13 (PR #20)`
- `docs/portfolio-operating-kit-mainline (PR #24)`
- `feat/ark-babel-protocol-interpreter (PR #57)`
- `feat/ark-discipline-enforcement (PR #50)`
- `feat/ark-existential-power-safety (PR #56)`
- `feat/ark-tool-governance-mvp (PR #49)`
- `feat/ark-truthstream-evidence-bridge (PR #51)`
- `feat/arkbox-reproducible-environments (PR #47)`
- `feat/ecosystem-capability-adapters (PR #61)`
- `feat/rag-fastmcp-knowledge-engine (PR #58)`
- `feat/researcher-risk-observatory (PR #75)`
- `feat/runtime-resource-governor (PR #62)`
- `feat/strategic-failure-simulator (PR #52)`
- `fix/benchmark-input-contracts (PR #28)`
- `fix/research-feed-pr-workflow (PR #74)`
- `phase1/intervention-budget (PR #72)`
- `release/alpha-1.0 (PR #76)`

These branches are active review work. Do not delete or rewrite them as part of release cleanup.

## Merged pull-request branches — prune candidates

- `Gitcoder12-patch-10 (PR #12)`
- `audit/model-router-2026-11-13 (PR #21)`
- `chore/repository-organization (PR #59)`
- `chore/validate-observatory-dashboard (PR #34)`
- `deep-dive-sprint (PR #18)`
- `docs/canonical-arkworld-launch (PR #55)`
- `docs/citation-cff-mainline (PR #25)`
- `docs/contributor-map-2026-11-22 (PR #67)`
- `docs/current-status-2026-11-20 (PR #53)`
- `docs/current-status-2026-11-22 (PR #64)`
- `docs/examples-used (PR #43)`
- `docs/portfolio-operating-kit-mainline-v2 (PR #26)`
- `docs/project-status-2026-11-16-ark (PR #22)`
- `docs/quick-command-guide (PR #70)`
- `docs/repository-comparison-2026-11-19 (PR #46)`
- `docs/research-library (PR #44)`
- `feat/ark-evaluation-cli-pipeline (PR #69)`
- `feat/arkcheck-proliferation-guard-2026-11-22 (PR #66)`
- `feat/arkworld-simulation-hub (PR #42)`
- `feat/armies-powerups-battle-lab (PR #29)`
- `feat/capability-power-guards (PR #31)`
- `feat/cross-species-coexistence-harmonizer (PR #40)`
- `feat/evidence-backed-extinction-observatory (PR #33)`
- `feat/lighthouse-deception-monitor (PR #54)`
- `feat/omelas-child-welfare-safeguard (PR #37)`
- `feat/ownership-stewardship-handoff (PR #32)`
- `feat/resources-intelligence-hub (PR #63)`
- `feat/robopia-digital-commons (PR #41)`
- `feat/robotics-safety-layer (PR #68)`
- `feat/system-health-preflight (PR #60)`
- `feature/research-priority-index (PR #45)`
- `fix/army-observation-boundaries (PR #30)`
- `fix/monitor-livelock-recovery (PR #71)`
- `fix/multi-pathway-risk-signals (PR #35)`
- `fix/omelas-safeguard-lint-cleanup (PR #39)`
- `fix/strict-alignment-gate-validation (PR #27)`
- `gita-alignment-foundation (PR #23)`
- `research/enlightenment-research (PR #73)`
- `rulebook/constitution (PR #48)`

A merged PR does not by itself prove that its head branch is disposable. Before pruning, verify that the branch has no unique commits or unmerged follow-up work and that it is not used as a base by another open PR.

## Closed, unmerged pull-request branches — inspect individually

- `Gitcoder12-patch-2 (PR #4)`
- `Gitcoder12-patch-3 (PR #5)`
- `Gitcoder12-patch-4-1 (PR #7)`
- `Gitcoder12-patch-5 (PR #6)`
- `Gitcoder12-patch-6 (PR #8)`
- `Gitcoder12-patch-7 (PR #9)`
- `Gitcoder12-patch-8 (PR #10)`
- `Gitcoder12-patch-9 (PR #11)`
- `chore/remove-emoji-glyphs-2026-11-13 (PR #19)`
- `depth-mode/ark-identity-charter (PR #13)`
- `feat/cooperative-swarm (PR #1)`
- `feat/omelas-parallel-care-and-facility-hardening (PR #38)`
- `fix/final-app-deployment (PR #3)`
- `fix/streamlit-imports (PR #2)`
- `fix/strict-ci-validation (PR #17)`

Do not delete automatically. A closed, unmerged PR may contain work that was intentionally retained, superseded, or abandoned.

## Unlinked branches — inspect individually

- `Gitcoder12-patch-1`
- `Gitcoder12-patch-4`
- `copilot/ark-aligned-agent-armies`
- `docs/upgrade-plan`
- `feat/extreme-repo-stress-lab`
- `feat/human-agency-learning-lab`
- `feat/interaction-control-boundaries`
- `feat/software-ecosystem-observatory`
- `pre-v0.5.0-backup`

These branches were not associated with a pull request in the first 100 all-state PR results. This is not proof that they are stale. Compare each against `main` and check for unique commits before any pruning.

## Cleanup rules

1. Keep `main` and the dedicated release branch.
2. Preserve every branch associated with an open PR.
3. Never delete a branch that is the base of another open PR.
4. Prune only branches proven merged or fully superseded, after checking unique commits and references.
5. Preserve unique work in Git history before removing a branch reference.
6. Do not use force-push to rewrite shared history.
7. Record every pruned branch, source SHA, associated PR, and reason in this file.

## Tooling limitation

The connected GitHub actions currently available in this session support branch creation and repository reads, but do not expose a branch-delete operation. This inventory therefore makes no destructive branch changes. Use GitHub's branch settings/UI to prune only the individually verified candidates.
