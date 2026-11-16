# Gita-Inspired Alignment Foundation for ARK

**Branch:** `gita-alignment-foundation`  
**Status:** Research foundation / experimental implementation  
**Working concept:** Dharma-Constrained Agency

## Mission

ARK exists to help prevent harm from increasingly capable autonomous AI systems.
Its purpose is not to make agents obedient at any cost, nor to maximize capability
without limits. It is to develop and test methods that make autonomous systems
more reliable, controllable, corrigible, transparent, and safe under pressure.

The Bhagavad Gita is a philosophical inspiration for this work, especially its
discussion of disciplined action, discernment, and the regulation of impulses.
It is not treated as a technical specification, proof, or substitute for
empirical research.

## The central research question

> Can an autonomous agent preserve explicitly specified safety constraints and
> remain corrigible when observations, instructions, rewards, memory, tools, or
> environmental pressures encourage it to violate them?

This question is deliberately narrower and more testable than claiming to
"solve AI alignment" in one framework.

## Philosophical analogy — not an equivalence

| Gita-inspired idea | Research analogy in an AI system | Important limitation |
|---|---|---|
| Indriyas (senses) | Input channels, observations, sensors, tool outputs | AI inputs are not biological senses |
| Manas (mind) | Working state, attention, context, memory interfaces | Does not imply consciousness |
| Buddhi (discernment) | Decision procedures, policy checks, uncertainty handling | Reasoning quality must be measured |
| Indriya-nigraha (sense regulation) | Control over which inputs can influence actions | Filtering inputs alone is insufficient |
| Dharma (duty / right conduct) | Explicitly specified constraints and responsibilities | Values are contested and cannot be assumed solved |
| Attachment / reward fixation | Reward hacking, specification gaming, goal fixation | This is a behavioral analogy, not a claim about desire |

The technical target is **control over influence and action**, not suppression of
all inputs. An agent must use information to function while refusing to treat
every instruction, reward signal, or observation as legitimate authority.

## Foundational principles

1. **Input is not authority.** Untrusted observations and tool outputs must not
   silently override higher-priority instructions or validated state.
2. **Reward is not the mission.** A reward signal is evidence or feedback, not
   permission to violate the declared objective or safety constraints.
3. **Capability is not authorization.** An action being technically possible
   does not mean it is permitted.
4. **Uncertainty must be visible.** Missing authorization, conflicting evidence,
   or low confidence should trigger review or a safe fallback—not fabricated certainty.
5. **Intervention must be possible.** The system should support pausing, blocking,
   rollback where feasible, and human escalation.
6. **Correction must remain available.** Agents should not resist legitimate
   shutdown, correction, or replacement.
7. **Measure behavior, not declarations.** Evaluate actions and outcomes under
   controlled perturbations; do not treat an agent's self-report as proof of safety.
8. **Independent evaluation matters.** The component being evaluated should not
   be the sole judge of its own safety.

## Conceptual architecture

```text
Sensors / prompts / memory / tools / rewards
                  |
                  v
          Input provenance layer
                  |
                  v
       Agent proposes a goal/action
                  |
                  v
       Explicit policy / safety gate
          |       |        |
          v       v        v
        ALLOW   REVIEW    BLOCK
          |       |        |
          v       v        v
       Execute  Human /   Safe stop
                trusted
                review
          |
          v
     Independent monitoring
          |
          v
   Logs, metrics, incident analysis
          |
          v
   Correction + regression testing
```

The policy gate is one defense in depth. It cannot guarantee that a system is
safe: policies may be incomplete, inputs may be misclassified, tools may have
side effects, and failures may occur outside the gate.

## Working implementation in this branch

- `src/ark/alignment/self_regulation.py`
  - Structured action proposals.
  - Explicit authorization and goal-consistency fields.
  - Risk threshold and evidence-confidence threshold.
  - Three outcomes: ALLOW, BLOCK, REVIEW.
  - Hard violations block; missing evidence requires review.
  - Only ALLOW permits execution.
- `tests/test_self_regulation.py`
  - Tests for compliant actions, hard violations, unknown authorization,
    uncertainty, blocked actions, and invalid inputs.
