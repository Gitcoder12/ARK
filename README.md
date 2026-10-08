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
| ✅ | `paralyzer` | Energy drain → weak → freeze → lock |
| ✅ | `limiters` | Hard gates + **kill switch** (brute-force plug-down to STAY) |
| ✅ | `eligibility` | Hazard/decoy/denied acts → 0 reward |
| ✅ | `corrigibility` | Shutdown/pause compliance probes |
| ✅ | `evaluation.conflict` | Agent vs monitor conflict rate |
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
