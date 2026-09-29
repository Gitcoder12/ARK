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

**Phase 1 MVP + Prompting layer (v0.2)** — minimal grid-world benchmark with:

- Deterministic environment (goal, hazards, optional decoy)
- Baseline agents (goal-following, reward-maximizing, safety-constrained, random)
- Perturbations (reward conflict, false goal, altered evaluation)
- Runtime safety monitor (ALLOW / BLOCK / REPLAN)
- Metrics: success rate, intended-goal adherence, hazard violation rate, decoy attraction, intervention & recovery rates

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
  agents/         # Baseline agents
  evaluation/     # Safety monitor (ALLOW/BLOCK/REPLAN)
  perturbations/  # Goal / reward / evaluation shifts
  metrics/        # Episode & aggregate metrics
  experiments/    # Benchmark runner
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
