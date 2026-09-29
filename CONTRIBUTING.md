# Contributing to ARK

Thank you for interest in alignment & reliability research.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Code style

- Python 3.11+
- `ruff check src tests`
- Prefer small, testable modules over large agents

## Adding experiments

1. New environments → `src/ark/envs/`
2. New agents → `src/ark/agents/`
3. New perturbations → `src/ark/perturbations/`
4. Register them in `experiments/runner.py`
5. Add tests under `tests/`

## Scientific bar

Every new claim should include:
- controlled baselines
- multiple seeds
- quantitative metrics
- explicit limitations
