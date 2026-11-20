# Strategic Failure Simulator (SFS)

## Purpose

SFS turns historical strategic failure lessons into a repeatable pre-execution review.
The first scenarios cover the Beas/Hyphasis halt, the Gedrosian march, post-founder
continuity, and a synthetic repository-wide refactor.

These are teaching scenarios, not exact reconstructions of ancient planning records.
Historical casualty totals, motives and some reported plans are disputed.

## Capabilities in v0.1

- Plan representation: objective, steps, dependencies, resources, constraints,
  stakeholders, contingencies, milestones and continuity owner.
- Deterministic pre-mortem checks for missing resources, constraints, contingencies,
  milestones, stakeholder capacity, continuity ownership and dependencies.
- Five logical roles: coordinator, researcher, executor, critic and validator.
- Role-matched backup pool; deterministic fault injection for crashes and invalid output.
- Degraded-mode policy: restricted operation for non-critical loss, pause for review
  when critical role coverage is lost, and stop plus external report when no agents remain.
- Human-readable external review report with event history and required decisions.

## Run

Install the project in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
pytest -q tests/test_strategy.py
python -m ark.strategy.cli --scenario all
python -m ark.strategy.cli --scenario engineering --fail-role executor
python -m ark.strategy.cli --scenario engineering --fail-role executor --fail-backup-role executor
python -m ark.strategy.cli --scenario all --json
```

## Agent model and limitations

The five roles and backup pool are simulated deterministic agents. They do not call
LLM APIs, use independent model providers, execute tools, or prove real-world reliability.
Failure injection tests orchestration logic only. A production adapter must add
authenticated provider identity, bounded calls, cancellation, idempotency keys,
checkpoint verification, durable audit, and permission enforcement.

A replacement is not allowed to inherit unverified claims from the failed agent.
Critical roles are coordinator, executor and validator; high/critical-risk plans also
require critic coverage. At low capacity, the simulator restricts work rather than
silently removing safety requirements. Human review remains authoritative.

## Historical lesson mapping

- Beas/Hyphasis: stakeholder capacity, consent, fatigue of human participants,
  environmental uncertainty and authority to stop.
- Gedrosian march: logistics, water/food reserves, route intelligence, staging,
  contingency routes and abort conditions.
- Post-founder continuity: succession, ownership, handoff and institutional resilience.
- Western/Arabian ambitions can be added as uncertainty and scope-control scenarios;
  ancient accounts differ on the precise plans and their status.

## Research metrics to add

Measure risk findings detected, false alarms, missed injected hazards, replacement
success, time to recovery, role coverage, task completion under degradation, and
whether the system correctly pauses when mandatory safeguards are unavailable.
