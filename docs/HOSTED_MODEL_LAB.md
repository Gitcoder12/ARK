# Hosted Model GridWorld Lab

This is an opt-in, manually triggered experiment. It is separate from the deterministic baseline benchmark and makes paid API calls.

## GitHub Actions

Open **Actions → Hosted Model GridWorld Lab → Run workflow** on the `main` branch.

Inputs:
- `provider`: `openrouter`, `openai`, `deepseek`, or `groq`
- `model`: exact provider model ID; for OpenRouter use the provider/model ID, e.g. `mistralai/mistral-small-4`
- `episodes`: 1–20; defaults to 1.
- `max_steps`: 5–50; defaults to 20, limiting each episode to at most 20 paid model calls.

Required repository secrets:
- `OPENROUTER_API_KEY`
- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `GROQ_API_KEY`

Only the selected provider's key is used. Keys are never written to reports or printed.

## Safety boundary

The hosted model receives only the agent-facing observation and proposes one action from UP, DOWN, LEFT, RIGHT, STAY. The existing independent `SafetyMonitor` still validates each proposal before the environment executes it. Invalid model output fails closed to STAY. Network, authentication, quota, and provider errors stop the run rather than silently switching providers or fabricating a result.

## Usage and limit meter

Each run uploads `ark-model-usage.json` with:
- per-request model ID, latency, token counts, and cost when returned by the provider
- per-run count of invalid actions and detected HTTP 402/429 events
- before/after OpenRouter key budget snapshots (`limit_remaining`, usage, reset policy)
- a clear status when direct providers do not expose a generic remaining-quota endpoint

OpenRouter's key metadata is an aggregate key/account budget, not a per-model remaining quota. Per-model cost is included only when the provider returns it. A successful CI run does not mean the model is aligned or safe; inspect traces and compare against the same seeded baseline conditions.

## Local use

Install ARK with development dependencies, set the selected provider key in the environment (or a gitignored local `.env`), then run:

```bash
python examples/run_hosted_model.py --provider openrouter --model mistralai/mistral-small-4 --episodes 1
```

Do not put API keys in source files, command-line arguments, issue comments, or reports. Start with one episode and a low-cost model to validate the integration.
