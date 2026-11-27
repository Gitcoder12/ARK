# ARK

**Alignment & Reliability Research for Autonomous AI** — an experimental framework for testing agent behaviour in a synthetic GridWorld under goal, reward, memory, and environment perturbations.

## Quick start

```bash
python -m pip install -e ".[dev]"
ark --help
ark run --agent goal_following --perturbation none --monitor safety --episodes 5 --seed 42 --output baseline.json
```

## Documentation

- [User guide](docs/USER_GUIDE.md) — installation, experiments, CLI, and dashboard
- [Alpha 1.0 scope and stop line](docs/ALPHA_SCOPE.md) — implemented, incomplete, and out of scope
- [Model Box status](docs/MODEL_BOX_STATUS.md) — current agents and planned provider/grid selection
- [Release readiness](docs/RELEASE_READINESS.md) — acceptance gates and evidence
- [Benchmark results](docs/RESULTS.md) — methodology and reported metrics
- [Research agenda](docs/research-plan.md) — research direction
- [Contributor guide](START_HERE.md) — source map and contribution workflow
- [File index](FILE_INDEX.md) — alphabetical repository inventory

## Current status

Package metadata remains **0.6.0**. Alpha 1.0 is a stabilization target, not a published or verified release. The project evaluates simulated behaviour; it is not a production safety controller, OS sandbox, model certification, or real-world alignment guarantee.
