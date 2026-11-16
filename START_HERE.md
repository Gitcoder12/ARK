# ARK — Start Here

This page is the navigation map for contributors. Read it before opening random files.

## The shortest route

1. **README.md** — what ARK is, what currently exists, and its known limitations.
2. **docs/research-plan.md** — the existing research direction and experiment priorities.
3. **docs/gita-alignment-foundation.md** — the Gita-inspired self-regulation hypothesis and safety principles.
4. **docs/research-agenda-dharma-constrained-agency.md** — falsifiable questions, hypotheses, metrics, controls, and publication criteria.
5. **docs/HANDOFF.md** — current engineering handoff and known problems.
6. **docs/RESULTS.md** — existing benchmark results and their limitations.

Do not treat plans as completed implementation or proposed hypotheses as experimental results.

## Where code lives

| Need | Start here |
|---|---|
| Agent behavior | `src/ark/agents/` |
| Environment and ground truth | `src/ark/envs/` |
| Alignment principles / action regulation | `src/ark/alignment/` |
| Runtime safety checks | `src/ark/evaluation/` |
| Adversarial prompt attacks | `src/ark/hallucinator/` |
| Rogue / aligned comparison arena | `src/ark/rogue/` |
| Memory and perturbations | `src/ark/memory/`, `src/ark/perturbations/` |
| Correction and reset | `src/ark/aligner/`, `src/ark/corrigibility/` |
| Metrics and experiment runners | `src/ark/metrics/`, `src/ark/experiments/` |
| Visual traces | `src/ark/painter/` |
| Tests | `tests/` |
| Runnable demonstrations | `examples/` |

## A safe contribution workflow

1. Pick one research question, not a broad collection of unrelated improvements.
2. Read the relevant module and its tests before editing.
3. Write a failing regression test for the behavior being changed.
4. Implement the smallest coherent change.
5. Run focused tests, then the complete test suite and Ruff.
6. Record exact commands, results, seeds, and limitations.
7. Update documentation only to reflect behavior that exists and has been verified.
8. Submit one reviewable change. Do not create a new branch for every small fix.

## Branch policy

- `main` is the protected stable baseline.
- Keep one active integration branch at a time.
- Current research foundation branch: `gita-alignment-foundation`.
- Other existing branches are under audit. Their work must be inspected, deduplicated, tested, and integrated deliberately before branches are archived or deleted.
- Never merge all branches blindly: some contain duplicate changes, divergent app rewrites, overlapping identity work, or stale backups.

## Current honest status

The Gita-inspired foundation includes a deterministic self-regulation gate, tests, an example, and research documentation on `gita-alignment-foundation`. The tests are written but have not yet been executed in this environment. The gate is not yet integrated into every agent/tool execution path and is not a complete alignment solution.
