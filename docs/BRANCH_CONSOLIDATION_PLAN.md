# ARK Branch Audit and Consolidation Plan

**Audit date:** 2026-11-16  
**Baseline:** `main` at `703481a0eaffd32e7340643a6b6a02de33e17472`  
**Scope:** Every non-`main` branch returned by GitHub at audit time.

## Executive summary

There are **25 non-main branches**. They are not 25 independent features. Several are duplicates, competing versions of the same file, or overlapping research changes.

The repository has **12 open pull requests**. The largest research branches overlap substantially:
- `deep-dive-sprint`: 74 commits ahead of main; 33 changed files in its comparison.
- `fix/strict-ci-validation`: 36 commits ahead; overlaps the deep-dive work on CI, charter, identity, and experiment code.
- `depth-mode/ark-identity-charter`: 4 commits ahead; overlaps the same identity/charter area.
- `gita-alignment-foundation`: 7 commits ahead; new self-regulation research foundation.

Do not merge all 25 branches directly into `main`. First consolidate into one integration line, resolve overlaps, run the full suite, then open one reviewed PR to protected `main`.

## Branch-by-branch disposition

| Branch | Observed delta from main | Proposed handling |
|---|---|---|
| `Gitcoder12-patch-1` | +1 commit; `requirements.txt` | Inspect dependency names/versions; keep only if required and compatible. |
| `Gitcoder12-patch-2` | +1; `app.py` import change | Duplicate/overlapping with Streamlit import fixes; compare and keep one correct implementation. |
| `Gitcoder12-patch-3` | +1; adds `test.py` | Review whether this is a real test; avoid retaining a redundant root-level test stub. |
| `Gitcoder12-patch-4-1` | +1; adds `Agents.MD` | Review policy content; consolidate into one canonical contributor/agent policy document if useful. |
| `Gitcoder12-patch-4` | +1; adds `src/hardware` | Inspect exact file/type and intended hardware interface before deciding. |
| `Gitcoder12-patch-5` | +1; adds 16-line `src/hardware` item | Inspect exact content and whether it duplicates patch-4. |
| `Gitcoder12-patch-6` | +1; adds `Skills.MD` | Review; merge useful guidance into canonical contributor documentation. |
| `Gitcoder12-patch-7` | +1; adds `Architecture.MD` | Review against actual package architecture; move/merge into `docs/` if accurate. |
| `Gitcoder12-patch-8` | +1; adds `Security.MD` | Review threat model and security claims; consolidate into canonical security documentation. |
| `Gitcoder12-patch-9` | +1; adds `Contributing.md` | Compare with existing `CONTRIBUTING.md`; avoid case-sensitive duplicate files. |
| `Gitcoder12-patch-10` | +2; adds `CITATION.cff` | Review metadata and citation validity; likely useful if accurate. |
| `audit/model-router-2026-11-13` | +1; adds `MODEL_AUDIT_ROUTER.md` | Review and consolidate useful data-integrity/review requirements. |
| `chore/remove-emoji-glyphs-2026-11-13` | +6; edits README and research plan | Review presentation-only changes; do not overwrite or regress canonical research text. |
| `copilot/ark-aligned-agent-armies` | Identical to main | No unique code to integrate; candidate for archival/deletion after final check. |
| `deep-dive-sprint` | +74; learned baseline, adversarial probes, monitor hardening, threat calibration, CI, identity/charter work | Highest-priority technical review. Preserve valuable features, but resolve overlap with strict-CI and identity branches. Worklog itself lists unrun benchmarks and remaining risks. |
| `depth-mode/ark-identity-charter` | +4; identity and charter implementation, CI and README changes | Compare against deep-dive and strict-CI versions; select one coherent implementation, not both blindly. |
| `docs/portfolio-operating-kit-2026-11-13` | +4; handbook, company-fit, feature plan, README and contributor docs | Keep only useful contributor/process docs; remove duplication and portfolio noise from core research docs. |
| `docs/project-status-2026-11-16-ark` | +1; adds `PROJECT_STATUS.md` | Useful dated status snapshot; keep if still accurate after integration. Open PR #22. |
| `docs/upgrade-plan` | Diverged: +1 / -11; adds `docs/UPGRADE_PLAN.md` | Do not merge branch history. Inspect and selectively extract the document if still relevant. |
| `feat/cooperative-swarm` | +2; adds cooperative agent and large `app.py` rewrite | Review backend agent separately from UI. Do not accept the UI rewrite without runtime tests. Open PR #1. |
| `fix/final-app-deployment` | +1; large `app.py` rewrite | Competes with cooperative-swarm UI and Streamlit import branches; compare behavior and deployment evidence before choosing. Open PR #3. |
| `fix/streamlit-imports` | +1; small `app.py` import fix | Compare with patch-2 and final deployment branch; keep one correct import strategy. Open PR #2. |
| `fix/strict-ci-validation` | +36; strict CI, charter and identity modules/tests | Strong candidate source for CI and identity work, but overlaps deep-dive and depth-mode. Open PR status to be checked against exact head. |
| `gita-alignment-foundation` | +7; self-regulation gate, tests, example, research docs and Start Here | Current active integration/research branch. Keep as the single working branch while consolidation proceeds. |
| `pre-v0.5.0-backup` | 12 commits behind main; no unique commits ahead | Preserve as historical backup; never merge into current work. |

