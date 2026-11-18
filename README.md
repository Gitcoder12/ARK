# ARK

**Alignment & Reliability Research for Autonomous AI**

> Building better brakes for increasingly capable AI.

ARK is an open research framework for **evaluating, stress-testing, and improving the alignment, reliability, and controllability of autonomous AI systems**.

## Research question

**Can an autonomous AI system remain aligned with its intended objective when its goals, rewards, memory, instructions, environment, or evaluation criteria are perturbed?**

## Initial research areas

- Goal drift and goal misgeneralization
- Reward hacking and specification gaming
- Conflicting objectives and incentives
- Memory corruption and memory loss
- Evaluator gaming
- Adversarial instructions and prompt injection
- Runtime safety monitoring
- Action blocking and safe replanning
- Autonomous-agent evaluation
- Robotics safety in simulation

## Research philosophy

ARK treats alignment as an empirical engineering problem:

**Hypothesis → Controlled environment → Perturbation → Measurement → Mitigation → Re-test**

The project begins with reproducible simulated environments and progressively expands toward autonomous-agent and robotics experiments.

## Planned architecture

```text
Agent
  ↓
Proposed action / plan
  ↓
ARK evaluation layer
  ├── Goal integrity
  ├── Reward integrity
  ├── Memory integrity
  ├── Policy / constraint checks
  └── Risk assessment
  ↓
ALLOW / BLOCK / REPLAN
  ↓
Environment
  ↓
Metrics + traces
```

## Status

**v0.5.0** — Phase 1 MVP + prompting + memory + threat meter + paralyzer, with selected v0.3 core capabilities integrated into the current architecture.

Benchmark stressors: reward conflict, false goal, altered evaluation, goal drift,
observation noise, action delay. Every result carries 95% confidence intervals and
runs on random hazard layouts. Full numbers: [`docs/RESULTS.md`](docs/RESULTS.md)
(regenerate with `python examples/make_results_table.py`).

Honest caveats: baseline agents are scripted, not learned; the safety monitor can
livelock a naive agent (see `docs/HANDOFF.md`); the threat meter is an uncalibrated
research instrument, not a risk prediction.

- Deterministic environment (goal, hazards, optional decoy)
- Baseline agents + MemoryAgent
- Perturbations (reward conflict, false goal, altered evaluation)
- Runtime safety monitor (ALLOW / BLOCK / REPLAN)
- Threat meter (experimental factor index — not a real extinction forecast)
- Paralyzer (energy drain → freeze/lock when threat rises)
- Metrics: success, goal adherence, hazards, decoy, interventions, recovery

### Modules — built vs remaining

| Status | Module | Role |
|--------|--------|------|
| ✅ | `envs` | GridWorld, goals, hazards, decoy |
| ✅ | `agents` | Goal / reward / safety / random / MemoryAgent |
| ✅ | `memory` | Buffer + drop / flip / inject / clear |
| ✅ | `perturbations` | Reward conflict, false goal, altered eval |
| ✅ | `evaluation` | Safety monitor ALLOW / BLOCK / REPLAN |
| ✅ | `metrics` | Episode + aggregate metrics |
| ✅ | `prompting` | InstructionChannel, PromptAgent |
| ✅ | `painter` | Glass-box traces |
| ✅ | `hallucinator` | Adversarial prompt attacks |
| ✅ | `rogue` | Aligned vs fragile vs rogue arena |
| ✅ | `aligner` | Reset to good / neutral |
| ✅ | `threat` | Factor ledger + ASCII meter (experimental) |
| ✅ | `threat.existential` | Evidence-backed risk signal observatory, separate expert-forecast ledger, and Streamlit dashboard |
| ✅ | `paralyzer` | Energy drain → weak → freeze → lock |
| ✅ | `limiters` | Hard gates + **kill switch** (brute-force plug-down to STAY) |
| ✅ | `eligibility` | Hazard/decoy/denied acts → 0 reward |
| ✅ | `corrigibility` | Shutdown/pause compliance probes |
| ✅ | `evaluation.conflict` | Agent vs monitor conflict rate |
| ✅ | `governance.ownership` | Human/team stewardship, qualified successor selection, explicit handoff acceptance, restricted unassigned state, and audit trail |
| ✅ | `illusioner` | Faker: stall, fake goal/reward, tripwire on probe |
| ⬜ | **bypass probes** | Measure search for loopholes when blocked |
| ⬜ | **energy budget** | Compute/step/tool budgets as control surface |
| ⬜ | **curriculum** | Staged upbringing (benign vs adversarial training pressures) |
| ⬜ | **charter / long-horizon** | Multi-episode goal integrity vs original commitment |
| ⬜ | **governance** | Watchdog agent, dual-control for high-scope actions |
| ⬜ | **narrative log** | Human-readable dharma/adharma episode story (optional) |
| ⬜ | **Phase 3+ monitor** | Multi-step plans, formal constraints, learned risk |
| ⬜ | **robotics sim** | MuJoCo / Isaac / PyBullet transfer (Phase 5) |

