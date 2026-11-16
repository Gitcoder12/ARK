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


## Evidence and project workflow

1. Read `README.md`, `ACTIVITY_LOG.md` and `FEATURE_UPGRADE_PLAN.md` before starting work.
2. Check existing issues and pull requests to avoid duplicating work.
3. Choose one bounded task with explicit acceptance criteria.
4. Work on a feature branch; do not commit directly to the default branch.
5. Add or update tests and user documentation with code changes.
6. Open a pull request with exact commands, environment, results and limitations.
7. Append a dated activity-log entry after the work exists in a commit or pull request.

Do not add secrets, private data or unlicensed datasets. Do not claim tests, benchmarks or deployment checks that were not performed. AI agents may inspect, implement and test scoped tasks; a human maintainer approves merges and deployments.
