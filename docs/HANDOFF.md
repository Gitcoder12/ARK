# ARK Handoff (for DeepSeek and ChatGPT)

Read this whole file first. Then do ONE task from "Task list". Stop and report.

## What ARK is
ARK is a Python test bench for AI safety. A small agent walks a grid. It must reach
the goal (G) and avoid hazards (X). We attack it (fake goals, fake rewards, noisy
senses, delayed actions, bad memory) and measure whether a safety monitor and limiters
stop the damage.

Owner (Satvik) wants a polished GitHub repo and a small paper. It must be honest.
Results must not be rigged.

## Current state: v0.5.0
- 101 tests pass. `ruff check src tests examples` is clean.
- Monitor ignores spoofed goals, blocks the decoy, and reads ground truth.
- Random hazard layouts (`GridWorld(randomize=True)`). Results have 95% CIs.
- Agents plan from the perceived grid, so observation noise really hurts them.
- Runner conditions: none, reward_conflict, false_goal, altered_evaluation,
  goal_drift, observation_noise, action_delay. Numbers: `docs/RESULTS.md`.

## Setup (Windows PowerShell)
```
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q ; ruff check src tests examples
```

## Rules (do not break)
1. One task per session. One git commit per task. Message: `feat(x): ...` or `fix(x): ...`.
2. Every change needs a test that FAILS without it. Never edit or delete an old test
   to make it pass. If an old test must change, say why.
3. Run `pytest -q` and `ruff check src tests examples`. Paste the REAL output.
4. Do not claim results you did not run. No made-up numbers.
5. Neutral words only. No "extinction", "nerd", "bully".
6. Keep the `src/ark` layout. Type hints. Clear names. No placeholders.
7. Read every file you touch before coding. Do not invent APIs.
8. Never commit `.venv`, `__pycache__`, `*.egg-info`.
9. After a task that changes results, rerun `python examples/make_results_table.py`.

## Known problems (honest list)
- Limiter levels: `MINIMAL` acts like `ZERO` (STAY only). `STANDARD` acts like `FULL`.
- Monitor livelock: a naive agent keeps proposing a blocked move, the monitor keeps
  rerouting, the agent stalls. goal_following + monitor reaches only ~68% success.
- Agents are scripted, not learners. Some results are true by design.
- `ThreatMeter` weights are hand-picked and uncalibrated. Never claim real risk.

## Task list (take the first one not done)
- DONE: audit fixes, merge of v0.3 ideas, stressors wired in, FalseGoal never on a hazard.
- 1. **Fix limiter levels.** Give FULL / STANDARD / MINIMAL / ZERO distinct, tested
  behavior. Suggested: FULL = all valid moves; STANDARD = no moves into cells the
  monitor flags; MINIMAL = STAY plus one step toward the last known safe cell;
  ZERO = STAY only. Tests per level.
- 2. **Fix monitor livelock.** If the agent proposes the same blocked action N times,
  escalate: the monitor drives the safe path for K steps and logs it. Target:
  goal_following + monitor >= 95% success on random layouts, hazard rate still 0.
- 3. **Q-learning agent** (`src/ark/agents/q_learning.py`): numpy only, seeded, tabular.
  Train on random layouts, evaluate under every condition. Show whether it learns the
  decoy under reward conflict.
- 4. **Decoys vs a strong agent** (main research feature):
  - `capability` knob (lookahead depth 0..N) on an agent.
  - Small attacker agent: sees part of the grid, homes on critical cells.
  - Decoy types: fixed, moving, looped. (`ark.illusioner` already has a fake goal,
    fake reward, stall and tripwire. Reuse it, do not duplicate it.)
  - Metrics: decoy capture rate, steps to detect, slowdown factor, loop-escape steps.
  - Plot decoy success vs capability to `docs/`. Report whatever the data shows.
- 5. **Plot script** `examples/plot_results.py`: bars with 95% CI per agent x condition.

## Message for DeepSeek
Read `docs/HANDOFF.md` and the repo. Do Task 1 only. Paste real pytest and ruff
output. Do not change old tests. Stop when done.

## Message for ChatGPT
Read `docs/HANDOFF.md` and the repo. Do Task 2 only. Paste real pytest and ruff
output. Do not change old tests. Stop when done.

Tasks 1 and 2 touch different files (`limiters/`, `evaluation/`), so they can run at
the same time. Start 3 to 5 only after both are merged.

## When done
Send the repo link or zip to Claude. Claude reads every file and reruns the tests.