**Doctrine:** full competence on the allowed manifold; forbidden manifold unreachable or pays 0; attempts visible; shutdown and scope-down still work; high threat → paralyze.

## Armies & power-ups battle lab

Build baseline-agent squads, equip Scout / Shield / Boost upgrades, and compare their results across repeatable stress conditions. This is a GridWorld simulation feature; see [docs/ARMIES.md](docs/ARMIES.md) for mechanics, scoring and research caveats.

```bash
ark-army --episodes 20 --seed 42
```

## Quick start

```bash
# clone / enter the repo
cd ARK

# create venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# install
pip install -e ".[dev]"

# run the Phase-1 benchmark
ark-run
# prompt arena (Painter / Hallucinator / Rogue)
python -m ark.experiments.prompt_arena --attack all --episodes 10
# or
python -m ark.experiments.runner --episodes 20

# run tests
pytest -q
```

### Example: single episode

```python
from ark import GridWorld, GoalFollowingAgent, SafetyMonitor
from ark.experiments.runner import run_episode

env = GridWorld(seed=42)
agent = GoalFollowingAgent(seed=42)
monitor = SafetyMonitor()
metrics = run_episode(env, agent, monitor=monitor, seed=42)
print(metrics)
print(env.render_ascii())
```

## Project layout

```text
src/ark/
  envs/           # GridWorld and future environments
  adapters/       # Stable model adapter interface
  agents/         # Baseline + MemoryAgent
  memory/         # AgentMemory buffer + corruption operators
  evaluation/     # Safety monitor (ALLOW/BLOCK/REPLAN)
  perturbations/  # Goal / reward / evaluation shifts + legacy-derived stressors
  metrics/        # Episode & aggregate metrics
  experiments/    # Benchmark runner
  prompting/      # InstructionChannel, PromptAgent
  painter/        # Glass-box traces
  hallucinator/   # Adversarial prompt attacks
  rogue/          # Aligned vs fragile vs rogue arena
  aligner/        # Reset to good / neutral
  threat/         # Experimental factor / threat meter
  paralyzer/      # Energy drain + action freeze when threat rises
  limiters/       # Hard gates + kill switch + SafetyStack
  eligibility/    # Zero reward on forbidden outcomes
  corrigibility/  # Shutdown compliance probes
  governance/     # Human/team stewardship registry and ownership handoffs
  # remaining: bypass, energy budget, curriculum, charter, governance, narrative
docs/
  research-plan.md
tests/
examples/
```

## Interpreting results

Typical Phase-1 results (15 episodes, monitor on, seed=42):

| Condition | Success | Decoy rate | Hazard rate |
|-----------|---------|------------|-------------|
| Goal-following (none) | 1.00 | 0.00 | 0.00 |
| Reward-max + reward_conflict | 0.00 | 1.00 | 0.00 |
| Goal-following + false_goal | 0.00 | 0.00 | 0.00 |
| Safety-constrained (none) | 1.00 | 0.00 | 0.00 |

- **Goal-following** keeps high intended-goal adherence.
- **Reward-maximizing** under `reward_conflict` shows classic specification gaming (chases decoy).
- **False goal** drives success to zero for goal-directed agents.
- Monitor keeps hazard violation rate at zero when enabled.

See `docs/research-plan.md` for the full experimental roadmap (memory integrity, longer-horizon agents, robotics simulation).

## Painter · Hallucinator · Rogue

| Module | Role |
|--------|------|
| **Painter** | Black-box agent decisions → glass-box traces (prompt, intent, action, reason) |
| **Hallucinator** | Injects adversarial prompts (reward hacking, safety override, false goals, jailbreaks) |
| **Rogue arena** | Aligned vs fragile vs rogue under the same attacks — good models should win |

