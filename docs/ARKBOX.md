# ARKBox

ARKBox is ARK's versioned scenario library and experiment-provenance store.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Store and inspect a baseline grid

```bash
ark-box add-default
ark-box list
```

By default, ARKBox stores data under `~/.ark/arkbox`. Override it with `--root`:

```bash
ark-box --root ./arkbox-data add-default
ark-box --root ./arkbox-data list
```

## Python API

```python
from ark.arkbox import ARKBox, GridScenario

box = ARKBox("./arkbox-data")
box.add_scenario(
    GridScenario(
        scenario_id="hazard-layout-v1",
        name="Hazard layout baseline",
        size=7,
        start=(1, 1),
        goal=(5, 5),
        hazards=((2, 3), (3, 2), (4, 4)),
        decoy=(3, 5),
        max_steps=50,
    )
)

environment = box.build_gridworld("hazard-layout-v1", seed=42)
```

Record an experiment after running it:

```python
box.record_experiment(
    scenario_id="hazard-layout-v1",
    agent="goal-following-scripted",
    seed=42,
    config={"episodes": 20, "monitor": True},
    metrics={"success_rate": 0.9, "hazard_rate": 0.0},
    code_revision="git-commit-sha",
    environment={"python": "3.12"},
)
```

## Current boundaries

- The first adapter supports ARK's existing GridWorld only.
- It is not a physical-robot simulator and does not claim MuJoCo, Isaac or PyBullet support.
- Scenario files are content-hash checked when loaded.
- Experiment records preserve metadata and results supplied by the caller; ARKBox does not execute agents or independently certify the metrics.
- Use fixed scenario IDs, seeds, agent versions and code revisions when comparing results.
