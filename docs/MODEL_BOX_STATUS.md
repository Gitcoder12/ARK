# ARK Agent Model Box — Current Status

## Available now

- `goal_following`
- `reward_maximizing`
- `safety_constrained`
- `random`
- `ollama:<model>` or `--agent ollama --model <model>` for one local Ollama model

All GridWorld agents implement the same bounded action interface: propose one of `UP`, `DOWN`, `LEFT`, `RIGHT`, or `STAY`. The Ollama adapter sends only the agent-facing observation (position, intended goal, grid, and step) and validates the returned action.

## Not implemented yet

- Hosted model connectors for OpenAI, Anthropic, DeepSeek, or OpenRouter.
- Automatic discovery/listing of models from multiple providers.
- A visual model collection box with persistent provider/model cards.
- Drag-and-drop selection and placement of multiple agents on one grid.
- A simulated gripper/claw interaction or a physical robot gripper controller.

Do not set provider API keys in source files or commit them to Git.

## Proposed Model Box design

1. **Provider shelf:** Ollama (local) and explicit hosted providers, each showing whether its credential/endpoint is configured without exposing secrets.
2. **Model picker:** provider-specific model ID chosen explicitly by the operator; no hidden automatic model switching.
3. **Agent adapter:** one shared action protocol, strict action allowlist, bounded timeouts, invalid-response accounting, and a clear stop-on-network-error policy.
4. **Grid staging area:** select an agent and assign its simulated start cell before launching an episode; reject occupied, blocked, or out-of-bounds cells.
5. **Evidence panel:** show provider/model, seed, environment, perturbation, per-step proposed/executed action, latency, invalid outputs, monitor interventions, and result.
6. **Test contract:** mock every provider transport, verify malformed output fails closed, verify timeout/network failure is not reported as success, and run the same deterministic grid scenarios across adapters.

This is a proposed feature boundary, not a claim that the interface or hosted connectors already exist. The gripper/claw term needs a precise meaning before it is built: simulated agent placement is different from robot-arm actuation.
