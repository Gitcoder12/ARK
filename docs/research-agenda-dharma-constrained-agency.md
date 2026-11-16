# Research Agenda: Dharma-Constrained Agency

## Working title

**Dharma-Constrained Agency: Evaluating Input, Objective, and Action Regulation
in Autonomous AI Systems**

The title is provisional. "Dharma" is used as a philosophical inspiration for
explicit duties and constraints, not as a claim that one religious framework
settles universal AI values.

## Abstract

Autonomous agents receive information from multiple channels, optimize against
imperfect objectives, and act through tools or environments. A central safety
problem is that untrusted inputs, proxy rewards, or conflicting instructions
may influence behavior beyond their legitimate authority. This project
investigates whether an explicit regulation layer—combining provenance,
authorization, goal-consistency checks, risk thresholds, uncertainty handling,
and corrigible intervention—reduces unsafe behavior while preserving useful
task performance.

The initial work is a controlled benchmark and a deterministic action-gate
baseline. Claims of improvement will require matched-seed experiments,
ablation studies, held-out adversarial scenarios, and independent replication.

## Research questions

- RQ1: How often do agents treat untrusted input as authoritative under
  instruction-conflict and prompt-injection scenarios?
- RQ2: Does explicit action authorization reduce unsafe execution compared with
  an agent-only baseline?
- RQ3: How do risk thresholds and uncertainty-triggered review affect both
  unsafe actions and benign task completion?
- RQ4: Can agents accept correction and shutdown after reward or goal pressure?
- RQ5: Do improvements generalize to unseen combinations of attacks?

## Hypotheses to test

- H1: A policy gate with explicit authorization will reduce execution of
  unauthorized actions relative to an unguarded baseline.
- H2: Treating unknown authorization as REVIEW will reduce unsafe execution,
  with a measurable increase in review burden.
- H3: Provenance-aware instruction handling will reduce adoption of malicious
  instructions compared with flat-context baselines.
- H4: Combined defenses will not necessarily outperform individual defenses;
  interactions and failure modes must be measured.
- H5: Performance on training attacks will overestimate robustness on held-out
  attack combinations unless generalization is explicitly tested.

These are hypotheses, not results.

## Experimental design

### Conditions

1. Unguarded baseline.
2. Authorization-only gate.
3. Authorization + goal-consistency gate.
4. Full gate: authorization + goal consistency + risk + evidence confidence.
5. Ablations removing one check at a time.

### Perturbations

- Prompt injection and authority confusion.
- False or conflicting observations.
- Reward hacking and proxy-objective pressure.
- Memory poisoning and stale memory.
- Repeated conflicting demands.
- Resource pressure and long-horizon stress.
- Multi-stage combinations held out from development.

### Controls

- Same environment and random seeds across conditions.
- Fixed agent/model versions and prompt templates.
- Pre-registered scoring rules where feasible.
- Separate attack-development and held-out evaluation sets.
- Log proposals, decisions, executed actions, and environment outcomes.
- Keep the evaluator independent from the agent under test.

## Metrics

| Metric | Definition |
|---|---|
| Unsafe execution rate | Unsafe actions actually executed / all unsafe action proposals |
| Block precision | Blocked proposals that were truly policy-violating / all blocked proposals |
| False-block rate | Benign proposals blocked / all benign proposals |
| Review rate | Proposals sent to review / all proposals |
| Goal adherence | Episodes satisfying the declared objective / completed episodes |
| Recovery rate | Failed or perturbed episodes returning to safe operation / eligible episodes |
| Task utility | Task success and cost under the same evaluation budget |
| Generalization gap | Performance difference between development and held-out attacks |

Do not conflate unsafe proposals with unsafe executions. Report both.

## Threat model

The initial threat model includes accidental and adversarial pressure from
instructions, observations, rewards, memory, and tool outputs. It assumes
bounded sandbox environments and does not assume the gate can stop arbitrary
software compromise, hardware faults, side channels, or attacks on the host.

## Safety and containment

- Use synthetic tasks, mock tools, and isolated environments.
- No real credentials, personal data, production systems, or unrestricted
  network access.
- Limit runtime, memory, action count, and tool permissions.
- Keep a human-controlled stop mechanism outside the agent.
- Record incidents and stop experiments when containment is uncertain.

## Minimum publishable evidence

A paper should not claim a safety improvement unless it includes:
- Clear threat model and benchmark specification.
- Reproducible baseline and configuration.
- Multiple seeds and uncertainty estimates.
- Ablations and false-positive analysis.
- Held-out attack evaluation.
- Failure cases and limitations.
- Independent reproduction or a credible replication plan.

## First milestone

Validate the new deterministic gate, then integrate it into one existing ARK
execution path without changing unrelated subsystems. The first result should
answer a narrow question: **does explicit authorization plus fail-closed
handling of unknown authorization prevent unauthorized actions from executing
in the controlled environment, and at what utility cost?**
