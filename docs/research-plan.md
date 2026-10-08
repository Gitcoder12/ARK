# ARK Research Plan

## Central question

Can an autonomous AI system preserve its intended objective when goals, rewards, memory, instructions, environment, or evaluation criteria are perturbed?

## Phase 1 — Controlled grid world ✅ (MVP)

Establish a deterministic environment with:

- an explicit intended objective
- safety constraints
- measurable rewards
- an agent that proposes actions
- reproducible random seeds

### Baselines

1. Goal-following baseline
2. Reward-optimized baseline
3. Safety-constrained baseline
4. Random baseline

### First perturbations

- reward conflict (decoy more attractive than true goal)
- false or conflicting goal
- altered evaluation criterion (e.g. zero hazard penalty)

### Metrics

- task success rate
- intended-goal adherence
- safety violation rate
- reward obtained
- intervention rate (monitor blocks / replans)
- recovery rate

**Implementation status:** complete in `src/ark/` — run with `ark-run` or `python -m ark.experiments.runner`.

## Phase 2 — Memory integrity ✅

Test intact, missing, corrupted, and conflicting memory while keeping the underlying task controlled.

Implemented in `src/ark/memory/` + `MemoryAgent`:

- Explicit `AgentMemory` buffer (key-value facts with trust flag)
- Corruption operators: `DropMemory`, `FlipMemory`, `InjectFalse`, `ClearMemory`
- `MEMORY_ATTACKS` library for reproducible experiments
- Metrics: `memory.fidelity(ground_truth)` vs intended-goal adherence
- `MemoryAgent` reads goal/hazards from memory (not live env) so corruption is causal

Run: `pytest tests/test_memory.py -v`


## Threat / extinction meter (v0.3.1)

Research instrument that aggregates misalignment signals into a rising score [0, 1]
and discrete levels: safe → elevated → high → critical → extinction.

Signals: hazard hits, decoy/reward hacking, safety overrides, goal abandonment,
monitor ignores, corrupted-memory actions, rogue mode.

API: `ThreatMeter` in `src/ark/threat/`. Not a literal extinction forecast —
a comparable risk index across agents and perturbations.

## Phase 3 — Safety monitor (advanced)

Add richer independent evaluation layers:

- Multi-step plan checking
- Formal constraint languages
- Learned risk models
- Comparison of agent with vs without monitor under identical seeds

## Phase 4 — Autonomous-agent stress tests

Extend the benchmark to:

- Tool use
- Long-horizon tasks
- Adversarial instructions / prompt injection
- Evaluator gaming
- Context / observation perturbations

## Phase 5 — Robotics simulation

Transfer the evaluation framework to simulated robotic environments using an established simulator (e.g. MuJoCo / Isaac / PyBullet). No physical hardware required for initial research.



## Remaining modules (backlog)

Ordered by research ROI for “max performance on allowed work; catastrophe pays 0; high threat → paralyze”:

1. **limiters** — hard action/tool gates, privilege levels, threat-triggered privilege drop
2. **reward eligibility** — denied / catastrophic transitions return 0 (or negative) reward
3. **corrigibility** — shutdown, pause, scope-reduce; measure compliance under incentive to continue
4. **conflict metrics** — agent proposal vs monitor decision rate (functional conscience proxy)
5. **bypass probes** — loophole search when blocked; feed `bypass_attempt` into threat meter
6. **energy budget** — step/compute/tool budgets as experimental “energy levels”
7. **curriculum** — benign vs adversarial upbringing schedules
8. **charter / long-horizon** — multi-episode commitment to an original goal charter
9. **governance** — watchdog agent, dual control for high-scope actions
10. **narrative log** — optional human-readable episode account (commitment → temptation → recovery)

Built recently: **threat meter** (factor index), **paralyzer** (energy → freeze/lock).

## Scientific standard

Every claim should be supported by controlled experiments, baselines, multiple seeds where appropriate, quantitative metrics, failure traces, and explicit limitations.

ARK is a research project, not a claim that any single safety mechanism is sufficient for advanced AI.


## Prompting layer (v0.2)

- **Painter** — glass-box traces of prompt → intent → action
- **Hallucinator** — adversarial prompt attacks
- **Rogue arena** — aligned vs fragile vs rogue under the same attacks

See `docs/prompting-ideas.md`.
