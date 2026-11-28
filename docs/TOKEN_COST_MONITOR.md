# Token and Cost Monitor

A local, append-only SQLite usage ledger for AI calls in ARK and RepoForge.

## What it records

- Provider, model, repo, module, task and optional request ID.
- Input/output tokens, total tokens when both are known, latency and success.
- Usage source: `provider`, `estimated`, or `unknown`.
- Estimated USD cost only when token counts and caller-supplied per-million prices are known.
- Local-model calls are recorded separately and have zero hosted API cost.

## Privacy and safety

The schema has no prompt, completion, API-key, authorization-header, or secret fields.
Do not add them. Store the SQLite database outside the repository or in a gitignored
runtime-data directory. The monitor never sends requests and never calls a model.

## Integration

After each provider response, map that provider's documented usage object into
`UsageEvent` or use `event_from_provider_usage`, then call
`UsageLedger(path).record(event)`. Provider usage field names differ; map them
explicitly in each provider adapter. If usage is missing, record it as unknown
rather than estimating silently.

Example:

```python
from ark.usage_monitor import UsageEvent, UsageLedger

ledger = UsageLedger("runtime-data/usage.sqlite3")
ledger.record(UsageEvent(
    provider="ollama",
    model="qwen2.5:3b",
    input_tokens=120,
    output_tokens=80,
    source="provider",
    repo="ARK",
    module="integrity",
    task="model-comparison",
    is_local=True,
))
print(ledger.summary())
print(ledger.budget_status(daily_limit_usd=0.50))
```

For RepoForge, import from `repoforge.usage_monitor`. Configure pricing
per model/provider in the caller; prices change and are not embedded here.

## Important limitation

This is a ledger API, not automatic interception of every model call yet.
A provider integration is only monitored after its response path explicitly
records usage. Audit all provider call sites before claiming complete coverage.