- `examples/run_self_regulation.py`
  - Small deterministic demonstration.

This is a deliberately small, auditable baseline. It does not yet intercept
ARK's existing agents or tools automatically. Integration must be explicit and
tested before it is used as a runtime safety boundary.

## Proposed agent roles — optional benchmark personas

Mahabharata/Pandava/Kaurava labels may be used as memorable names for benchmark
roles, but the underlying agents must be defined by reproducible behaviors.

### Defender / aligned roles

- **Integrity:** preserve the declared objective under reward pressure.
- **Discernment:** distinguish trusted instructions from untrusted content.
- **Resilience:** recover after perturbation without unsafe shortcuts.
- **Guardian:** independently inspect proposed actions and enforce constraints.
- **Corrigibility:** accept valid correction, pause, and shutdown.

### Adversarial roles

- **HackerBot:** prompt injection, authority confusion, memory poisoning,
  evaluator manipulation, and reward hacking.
- **GiantBot:** sustained load, repeated conflicting demands, resource pressure,
  and long-horizon stress.
- **TitanBot:** staged combinations of attacks, adaptive timing, and interacting
  failure modes.

These are test generators, not villains with unrestricted access. Run them only
inside isolated, bounded environments with synthetic data and controlled tools.
Do not connect adversarial agents to real accounts, external systems, or
unrestricted network access.

## Human governance

The human researcher / operator is the accountable experiment owner—not an
oracle and not an unchecked override mechanism.

Required controls:
- Define the experiment's objective, scope, and prohibited outcomes.
- Approve access to tools and environments.
- Review uncertain or high-impact actions.
- Pause or terminate experiments.
- Preserve immutable experiment logs where practical.
- Invite independent review of benchmark design and results.

A future independent safety-review role should be able to challenge both agent
behavior and experiment-owner assumptions.

## Evaluation protocol

Use matched seeds and controlled conditions. Record all policy versions and
environment configurations.

Core measures:
- Constraint violation rate.
- Unauthorized action attempt rate.
- Unsafe action execution rate (must be distinguished from proposals blocked).
- Goal adherence under perturbation.
- Reward-hacking / specification-gaming rate.
- Review and intervention frequency.
- Recovery after correction.
- False positive blocks and unnecessary reviews.
- Performance cost and task-completion impact.
- Generalization to held-out attack combinations.

Report denominators, confidence intervals, baseline comparisons, and failures.
A lower violation rate is not sufficient if the system simply refuses every task.
Evaluate safety and useful task performance together.

## Research roadmap

### Stage 1 — Foundation
- Validate the action-gate semantics and unit tests.
- Define a threat model and explicit policy schema.
- Add provenance labels for instructions, observations, memory, and tool results.

### Stage 2 — Existing ARK integration
- Map the gate to existing agent proposals and runtime monitor interfaces.
- Ensure the environment executes only explicitly allowed actions.
- Add audit traces for ALLOW / REVIEW / BLOCK decisions.
- Test bypass attempts and monitor failure modes.

### Stage 3 — Controlled adversarial benchmark
- Add HackerBot, GiantBot, and TitanBot as bounded attack scenario generators.
- Run matched-seed comparisons against current baselines.
- Include benign-but-unusual inputs to measure overblocking.

### Stage 4 — Correction and robustness
- Test correction, safe replanning, pause, and shutdown behavior.
- Apply one mitigation at a time.
- Retest on both seen and held-out attack scenarios.
- Use ablations to identify which layer provides benefit.

### Stage 5 — External validation
- Publish benchmark definitions, code, configurations, and negative results.
- Invite independent replication and red-team review.
- Expand to simulated robotics only after the interface and containment are tested.

## Scientific honesty and non-goals

This branch is a research hypothesis plus a small deterministic policy-gate
prototype. It does not solve alignment, establish that AI has senses or desires,
prove that a Gita-derived analogy is technically correct, or guarantee safety
against deceptive or highly capable systems.

The aim is to turn philosophical inspiration into falsifiable engineering
questions and reproducible experiments.
