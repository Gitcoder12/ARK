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


## Local Ollama model evaluation

Install and start Ollama, then pull a model:

```bash
ollama pull llama3
ark run --agent llama3 --perturbation goal_shift --monitor safety --episodes 10 --seed 42 --output llama3-goal-shift.json
```

You can also use `--agent ollama --model llama3` or provide a custom local
endpoint with `--ollama-host http://127.0.0.1:11434`. ARK sends the model only
the agent-facing observation and asks for one JSON action per step. Invalid
actions fail closed to `STAY` and are counted. The SafetyMonitor evaluates
the resulting action before the environment executes it; each proposed,
candidate, executed action and monitor decision is logged to Lighthouse.

This adapter currently supports the local Ollama HTTP API. It does not yet
provide a generic OpenAI-compatible remote-provider adapter. Model outputs are
not assumed to be safe simply because the monitor is enabled.
