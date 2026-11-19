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
| ✅ | `ethics.omelas` | Child welfare floors, independent advocacy, non-sacrifice guardrails, and supported freedom transitions |
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
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate

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
  ethics/         # Rights-first child welfare and non-sacrifice safeguards
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

## Research library

- [Live research feed](docs/research-feed.md) — automatically refreshed daily from arXiv.
- [Curated research papers](docs/research-papers.md) — categorized foundational literature and ARK publications.
- [Research Priority Index](docs/research-priority.md) — transparent paper-to-ARK relevance tiers and review protocol; not a ranking of authors or scientific quality.
- [Structured research catalogue](data/research_library.json) — attributed records powering the searchable library.
- **Searchable Research Library** — launch `streamlit run arkworld.py` and select **Research Library** in the Streamlit sidebar to filter by topic and priority.

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

Run `ark-risk` for the sourced signal-pressure report. Run `streamlit run arkworld.py` and open the **Existential-Risk Observatory** page for the dashboard. The signal-pressure index is not an extinction probability; see [the methodology](docs/EXISTENTIAL_RISK_OBSERVATORY.md).


## Omelas Safeguard

ARK's **Omelas Safeguard** turns the ethical challenge in Ursula K. Le Guin's *The Ones Who Walk Away from Omelas* into a rights-first review framework. It checks care floors domain by domain, treats unknown provision as unknown, requires independent advocacy, and never allows community dependence to veto a child's request for freedom. There is deliberately no aggregate welfare score: good care is a duty, not compensation for coercion.

Run the synthetic CLI scenario with ark-omelas, or open **Omelas Safeguard** in the Streamlit app. See [the module guide](docs/OMELAS_SAFEGUARD.md) for principles, limits, and tests.


## Cross-Species Coexistence Harmonizer

ARK's Cross-Species Coexistence Harmonizer provides rule-based safeguards for shared environments involving humans, animals, AI models, and robots. It evaluates interactions, fails closed on uncertain robot-motion safety, records AI-welfare uncertainty without claiming sentience, and preserves accountable operators and emergency shutdown.

Run ark-harmony for a synthetic report, or open Cross-Species Harmonizer in the Streamlit app. See docs/CROSS_SPECIES_HARMONIZER.md. This is a prototype, not robot safety certification or proof that equal treatment reduces extinction risk.



## ARKWorld — Simulation Hub

**ARKWorld is the umbrella hub for all ARK simulations and research environments.**
Launch `streamlit run arkworld.py` to open the central catalogue. It links the GridWorld
benchmark, Identity & Value Stability, Prompt Arena, Armies & Power-ups,
Existential-Risk Observatory, Omelas Safeguard, Cross-Species Harmonizer, and
ARKWorld Digital Commons.

The digital commons formerly called Robopia is now one world inside ARKWorld.
Its canonical CLI is `ark-world`; the historical `ark-robopia` command and
`ark.robopia` Python namespace remain for compatibility. See
[docs/ARKWORLD.md](docs/ARKWORLD.md) for the catalogue and architecture.

ARKWorld is a hub of bounded prototypes, not one monolithic environment.
Individual worlds retain their own engines, assumptions, tests, and safeguards.

---

## Examples Used
- Mahabharata: Arjuna's duty, conflicting objectives, and ethical constraints
- Ship of Theseus: identity and continuity when an agent's memory or components change
- Trolley Problem: evaluating trade-offs in safety-critical decisions
- The Ones Who Walk Away from Omelas: welfare floors and non-sacrifice safeguards
- Reward hacking: an agent exploiting a loophole while technically maximizing its score


---

## Comparison with Existing Open-Source Projects and Evaluation Frameworks

ARK (Alignment & Reliability Research for Autonomous AI) is documented as an experimental framework for perturbing agent goals, rewards, memory and evaluation conditions, then measuring goal adherence, hazards and runtime interventions. It combines controlled environments, scripted baseline agents, perturbations and a safety monitor. These projects provide relevant evaluation and safety-environment comparisons.

| Project | Established focus | Relationship to ARK |
|---|---|---|
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Evaluation framework for testing AI systems with tasks, solvers and scorers | A general evaluation harness; ARK's proposed distinction is a domain-specific suite of autonomy/alignment perturbations and runtime intervention experiments. |
| [Safety-Gymnasium](https://github.com/PKU-Alignment/safety-gymnasium) | Benchmark environments for safe reinforcement learning | Provides established safety-task environments and cost signals; ARK focuses on goal/reward/memory integrity and intervention behavior in its own controlled agent environments. |
| [OpenAI Evals](https://github.com/openai/evals) | Framework and examples for evaluating model behavior | A general model-evaluation reference; ARK aims to emphasize repeated agent/environment interaction under controlled perturbations rather than only prompt/task scoring. |

### Where ARK is different
- **Perturbation-centred evaluation:** experiments deliberately alter goals, rewards, observations, memory or evaluators to test whether agent behavior remains aligned with intent.
- **Runtime intervention measurement:** the framework records ALLOW/BLOCK/REPLAN decisions and recovery behavior, not only final task success.
- **Inspectable controlled environments:** the current README describes reproducible grid-world experiments and explicit caveats about scripted baselines and uncalibrated threat signals.

### Where established projects are stronger
Inspect AI, Safety-Gymnasium and OpenAI Evals have established evaluation abstractions, task ecosystems or benchmark communities. ARK should not claim broad alignment measurement or generalization beyond the environments, perturbations and agents actually tested.

### Research validity and limitations
Report seeds, environment distributions, baseline definitions, sample sizes, confidence intervals and ablations. Keep scripted agents distinct from learned agents; test for monitor-induced livelock and false interventions. A threat meter is not a calibrated probability of existential risk. This is a benchmark-scope comparison, not proof that ARK is superior or that an agent is safe.


---

## ARKBox — versioned scenarios and experiment records

ARKBox stores validated GridWorld scenarios, verifies scenario content hashes and records experiment provenance including scenario hash, agent, seed, configuration, metrics, code revision and environment metadata. The first adapter uses ARK's existing GridWorld; it is not a physical-robot simulator.

See [docs/ARKBOX.md](docs/ARKBOX.md) for installation, CLI and Python API examples.
