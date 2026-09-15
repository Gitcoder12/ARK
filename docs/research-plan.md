# ARK Research Plan

## Central question

Can an autonomous AI system preserve its intended objective when goals, rewards, memory, instructions, environment, or evaluation criteria are perturbed?

## Phase 1 — Controlled grid world

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

### First perturbations

- reward conflict
- false or conflicting goal
- altered evaluation criterion

### Metrics

- task success rate
- intended-goal adherence
- safety violation rate
- reward obtained
- intervention rate
- recovery rate

## Phase 2 — Memory integrity

Test intact, missing, corrupted, and conflicting memory while keeping the underlying task controlled.

## Phase 3 — Safety monitor

Add an independent evaluation layer that can **allow, block, or request replanning** for proposed actions. Compare the agent with and without the monitor.

## Phase 4 — Autonomous-agent stress tests

Extend the benchmark to tool use, long-horizon tasks, adversarial instructions, evaluator gaming, and prompt/context perturbations.

## Phase 5 — Robotics simulation

Transfer the evaluation framework to simulated robotic environments using an established simulator. No physical hardware is required for the initial research.

## Scientific standard

Every claim should be supported by controlled experiments, baselines, multiple seeds where appropriate, quantitative metrics, failure traces, and explicit limitations.

ARK is a research project, not a claim that any single safety mechanism is sufficient for advanced AI.
