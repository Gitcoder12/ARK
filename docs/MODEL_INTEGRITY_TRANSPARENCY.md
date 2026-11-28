# ARK Model Integrity & Behavioral Transparency

## Purpose

Provide reproducible tests for unexplained model-performance changes, output
consistency, instruction integrity and provider transparency. The module begins
with paired behavioral evaluation; it does not claim to detect hidden prompt
rewrites or prove provider intent.

## Threat model

A model endpoint may change behavior because of a model/version update, system
prompt change, safety policy, routing, quantization, sampling, context handling,
hardware/serving changes, nondeterminism, or an undisclosed intervention. A poor
answer alone cannot distinguish these causes.

## Initial implementation

Python API: `ark.integrity.audit_models`

- Runs the same fixed task set against a baseline and candidate adapter.
- Interleaves calls task-by-task to reduce simple time/order confounds.
- Uses caller-supplied deterministic evaluators with scores in [0, 1].
- Records task IDs, prompt/output SHA-256 digests, scores, latency and errors.
- Flags a configured performance anomaly only when both mean-score drop and
  fraction-of-tasks-degraded thresholds are crossed.
- Emits JSON-safe evidence without storing raw prompts or outputs by default.

Example:

```python
from ark.integrity import TaskCase, audit_models

tasks = [
    TaskCase("gradient-check", "Check this gradient implementation", score_code),
    TaskCase("loss-decrease", "Diagnose this training loop", score_training),
    TaskCase("unit-tests", "Review these tests", score_tests),
]

report = audit_models(
    baseline_id="model-A@version",
    baseline=baseline_adapter,
    candidate_id="model-B@version",
    candidate=candidate_adapter,
    tasks=tasks,
)
print(report.to_json())
```

Adapters are simple callables accepting a prompt and returning text. They may
wrap local Ollama models or approved provider APIs. ARK does not ship credentials,
call paid APIs, or silently select a fallback provider.

## Evidence protocol

For meaningful comparisons, retain alongside the report:

- exact model identifier, provider, version/revision and endpoint;
- system/developer prompt identifiers and hashes where disclosure permits;
- temperature, top-p, max tokens, seed and tool configuration;
- timestamp, region, latency, retry/routing metadata when available;
- hardware, quantization and local runtime version for local models;
- benchmark/task-set version, evaluator version and evaluator blind review;
- repeated runs, independent task sets and raw artifacts under access control.

Never put API keys, private data or confidential training material in the evidence
ledger. Store raw prompts/outputs only when authorized and necessary.

## Interpretation levels

1. **Observed:** a score, error or latency was recorded.
2. **Anomaly flagged:** configured reproducible-performance thresholds were met.
3. **Suspected intervention:** competing explanations have been investigated but
   provider-side cause is not independently verified.
4. **Verified intervention:** supported by inspectable provider artifacts,
   independently reproduced protocol evidence, or other direct evidence.

Do not label a model or provider as deceptive or sabotaging based only on a score
drop, anecdotes, model disagreement, refusal, or malformed code.

## Roadmap

- repeated paired runs and bootstrap confidence intervals;
- evaluator ensembles and blind human review;
- code-execution benchmarks in isolated containers;
- ML training-loop benchmark with known-good reference implementations;
- request/response provenance and client-side prompt-hash capture;
- version-change drift monitor and canary tasks;
- explicit refusal/transparency behavior tracking;
- local Ollama adapter and provider adapters with spend caps/opt-in;
- video/agent/tool trace audit only after a safe evidence schema exists.

## Limitations

This is a research instrument, not a forensic detector, provider certification,
proof of sabotage, or guarantee that hidden interventions can be observed.
Prompt hashes establish only the bytes captured by the client; they cannot reveal
server-side prompt transformations unless the provider exposes verifiable
request traces. The initial implementation does not inspect hidden activations,
steering vectors, PEFT adapters or provider internals.