## Open pull requests found

| PR | Branch | Subject | Audit note |
|---|---|---|---|
| #22 | `docs/project-status-2026-11-16-ark` | Project status snapshot | Docs-only; verify status after consolidation. |
| #21 | `audit/model-router-2026-11-13` | Model audit and data integrity | Draft; review policy and merge useful parts. |
| #20 | `docs/portfolio-operating-kit-2026-11-13` | Project handbook | Draft; deduplicate documentation. |
| #19 | `chore/remove-emoji-glyphs-2026-11-13` | Remove emoji glyphs | Draft; presentation-only review. |
| #18 | `deep-dive-sprint` | Learned baseline, adversarial probes, threat calibration | Major technical PR; inspect exact head and rerun CI. |
| #13 | `depth-mode/ark-identity-charter` | Identity and charter measurement | Overlaps PR #18. |
| #12 | `Gitcoder12-patch-10` | Citation metadata | Validate metadata. |
| #5 | `Gitcoder12-patch-3` | Streamlit title in test.py | Likely minor; inspect necessity. |
| #4 | `Gitcoder12-patch-2` | Import paths | Overlaps PR #2. |
| #3 | `fix/final-app-deployment` | App refactor | Competes with PR #1. |
| #2 | `fix/streamlit-imports` | Streamlit imports | Competes with PR #3 and #4. |
| #1 | `feat/cooperative-swarm` | Cooperative swarm and UI | Separate backend value from large UI rewrite. |

## Recommended consolidation order

1. **Freeze branch creation.** Use `gita-alignment-foundation` as the only active integration branch for now.
2. **Establish the quality gate.** Reconcile strict CI changes from the technical branches; run Ruff and pytest with failures enabled.
3. **Integrate core research code.** Review learned baseline, adversarial evaluation, threat calibration, identity/charter, and monitor hardening. Resolve overlapping versions by tests and source review.
4. **Integrate self-regulation.** Wire the Gita-inspired gate into one existing action execution path; add end-to-end tests proving that BLOCK/REVIEW actions cannot execute.
5. **Review the app once.** Compare the three app.py alternatives; choose one coherent version, then test imports and launch/deployment.
6. **Consolidate documentation.** Keep one README, one CONTRIBUTING guide, one architecture guide, one security/research integrity guide, and this Start Here map.
7. **Review small patches.** Dependencies, citation, hardware, and miscellaneous root files only after their contents are verified.
8. **Validate the complete integration branch.** Run the full test suite, Ruff, package install, example smoke tests, and app startup. Record exact outputs.
9. **Open one integration PR to main.** Keep main protected; merge only after all checks and review are complete.
10. **Archive or delete superseded branches only after integration is merged and the final branch audit confirms no unique work remains.**

## Important safety rule

A branch comparison tells us which commits/files differ; it does not prove code correctness. The audit identifies candidates and conflicts, not automatic merge approval. In particular, no branch should be merged merely because GitHub says it is mergeable.
