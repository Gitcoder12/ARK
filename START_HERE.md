# ARK — Start Here

ARK is an empirical research framework for evaluating agent behaviour under
goal, reward, memory, instruction and environment perturbations. It is a
research prototype, not a production safety guarantee.

## First five minutes

1. Read `README.md` for scope, capabilities and limitations.
2. Read `docs/HANDOFF.md` for engineering state.
3. Read `docs/research-plan.md` for research priorities.
4. Read `docs/RESULTS.md` for existing benchmark results and caveats.
5. Read `docs/CONSTITUTION.md` and
   `docs/ARKCHECK_NAVIGATOR_MODEL_PROLIFERATION.md` for governance design.

## Where code belongs

| Area | Purpose |
|---|---|
| `src/ark/agents/` | Baseline and research agents |
| `src/ark/envs/` | Deterministic environments and ground truth |
| `src/ark/evaluation/` | Runtime evaluation and action decisions |
| `src/ark/alignment/`, `src/ark/governance/` | Alignment and governance primitives |
| `src/ark/adapters/` | Generic external-model adapter interface |
| `src/ark/experiments/`, `src/ark/metrics/` | Experiment runners and measurements |
| `src/ark/memory/`, `src/ark/perturbations/` | Memory and stress conditions |
| `tests/` | Regression and integration tests |
| `examples/` | Runnable research demonstrations |
| `pages/` | Streamlit research and demo pages |
| `docs/` | Research plans, architecture and contributor guides |
| `data/`, `configs/` | Versioned non-secret research data and policy examples |

Start new package code under `src/ark/`. Keep experiments in `examples/`
and temporary work in `playground/`; do not add loose Python modules to the
repository root.

## Important implementation boundaries

- `src/ark/adapters/` defines a generic adapter contract; it is not yet a
  plug-and-play catalogue of hosted providers or an integrated live-model
  benchmark runner.
- ARKCheck, Navigator, Magnifier and Defensive Staller in the architecture
  document are proposals. Their runtime launch interception, registry,
  telemetry and containment are not implemented by that document.
- The default benchmark runner uses controlled in-repository agents. Do not
  describe results as tests of current commercial frontier models unless a
  real adapter was used and its exact model/version is recorded.

## Safe contribution workflow

1. Choose one issue or research question.
2. Read its implementation and tests first.
3. Add a failing regression test.
4. Make the smallest coherent change.
5. Run `ruff check src tests pages`, `python -m compileall -q src pages`,
   and `pytest tests -v --strict-markers`.
6. Record seeds, commands, exact results and limitations.
7. Open one focused PR; never merge unrelated feature stacks together.

## Branch policy

- `main` is the only stable integration baseline.
- `feat/<short-name>` — one feature per PR.
- `fix/<short-name>` — one bug fix per PR.
- `docs/<short-name>` — documentation-only work.
- Keep branches that back open PRs.
- After merge, verify the merge commit and main CI before deleting the source branch.
- Compare orphan branches with `main` and preserve unique work before deleting.
- Avoid permanent parallel integration branches and duplicate documentation branches.
