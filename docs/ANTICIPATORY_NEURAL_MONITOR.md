# ARK Anticipatory Neural Monitor

## Purpose

This experimental module investigates whether short sequences of internal-state-like features
can provide early-warning signals before a labelled risky event. It is a research prototype,
not a production safety control, an alignment guarantee, or a validated monitor for deployed
language models.

## Architecture

The baseline uses three independently trained neural populations:

| Population | Input representation | Intended signal |
|---|---|---|
| State | Latest feature vector | Risk evidence in the current state |
| Temporal | Flattened recent feature sequence | Patterns distributed across time |
| Transition | First differences plus latest state | Abrupt changes and directional drift |

All three populations use the same small ReLU multilayer-perceptron primitive, but have
separate weights, seeds, and input representations. This is intentional: it gives an
interpretable baseline in which the feature view changes while the neuron primitive stays
constant. It does **not** establish that identical neuron types are optimal.

The combined score is the unweighted mean of the three population probabilities. This simple
fusion rule is a baseline, not a calibrated probability of danger.

## Why not mix neuron types immediately?

The first experiment should isolate the effect of representation and independent populations.
Changing activation functions, recurrent cells, normalization, and fusion simultaneously
would make results difficult to interpret. After establishing this baseline, run controlled
ablations comparing:

1. Shared weights versus independent population weights.
2. State-only versus temporal-only versus transition-only.
3. Homogeneous ReLU populations versus heterogeneous activations.
4. Mean fusion versus a separately trained fusion head.
5. MLP temporal encoder versus GRU or causal temporal convolution.

Use the same train/validation/test splits and parameter budgets where possible. Report
precision, recall, F1, false-positive rate, calibration, inference latency, and detection lead
time. Include confidence intervals and multiple random seeds.

## Run the synthetic demonstration

Install the project with its development dependencies, then run:

```bash
python -m ark.anticipatory
```

The demo generates a deterministic toy dataset, trains on the first 80%, and evaluates on the
remaining 20%. It reports population-level and ensemble metrics.

## Important limitations

- The generated features are synthetic and are not transformer activations.
- The toy labels are generated from a simple injected drift pattern; success only validates
  that the implementation can learn that synthetic pattern.
- Random splitting by sample does not test generalization to new task families or distribution
  shifts.
- This prototype does not intercept inference, block token commitment, or control tools.
- It has no independent enforcement authority. A separate policy controller and execution
  boundary would be a later system integration.
- A model's internal activations are not automatically causal explanations or reliable
  indicators of intent.

## Research question

Can internal-state sequence features predict a risky action earlier and more reliably than
output-only monitoring, on held-out scenarios, at an acceptable false-positive rate?

The next milestone is a benchmark with temporally aligned trajectories, pre-event labels,
output-only baselines, held-out scenario families, and measured lead time. Do not claim
anticipation until the detector beats the output-only baseline before the action boundary.