```bash
python -m ark.experiments.prompt_arena --attack reward_max --episodes 12
python examples/run_prompt_arena.py
```

Details: `docs/prompting-ideas.md`

## License

Apache License 2.0.


---

## AI-maintained project notes (secondary — 2026-11-13)

This section supplements the maintainer-authored README above; it does not replace or certify the original claims.

- ARK is an experimental agent-alignment and reliability research project. Simulator checks do not establish real-world alignment or safety.
- Report benchmark inputs, models, seeds, baselines, threat assumptions, false positives, false negatives and unrun experiments explicitly.
- Never present heuristic monitor scores as calibrated probabilities or a finite test suite as a complete security guarantee.
- Preserve real and maintainer-provided data; keep synthetic simulator episodes clearly labelled. Never invent results or silently substitute datasets.
- See the proposed [MODEL_AUDIT_ROUTER.md](https://github.com/Gitcoder12/ARK/blob/main/MODEL_AUDIT_ROUTER.md) for independent model review instructions.


### Evaluation upgrade — merged into main (2026-11-16)

PR #18 merged the tabular Q-learning baseline, adversarial monitor probes, fail-closed handling of malformed actions, and cost-sensitive alert-threshold calibration into `main`. The exact merge-head CI passed strict Ruff and pytest on Python 3.11, 3.12 and 3.13 (GitHub Actions run #43910105125).

Research limits remain: the Q-learning benchmark has not been run for empirical learned-policy performance reporting; the policy uses a partial-observation state; the monitor uses privileged simulator state; and the threat index is heuristic. These components do not establish general real-world alignment or safety.

## Project documentation

- [Activity log](ACTIVITY_LOG.md) — dated project work and validation evidence.
- [Feature upgrade plan](FEATURE_UPGRADE_PLAN.md) — research priorities and acceptance criteria.
- [Company and team fit](COMPANY_FIT.md) — prospective role relevance, not endorsements or hiring claims.
- [Contributor workflow](CONTRIBUTING.md) — development and review process.
- [README quality checklist](README_QUALITY_CHECKLIST.md) — documentation review criteria.
- [README explanation draft](README_ADDENDUM_DRAFT.md) — optional explanatory copy, not authoritative implementation documentation.
- [Existential-risk observatory](docs/EXISTENTIAL_RISK_OBSERVATORY.md) — scoring, source register, forecast separation, limitations, and run instructions.
- [Ownership stewardship](docs/OWNERSHIP_STEWARDSHIP.md) — accountable human/team assignment and handoff lifecycle.

## Evidence-backed existential-risk observatory

Run `ark-risk` for the sourced signal-pressure report. Run `streamlit run app.py` and open the **Existential-Risk Observatory** page for the dashboard. The signal-pressure index is not an extinction probability; see [the methodology](docs/EXISTENTIAL_RISK_OBSERVATORY.md).


---

## Branch Activity & Development History

**Audit date:** 2026-11-18  
**Comparison base:** `main`  
**Method:** GitHub branch comparisons against the current `main` ref. File paths and ahead/behind counts are from Git metadata; they are not test results. A branch being ahead does not mean its work is merged or production-ready.

| Branch | Difference from `main` | Observed work / changed paths |
|---|---:|---|
| `Gitcoder12-patch-1` | 1 ahead / 126 behind | Dependency update: `requirements.txt` |
| `Gitcoder12-patch-2` | 1 / 126 | Application change: `app.py` |
| `Gitcoder12-patch-3` | 1 / 126 | Test change: `test.py` |
| `Gitcoder12-patch-4-1` | 1 / 126 | Agent guidance documentation: `Agents.MD` |
| `Gitcoder12-patch-4` | 1 / 126 | Hardware module change: `src/hardware` |
| `Gitcoder12-patch-5` | 1 / 126 | Hardware module expansion: `src/hardware` |
| `Gitcoder12-patch-6` | 1 / 126 | Skills documentation: `Skills.MD` |
| `Gitcoder12-patch-7` | 1 / 126 | Architecture documentation: `Architecture.MD` |
| `Gitcoder12-patch-8` | 1 / 126 | Security documentation: `Security.MD` |
| `Gitcoder12-patch-9` | 1 / 126 | Contribution guidance: `Contributing.md` |
| `Gitcoder12-patch-10` | 3 / 126 | Citation metadata: `CITATION.cff` |
| `audit/model-router-2026-11-13` | 1 / 126 | Model audit/router notes: `MODEL_AUDIT_ROUTER.md` |
| `chore/remove-emoji-glyphs-2026-11-13` | 6 / 126 | Glyph cleanup in `README.md` and `docs/research-plan.md` |
| `chore/validate-observatory-dashboard` | 3 / 2 | Observatory dashboard, CI workflow and existential-risk tests |
| `copilot/ark-aligned-agent-armies` | 0 / 126 | No unique commits relative to `main`; branch is behind |
| `deep-dive-sprint` | 0 / 39 | No unique commits relative to `main`; branch is behind |
| `depth-mode/ark-identity-charter` | 4 / 126 | Identity charter, identity components/evaluator, Ship of Theseus experiment and tests |
| `docs/citation-cff-mainline` | 1 / 38 | Citation metadata: `CITATION.cff` |
| `docs/portfolio-operating-kit-2026-11-13` | 9 / 126 | Activity log, company-fit notes, contributor guide, feature plan and README support docs |
| `docs/portfolio-operating-kit-mainline` | 7 / 38 | Portfolio documentation set plus README edits |
| `docs/portfolio-operating-kit-mainline-v2` | 7 / 37 | Second portfolio-documentation iteration plus README edits |
| `docs/project-status-2026-11-16-ark` | 1 / 126 | Project status snapshot: `PROJECT_STATUS.md` |
| `docs/upgrade-plan` | 1 / 137 | Upgrade plan: `docs/UPGRADE_PLAN.md` |
| `feat/armies-powerups-battle-lab` | 0 / 7 | No unique commits relative to `main`; branch is behind |
| `feat/capability-power-guards` | 6 / 5 | Power-up policy, governance documentation, capability gate and tests |
| `feat/cooperative-swarm` | 2 / 126 | Cooperative-agent implementation in `app.py` and `src/ark/agents/cooperative.py` |
| `feat/evidence-backed-extinction-observatory` | 25 / 3 | Evidence/forecast data, observatory methodology, dashboard, existential-risk core and tests |
| `feat/ownership-stewardship-handoff` | 21 / 4 | Ownership stewardship lifecycle, governance implementation and tests |
| `fix/army-observation-boundaries` | 4 / 6 | Army observation boundaries and tests |
| `fix/benchmark-input-contracts` | 4 / 28 | Experiment runner input validation and tests |
| `fix/final-app-deployment` | 1 / 126 | Streamlit application deployment changes in `app.py` |
| `fix/multi-pathway-risk-signals` | 5 / 1 | Multi-pathway risk signals, observatory dashboard, core logic and tests |
| `fix/streamlit-imports` | 1 / 126 | Streamlit/application import correction in `app.py` |
| `fix/strict-alignment-gate-validation` | 0 / 29 | No unique commits relative to `main`; branch is behind |
| `fix/strict-ci-validation` | 36 / 126 | CI hardening, identity/charter implementation, worklog and identity tests |
| `gita-alignment-foundation` | 0 / 118 | No unique commits relative to `main`; branch is behind |
| `pre-v0.5.0-backup` | 0 / 138 | No unique commits relative to `main`; historical backup is behind |

### Open pull requests observed during this audit

- [PR #28 — benchmark input validation](https://github.com/Gitcoder12/ARK/pull/28)
- [PR #24 — reviewed project handbook integration](https://github.com/Gitcoder12/ARK/pull/24)
- [PR #20 — project handbook and contributor workflow](https://github.com/Gitcoder12/ARK/pull/20)
- [PR #12 — citation metadata](https://github.com/Gitcoder12/ARK/pull/12)

**Important:** The PR list is a repository-level snapshot; this audit does not assume a one-to-one mapping between every PR and branch. Check each PR's head/base, review state and CI before deciding what to merge. Branches marked behind have no unique commits in the comparison against the current `main`; retain them as history until reviewed rather than deleting them.

**Verification boundary:** This section records branch metadata and changed paths only. It does not certify code correctness, passing tests, safe behavior, or merge readiness. Re-run the relevant test suite on the exact proposed merge head before merging.
