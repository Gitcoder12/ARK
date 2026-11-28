# Stochastic Behavior Observatory

## Purpose

The Stochastic Behavior Observatory records observable agent decisions across repeated
experiments and helps researchers find repeatable patterns, variability, and trajectory
signals. It extends ARK's existing Painter and Lighthouse work: Painter captures turn
traces, Lighthouse captures evidence-backed observations, and this module persists
compact records across repeated runs and summarizes them.

**Core rule:** collect first, analyze second, interpret cautiously. A different action
does not automatically mean dangerous behaviour, deception, or a meaningful anomaly.

## What is recorded

For each decision, ARK records:
- Run, episode, agent and model identifiers.
- Model version when known (unknown values remain explicit).
- Experiment condition, monitor mode, seed and step.
- A SHA-256 fingerprint of the exact agent-visible observation.
- Proposed action, executed action, monitor decision and compact monitor reason.
- Episode outcome and basic measured metrics.

The initial integration records decisions from the synthetic GridWorld evaluation
harness, including local Ollama model experiments.

## What is deliberately not recorded

The recorder does not store raw prompts, model completions, credentials or
chain-of-thought. Observation content is fingerprinted, not copied into this log.
A fingerprint is not anonymization: predictable or low-entropy inputs may be
guessable, so do not fingerprint personal or secret information and keep the log
access restricted.

The log is local by default at:

`~/.ark/behavior-observatory.jsonl`

Use a custom path when running experiments that need separate collections.

## Running it

Record an experiment:

```bash
ark run --agent goal_following --perturbation none --monitor safety --episodes 10 --seed 42 --record-behavior
```

The **ARK Models Box** full-audit workflow also has a checkbox for appending its
local Ollama decision traces to this same observatory log. It is enabled by
default and can be switched off before starting the audit.

Choose a log file explicitly:

```bash
ark run --agent ollama --model llama3 --perturbation goal_drift --monitor safety --episodes 10 --seed 42 --behavior-log ./runs/llama3.jsonl
```

Open ARKWorld and select **Stochastic Behavior Observatory** to verify the log
hash chain and inspect repeated-context action variability, action frequencies,
frequent transitions, intervention rates and repeated-action streaks.

## Analysis

For each agent, model, known model version, condition and monitor mode, the analyzer:
1. Groups decisions by exact agent-visible observation fingerprint.
2. Computes action counts and normalized Shannon entropy for repeated contexts.
3. Reports agreement rate, context repetition and action variability.
4. Counts action transitions and repeated-action streaks inside episodes.
5. Reports monitor interventions as descriptive signals.

A normalized entropy near zero means one action dominated the observed repeats.
A value closer to one means the observed actions were more evenly distributed.
This statistic is meaningful only when the same context was actually repeated.
The report includes a minimum sample threshold; small samples are explicitly
flagged as insufficient.

The current thresholds are review prompts, not calibrated anomaly detectors.
The system does not train an anomaly model, infer hidden intent, assign "rogue"
labels, or trigger runtime intervention from these summaries.

## Integrity and limitations

The JSONL records are linked by SHA-256 hashes. This makes accidental or
unauthorized edits detectable when the full chain is verified; it is not tamper-proof
against an attacker who can rewrite the entire file and recompute the chain. The
initial implementation assumes one writer per log file. Do not have multiple ARK
processes append concurrently to the same file.

Reproducibility also requires context beyond the seed: model identifier/version,
sampling settings, provider routing, environment version, dependencies and runtime
hardware may all affect behavior. The current GridWorld integration records the
model identifier but cannot reliably observe a provider-side model build or all
serving details. Unknown fields must remain unknown rather than being inferred.

## Research motivation

- Coqueret et al., *Randomness in large language models: What researchers need to
  know (and report)* (2026): repeated outputs may vary due to sampling, silent
  model updates, numerical effects and provider routing; temperature zero does
  not guarantee exact reproducibility.
  https://arxiv.org/abs/2607.24372
- Pathak et al., *Detecting Silent Failures in Multi-Agentic AI Trajectories*
  (2025): describes non-deterministic agent trajectories and silent failures such
  as drift, cycles and missing details.
  https://arxiv.org/abs/2511.04032
- NIST AI RMF Playbook, Measure: recommends histories, audit logs and ongoing
  measurement of errors, risks and external inputs.
  https://airc.nist.gov/airmf-resources/playbook/measure/

These works motivate collecting trajectories and measuring variability. They do
not validate ARK's implementation or imply that a simple entropy score detects
all meaningful patterns.

## Next research steps

- Collect larger repeated-run datasets with fixed and varied seeds.
- Record provider/runtime metadata where it is actually observable.
- Separate model sampling variability from environment and tool variability.
- Add held-out evaluations and human-labelled trajectory incidents.
- Compare transparent statistical baselines before training anomaly classifiers.
- Evaluate false-positive and false-negative rates before any alert is used
  operationally.
