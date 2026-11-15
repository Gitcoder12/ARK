# Project Status — ARK

**Snapshot date:** 2026-11-16  
**Status type:** Initial documentation and repository-tree assessment  
**Default branch:** main  
**Review completeness:** Partial — not a code audit or release certification

## Project purpose
Research framework for evaluating, stress-testing and improving alignment, reliability and controllability of autonomous AI systems in controlled simulated environments.

## Current maturity (README-declared; not independently verified)
README states v0.5.0 with GridWorld, scripted baseline agents, MemoryAgent, perturbations, runtime safety monitor, metrics, prompting and experimental threat/paralyzer components. It explicitly notes baseline agents are scripted, threat meter is uncalibrated and monitor can livelock a naive agent.

## Observed repository structure
app.py, src/, tests/, docs/, examples/, pyproject.toml, requirements.txt, Makefile and .github/.

## Known issues and risks to investigate
Research metrics and 95% confidence intervals require reproduction with exact seeds/data and scripts. The threat meter is not a real risk forecast. Readme lists experimental components including paralyzer; claims need tight scoping. Known historical PR #18 addressed an agent-environment mutation safety issue but was blocked by required branch checks; verify current main and PR state before assuming fix is integrated. No tests run in this pass.

## Recommended next actions
Run pytest/lint and reproduce docs/RESULTS.md; inspect environment isolation and agent action boundaries; verify the PR #18 fix is merged or still outstanding; evaluate monitor livelock and false blocks; keep scripted baselines clearly distinguished from learned agents; add seeds/configuration to every published table.

## Verification record
| Check | Result |
|---|---|
| Default-branch top-level tree | Inspected |
| README | Inspected |
| Deep source review | Not performed |
| Tests / build / runtime | Not run |
| Security / dependency audit | Not run |
| Live deployment / API checks | Not run |
| Independent review | Not performed |

## Change log
- 2026-11-16: Added this initial status snapshot on a review branch. No application code or existing data changed.

> Update this file only after the corresponding inspection or verification has actually been performed. Distinguish observed facts, README claims, hypotheses and unrun checks.