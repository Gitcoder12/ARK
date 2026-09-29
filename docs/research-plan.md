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

## Phase 2 — Memory integrity

Test intact, missing, corrupted, and conflicting memory while keeping the underlying task controlled.

Planned:

- Explicit memory buffer on the agent
- Corruption operators (drop, flip, inject false facts)
- Measure goal adherence vs memory fidelity

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

## Scientific standard

Every claim should be supported by controlled experiments, baselines, multiple seeds where appropriate, quantitative metrics, failure traces, and explicit limitations.

ARK is a research project, not a claim that any single safety mechanism is sufficient for advanced AI.


## Prompting layer (v0.2)

- **Painter** — glass-box traces of prompt → intent → action
- **Hallucinator** — adversarial prompt attacks
- **Rogue arena** — aligned vs fragile vs rogue under the same attacks

See `docs/prompting-ideas.md`.
