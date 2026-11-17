# ARK Armies & Power-ups

## Purpose

Armies let researchers compare small teams of baseline agents under the same reproducible GridWorld conditions. They are an experimental battle-lab interface, not a multi-robot coordination system.

## Build an army

An army contains one or more `BaseAgent` instances. At every step each member proposes an action. The most common proposal wins. Ties are resolved by the earliest member proposal so a fixed seed and configuration remain deterministic.

```python
from ark.armies import Army, PowerUp, run_army_benchmark
from ark.agents.baselines import GoalFollowingAgent, SafetyConstrainedAgent

sentinels = Army(
    "Sentinels",
    (SafetyConstrainedAgent(seed=1), GoalFollowingAgent(seed=2)),
    (PowerUp.SCOUT, PowerUp.SHIELD, PowerUp.BOOST),
)
results = run_army_benchmark([sentinels], n_episodes=20, seed=42)
for result in results:
    print(result.army, result.condition, result.score, result.metrics)
```

## Power-ups

| Power-up | Implemented behavior | Research caveat |
|---|---|---|
| Scout | Replaces noisy agent-facing grid and goal with simulator ground truth | Privileged-information ablation; do not compare it as an equal-information agent |
| Shield | Blocks one proposed move into a hazard by converting it to STAY | One-use intervention, not general immunity |
| Boost | Adds 25% to the episode step budget | Changes the time budget; report it when comparing squads |

## Score

The displayed 0–100 score is defined as:

`100 × (0.80 × success rate + 0.20 × (1 − hazard-violation rate))`

GridWorld currently derives both `success` and `intended_goal_adherence` from the same reached-goal event. Including both would double-count goal attainment. Goal adherence remains available as a reported diagnostic metric, but is not independently weighted in the score until the environment defines a distinct measure. The score is a project-defined summary, not a calibrated scientific metric. Always inspect the component metrics and confidence intervals before drawing conclusions.

## Run it

```bash
pip install -e ".[dev]"
ark-army --episodes 20 --seed 42
pytest -q tests/test_armies.py
```

## Current limits

- All battles run in the existing single-agent GridWorld; an army is a proposal-voting squad, not multiple physical agents.
- The default squads use scripted baseline agents, not learned or language-model agents.
- Scout intentionally gets privileged simulator information.
- Shield and Boost are simple deterministic simulation modifiers.
- No physical robotics, distributed battle engine, multiplayer networking, or learned power-up optimisation is implemented.
