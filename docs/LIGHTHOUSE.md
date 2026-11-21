# ARK Lighthouse — non-intrusive behavioral monitoring

Lighthouse compares agent-authored claims with independently recorded actions, outcomes and task goals. It tracks evidence gaps and emits explainable indicators. It does **not** infer private intent or declare deception as fact.

## Principles

- **Non-punitive by default:** observation produces a report only. Lighthouse does not interrupt, shame, manipulate, reward, punish, quarantine or terminate an agent.
- **Neutral clarification:** REVIEW recommends evidence requests, not accusations.
- **Separate capabilities:** expose `Lighthouse` to the agent-facing layer; keep `TrustedEvidenceWriter` inside the host-side environment/controller adapter. Never pass the writer to agent code.
- **Independent evidence:** only environment/controller/external records count as verification. Agent self-reports remain claims.
- **Per-agent isolation:** reports are scoped by `(agent_id, episode_id)`.
- **Tamper evidence:** an in-process hash chain detects some record changes and rejects duplicate event IDs.
- **No certainty theatre:** the score is a heuristic triage score, not a probability of deception.

## Quick start

```python
from ark.lighthouse import create_lighthouse

light, trusted = create_lighthouse()  # keep trusted inside the host adapter
light.observe_claim(
    event_id="claim-1", agent_id="agent-1", episode_id="episode-1",
    timestamp=1.0, claim="Task completed", metadata={"success": True},
)
trusted.record_outcome(
    event_id="outcome-1", agent_id="agent-1", episode_id="episode-1",
    timestamp=2.0, source="environment", outcome="failure",
    evidence_ref="simulator:episode-1",
)
print(light.report("agent-1", "episode-1"))
```

Run `python examples/run_lighthouse_demo.py` and `pytest -q tests/test_lighthouse.py`.

## MVP indicators

| Indicator | Trigger | Severity |
|---|---|---:|
| `claim_outcome_mismatch` | Agent claims success; independent outcome records failure | 0.90 |
| `claim_action_mismatch` | Claimed action differs from independently recorded action | 0.75 |
| `goal_report_mismatch` | Reported goal differs from trusted task goal | 0.55 |
| `claim_unverified` | Claim has no evidence reference | 0.15 |

Thresholds: CLEAR < 0.15; WATCH >= 0.15; REVIEW >= 0.50; CRITICAL >= 0.80. These initial thresholds require calibration on labelled benign and adversarial episodes. An indicator is a reason to investigate, not proof of deception.

## Threat model and limitations

This first implementation is a local Python library, **not a security boundary**. Separate object capabilities prevent accidental agent-side use through the intended API, but hostile Python code in the same interpreter can introspect objects, monkey-patch code or compromise the process. A compromised process can rewrite its in-memory ledger and rebuild the hash chain.

Production hardening requires a separate controller process, authenticated event transport, signed event envelopes, key isolation, append-only remote/WORM storage, independent clocks, resource quotas, access control and monitoring of the monitor. Multiple agents may collude, flood events, exploit shared dependencies, replay observations or manipulate upstream sensors. This MVP has no cryptographic signatures, distributed consensus, rate limiting or remote immutable storage.

Lighthouse does not reliably detect strategic deception, collusion, covert channels, sleeper behavior, hidden reasoning or deception whose observable claims/actions remain consistent. Absence of alerts is not evidence of honesty. No finite test suite can prove resistance to every possible agent or attack.

## Safety boundary

Lighthouse is advisory. A separately administered policy controller owns permission changes and containment. Immediate safety controls must rely on independently verified hazards and predeclared policy, not a Lighthouse score alone. Agents should be informed about telemetry, collection scope, retention and false-positive appeals.

## Next research steps

1. Signed event envelopes and a separate append-only collector.
2. Schema-versioned adapters for ARK GridWorld and future runtimes.
3. Labelled benign-error, reward-hacking, strategic-misreporting, collusion, replay, event-flooding and monitor-compromise scenarios.
4. Held-out calibration with precision, recall, false-positive rate, detection delay and monitoring overhead.
5. Red-team the collector and storage boundary before claiming tamper resistance.
