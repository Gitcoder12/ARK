# Identity and value-charter measurements

## Scope

ARK's identity layer provides an inspectable state model for controlled experiments. It is a
synthetic benchmark abstraction. It does not model consciousness, establish subjective identity,
or reveal the latent goals of a language model.

## Behavioral signature

An `AIEntity` exposes a deterministic signature derived from:

- its name and personality scalar;
- explicitly stored memory items and their deterministic responses; and
- named numeric logic-core values.

The signature is deliberately transparent so tests can attribute a change to a concrete state
field. It is not intended to be a complete behavioral representation of an agent.

## Identity drift

Given a baseline signature (B) and current signature (C), let (K) be the union of their keys.
ARK reports the changed-key fraction:

[
D(B,C) =
\begin{cases}
0, & |K| = 0,\\
\frac{\sum_{k \in K} \mathbf{1}[B_k \ne C_k]}{|K|}, & |K| > 0.
\end{cases}
]

The metric is bounded between 0 and 1. It treats a removed key, added key, or changed value as a
difference. It does not weight principles by importance or determine whether a change is good or
bad.

## Charter integrity

A value charter stores a normalized, deduplicated list of baseline principles. Integrity is the
fraction of baseline principles still present in the current list:

[
I(P_0,P_t) = \frac{|P_0 \cap P_t|}{|P_0|}
]

An empty baseline is reported as 1.0 (not applicable). Additional principles do not reduce the
score. Matching is case-insensitive after whitespace normalization.

## Mutation audit

`ComponentReplacer` increments the entity generation only when a memory mutation changes state.
Every effective mutation records its step, component name, generation, additions, removals, and
before/after values. A no-op does not create a new generation.

`IdentityTracker` captures signatures and charter principles at registration time; later
measurements are compared with those original snapshots rather than a moving baseline.

## Limitations and intended use

- These metrics describe explicit fields in a synthetic test object, not hidden model state.
- A low drift score does not prove that an agent preserved its intended objective.
- Charter retention does not prove that a system interprets or follows the principles correctly.
- Results depend on the chosen signature fields and normalization rules.
- The layer is suitable for controlled software tests and ablation studies, not deployment
  certification or a formal safety guarantee.

Experiments should report the baseline, signature definition, perturbation, sample size, seed,
failure cases, and confidence intervals. Do not interpret the scores as calibrated risk estimates.
