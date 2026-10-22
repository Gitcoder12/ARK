# ARK upgrade plan
Audit date: 2026-10-22. Written on branch `docs/upgrade-plan`.

## Current state (measured)
- 76 files, about 5,200 lines of Python under `src/ark`, 13 test files
- `pytest`: **101 passed** (about 9 s). `ruff check .`: clean
- CI exists: `.github/workflows/ci.yml` (push and PR to `main`, Python 3.11 and 3.12)
- Missing: type checking, a coverage gate, a reproducible results table in the README

## Goals, in order
1. **Reproducible results.** Add `make benchmark` (seeded) that prints a results table; the README shows that table.
   Done when a fresh clone reproduces the same numbers with a fixed seed in 3 commands.
2. **Honest, narrow claim.** README section "What ARK measures and what it does not", with a simple baseline to compare against.
   Done when every number in the README has a command that regenerates it.
3. **Plain-language summary.** Five lines at the top, no jargon: the problem, the method, the result.
4. **Quality gates.** Add mypy (start lenient, tighten module by module) and a coverage gate (>= 85%) to CI.
   Done when CI fails on a deliberate type error and passes on the branch without it.
5. **Packaging.** PyPI-ready `pyproject.toml` (metadata, classifiers, entry points). Done when `python -m build` succeeds.
6. **Decoy / false-target experiment (v0.6).** Write the hypothesis, metric and stopping rule in `docs/` BEFORE implementing.
   Implement behind a flag. Report the result even if it is negative.

## Out of scope until 1 to 4 are done
New attack families or new environments.

## Quality gate
`ruff check . && pytest` (plus mypy and coverage once added)

## Rules for any contributor or AI model working from this plan
1. Work on a **new branch** (for example `feat/<topic>`). Never push to `main`. Open a pull request.
2. Run the quality gate before every push. Paste the real test output into the PR description.
3. Do not claim anything you did not measure. No invented benchmarks, no placeholder numbers.
4. Small, focused commits. Take git identity from `git log -1`; never invent an email address.
5. Never commit secrets, tokens, raw data or generated artifacts.
6. When a task is finished, tick its box here and note the date and PR number.

## Status
- [ ] Not started
