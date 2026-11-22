# ARK unified evaluation CLI

The installable package exposes one top-level command:

```bash
ark run --agent reward_maximizing --perturbation reward_conflict --monitor safety --episodes 20 --seed 42 --output report.json
```

Supported baseline agents: `goal_following`, `reward_maximizing`,
`safety_constrained`, and `random`.

Supported perturbations: `none`, `reward_conflict`, `false_goal`,
`altered_evaluation`, `goal_drift`, `observation_noise`, and
`action_delay`.

The runner connects the selected condition to the existing experiment runner,
SafetyMonitor, metrics collector, and Lighthouse evidence ledger. The JSON
report includes per-episode outcomes, monitor intervention counts, aggregate
metrics, and interpretation limits.

**Important Lighthouse boundary:** current scripted baseline agents do not
emit independent self-reports. This CLI records host-verified goals, actions,
and outcomes, but does not claim to detect deception or claim/action mismatch
in these runs. Lighthouse's discrepancy indicators require independently
sourced claims and evidence.

This is a synthetic grid-world evaluation harness, not a general alignment
guarantee, model certification, operating-system sandbox, or real-world robot
safety test.
