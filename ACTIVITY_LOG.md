# ARK — Activity Log

**Snapshot:** 2026-11-16  
**Purpose:** Record project changes, validation evidence and limitations without overstating maturity.

## Verified integration status

- PR #18 merged into `main` on 2026-11-16. It integrates the tabular Q-learning baseline, adversarial monitor probes, fail-closed malformed-action handling and cost-sensitive alert-threshold calibration.
- The exact PR #18 merge head passed strict Ruff and pytest on Python 3.11, 3.12 and 3.13 (GitHub Actions run #43910105125).
- PR #23 added the Gita-inspired ALLOW / BLOCK / REVIEW self-regulation research gate to `deep-dive-sprint`; that branch was then merged into `main` through PR #18.
- PR #21 (model-audit/data-integrity policy) and PR #22 (project status snapshot) were integrated into `deep-dive-sprint` before PR #18 merged it into `main`.

## Current implementation and limitations

ARK is an experimental alignment and reliability research framework. The merged code includes a tabular Q-learning baseline, adversarial monitor probes, monitor hardening, threshold calibration and a self-regulation research gate.

The benchmark has not yet been run for empirical learned-policy performance reporting. The Q-learning state is partial-observation and tabular; the simulator monitor uses privileged environment state; the threat index is heuristic rather than a calibrated real-world probability. The self-regulation gate is a research primitive, not a complete runtime safety boundary. Finite regression tests do not establish general alignment or safety.

## Append-only record

| Date | Change | Evidence | Caveats |
|---|---|---|---|
| 2026-11-16 | PR #18 merged to main | GitHub Actions run #43910105125; strict Ruff and pytest on Python 3.11, 3.12 and 3.13 | CI success is not a production-readiness or alignment guarantee |
| 2026-11-16 | PR #23 self-regulation gate integrated through PR #18 | PR #23 merged into development branch; development branch merged by PR #18 | Inputs require independent validation; not a complete runtime safety boundary |
| 2026-11-16 | PR #21 audit policy and PR #22 status snapshot integrated through PR #18 | Both PRs merged into development branch before PR #18 | Documentation does not replace an independent code or security audit |

Record failures, regressions, reverted work and checks not run. Never overwrite historical entries or attribute changes to an agent that did not perform them. A green CI run is not proof of production readiness.

## Documentation rollout — PR #20

This pull request adds the project-specific feature plan, company-fit mapping, README quality checklist and activity log. It retains the existing contribution setup, code-style guidance, experiment instructions and scientific bar while adding a clearer review workflow.

Validation for this documentation-only change: source and diff review. No application runtime test or deployment is claimed by this documentation change.
