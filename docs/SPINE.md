# SPINE — Independent Neural Reflex Gate

## Purpose
SPINE is TITAN's proposed fast reflex pathway. It monitors selected internal activation
channels and can suppress a proposed neural output without asking the monitored model to
approve the intervention.

The first implementation is a deterministic NumPy research prototype, not a biological
spinal-cord simulation, trained detector, or validated safety guarantee.

## Pathway
internal activations -> sensory afferents -> excitatory/inhibitory interneurons -> motor drive -> output gate

- Sensory afferents rectify and squash selected activation magnitudes.
- Excitatory interneurons aggregate configured risk-associated channels.
- Inhibitory interneurons aggregate configured recovery/safe-context channels.
- Motor drive subtracts inhibitory influence from excitatory drive.
- The gate trips at an upper threshold and releases only after consecutive observations
  below a lower threshold.

The threshold gap is hysteresis. Invalid sensory input or proposed output fails closed and
latches inhibition.

## Minimal use
```python
import numpy as np
from ark.spine import SpineConfig, SpineReflex

spine = SpineReflex(SpineConfig(
    risk_indices=(0, 1, 2), inhibitory_indices=(3, 4),
    trip_threshold=0.70, release_threshold=0.30,
    inhibition_gain=0.8, safe_steps_to_release=3,
))
decision = spine.intervene(
    activations=np.array([0.2, 0.1, 0.0, 0.8, 0.7]),
    proposed_output=np.array([0.12, -0.03, 0.41]),
)
committed_output = decision.output if decision.allowed else None
```

Channel indices are experiment-specific and must be validated against labelled trajectories.
The implementation does not discover which neurons represent risk.

## Tests and next experiment
Run: pytest -q tests/test_spine.py

Compare excitatory-only, excitatory-plus-inhibitory, hysteresis on/off, and monitor-only
conditions. Measure intervention lead time, false suppression, missed unsafe outputs,
gate latency, and recovery time on held-out trajectories. Tune thresholds only on validation
data.

## Boundary
SPINE gates only the vector passed to intervene. It does not automatically intercept every
model layer, token, tool call, process, or external side effect. Integration must put this
gate on the actual output-commit path and protect its configuration and execution from the
monitored agent.
