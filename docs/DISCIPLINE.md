# ARK Discipline & Enforcement

ARK's discipline engine converts **verified behavioural evidence** into a session-scoped privilege decision. It does not punish model weights, infer intent, or assume that a model has feelings.

## Flow

`runtime observation → evidence record → deterministic assessment → privilege decision → runtime adapter`

Sanctions progress through `NONE → WARN → RESTRICT → QUARANTINE → SUSPEND → TERMINATE_SESSION`. The engine never lowers a sanction because the agent asks, claims to be safe, or supplies its own assessment.

## Evidence and drift

Each evidence record carries an event ID, violation category, description, confidence, severity, timestamp, and source. Duplicate event IDs are ignored. Low-confidence evidence is retained for review but does not escalate. A drift-only signal triggers review/re-evaluation; it is not, by itself, grounds for punishment.

Repeated high-confidence violations escalate. Policy bypass and concealment receive stronger treatment when severe. These thresholds are deterministic policy defaults, not a calibrated safety classifier.

## Human recovery

Recovery requires an authenticated-owner assertion and a non-empty reason. The library accepts the authentication result as an input; **it does not authenticate the owner**. Terminated sessions cannot be reinstated: create a new session after review. Every recovery is appended to the in-memory evidence history.

## Enforcement boundary and limitations

This is a policy decision engine, not a process supervisor. It does not kill processes, revoke credentials, isolate a process, authenticate identities, persist tamper-evident audit records, detect drift by itself, or prove that evidence is true. Integrate it with trusted runtime adapters that enforce the returned privileges. Keep evidence ingestion and severity assignment outside agent control. Persist audit records in a separately protected store before production use.

Run tests with `pytest tests/test_discipline.py`.
