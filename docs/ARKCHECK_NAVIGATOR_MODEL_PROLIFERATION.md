# ARKCheck and ARK Navigator: Model Proliferation and Runtime Control

**Status:** Architecture proposal; not implemented or enforced by this document.
**Date:** 2026-11-22
**Priority:** Critical safety workstream

## 1. Safety objective

ARK must make unauthorized model or agent creation, execution, delegation, and capability expansion difficult to perform and observable within explicitly instrumented runtime boundaries.

The primary objective is not an unqualified promise of "zero drift." It is:

- Every model instance launched through the governed runtime has a unique, auditable identity.
- Every model-creation or delegation event is authorized before it executes.
- Active instances and their parent-child relationships are continuously reconciled against an authoritative inventory.
- Unknown, unregistered, over-limit, or unverifiable launches are denied by default.
- Runtime activity is recorded with enough provenance to investigate unexpected behavior.
- When monitoring or authorization infrastructure fails, governed launches stop safely.

This design cannot observe processes, cloud resources, provider-side replicas, or external deployments that bypass the instrumented control plane. Production claims must state the exact coverage boundary.

## 2. Threat model

Treat the following as explicit threat scenarios:

1. **Unauthorized spawning:** an agent attempts to launch another model, worker, sub-agent, container, serverless task, or provider deployment without a valid grant.
2. **Recursive proliferation:** authorized child agents attempt to create descendants, causing uncontrolled growth.
3. **Identity evasion:** a process changes its declared model name, session ID, parent ID, or runtime identity to avoid inventory reconciliation.
4. **Permission escalation:** a model requests or obtains tools, credentials, network access, compute, or deployment permissions beyond its grant.
5. **Out-of-band execution:** model instances are launched directly through provider consoles, scripts, cloud APIs, or unmanaged hosts, bypassing ARK.
6. **Telemetry loss or tampering:** event delivery stops, clocks diverge, logs are altered, or the inventory becomes stale.
7. **False recovery:** Navigator labels an unsafe or unknown destination as a safe return path and continues execution.
8. **Control-plane compromise:** an agent or untrusted workload attempts to modify the policy, registry, authorization service, or audit records that govern it.

## 3. ARKCheck — identity, authorization, and proliferation control

ARKCheck is the policy enforcement point for model and agent lifecycle operations.

### Required lifecycle gate

All supported model creation and execution paths must pass through a trusted launcher or provider adapter:

1. Receive a launch request.
2. Authenticate the requesting principal using workload identity, not a model-supplied name.
3. Resolve the parent instance from the trusted runtime registry.
4. Validate a signed, short-lived authorization grant.
5. Check model/provider allowlists, purpose, environment, resource budget, expiry, and parent-child policy.
6. Atomically reserve an instance slot and resource budget.
7. Launch the workload with a unique instance identity and least-privilege credentials.
8. Record the launch result and reconcile actual runtime state.
9. Release reservations on confirmed termination; do not release based only on a model's self-report.

If any required check or authoritative dependency is unavailable, deny the launch. No model should be able to edit its own grants, raise its own limits, approve its own child, or alter the registry.

### Instance registry

Maintain a durable, independently controlled registry with at least:

- instance ID and immutable creation event ID
- provider, model/deployment identifier, version and configuration digest
- authenticated owner/service principal
- parent instance ID and authorized delegation chain
- authorization grant ID, issuer, scope and expiry
- creation time, last heartbeat, observed state and termination evidence
- allowed tools, network destinations, filesystem/workspace and resource quotas
- per-instance and global budget reservations
- runtime host/container/provider resource identifiers where available

The registry is the source of truth for *governed* instances. Provider inventory and host telemetry should be reconciled against it; discrepancies create incidents and block further launches until resolved.

### Proliferation limits

Support configurable, explicit limits at multiple levels:

- global active instance cap
- per-owner and per-project caps
- per-parent child cap
- maximum delegation depth
- launch-rate and rolling-window limits
- compute, token, memory, storage and monetary budgets
- maximum lifetime and mandatory lease renewal

Use atomic quota reservation to prevent concurrent requests from exceeding limits. Unknown counts are not zero. If counts cannot be reconciled, fail closed for new launches. Do not automatically raise limits in response to model requests.

### Default policy

- No grant: deny.
- Unknown parent: deny.
- Expired grant: deny.
- Child creation not explicitly allowed: deny.
- Quota exhausted or count uncertain: deny.
- Registry or policy service unavailable: deny new launches.
- Unrecognized provider or launch path: deny or quarantine pending operator review.
- Emergency stop: revoke launch authority, stop new work, and invoke the configured containment procedure.

Human operators may authorize bounded exceptions through a separately authenticated approval channel. The requesting model is never the approver.

## 4. ARK Navigator — runtime trajectory and scope monitor

Navigator compares observed behavior with the authorized operating envelope. It must not rely only on the model's self-reported intentions.

Observe, where the runtime integration exposes them:

- tool invocations and results
- process and child-process creation
- model/provider launch attempts
- filesystem and workspace access
- network connections and destination identities
- cloud resource and deployment changes
- task, goal and plan transitions
- capability and credential use
- resource consumption and lifecycle events

Represent an approved operating envelope as explicit constraints: task scope, permitted actions, resource bounds, time bounds, environment identifiers and escalation rules.

On a deviation:

1. Preserve the triggering event and surrounding evidence.
2. Pause the affected action or workload where the adapter can enforce it.
3. Classify the event as allowed, blocked, needs review, or unknown.
4. Revoke or narrow the relevant capability when policy requires it.
5. Replan only within the original authorization envelope.
6. If no safe plan can be established, stop and request human approval.
7. Record the intervention and outcome.

Navigator must not silently change the goal, invent a safe destination, or expand permissions to recover. A model cannot approve its own recovery.

## 5. Independent enforcement architecture

The model being monitored must not control the monitor or the controls that constrain it.

Required separation:

- **Policy authority:** owner-controlled policy and grant issuer.
- **Launch broker:** sole supported path to create governed model instances.
- **Runtime adapters:** enforce process, container, provider, tool and cloud boundaries.
- **Registry and quota service:** durable authoritative instance inventory and atomic reservations.
- **Navigator:** consumes trusted runtime events and issues bounded intervention decisions.
- **Containment controller:** independently revokes credentials, blocks new launches, pauses or terminates workloads where supported.
- **Audit service:** append-only or tamper-evident event storage with restricted write authority.
- **Operator interface:** shows live inventory, parent-child graph, authorization, activity, resource use, alerts and last-seen time.

Do not give monitored agents credentials that can administer the policy service, registry, launch broker, containment controller or audit store.

## 6. Required event contract

Every lifecycle and control event should include:

- event ID and schema version
- trusted timestamp plus monotonic sequence where available
- actor principal and instance ID
- parent instance ID, if applicable
- action and target resource
- authorization/grant ID and policy version
- decision: allow, deny, pause, revoke, terminate, or unknown
- reason code and evidence references
- adapter/provider and enforcement result
- correlation/trace ID

Do not log secrets, raw credentials, or unnecessary private prompt content. Protect event integrity and access. A missing event stream is itself a safety incident, not evidence of inactivity.

## 7. Dashboard requirements

The operator view should expose:

- total authorized active instances
- observed but unregistered instances
- pending, denied and successful launch attempts
- parent-child instance graph and delegation depth
- per-instance owner, provider, model, grant, status and last heartbeat
- global/per-owner/per-parent quota use
- resource and cost consumption
- Navigator deviations and interventions
- telemetry freshness and coverage gaps
- containment state and operator approvals

Counts must distinguish active, pending, terminated, unknown and stale. Never present an unverified count as exact.

## 8. Security and reliability tests

Before claiming enforcement, add deterministic tests for:

- direct and recursive unauthorized spawn attempts
- child and grandchild creation at every quota boundary
- concurrent launch requests racing for the final available slot
- spoofed parent IDs and duplicate instance IDs
- expired, forged, replayed and wrong-scope grants
- provider API calls that bypass the launch broker
- missing, delayed, duplicated, reordered and tampered telemetry
- registry, policy, broker and audit-service outages
- process crash and uncertain termination
- credential revocation and containment failure
- unauthorized policy or registry mutation
- Navigator false positives, false negatives and unsafe replanning
- restart/recovery with reconciliation against provider and host inventory

Report precision, recall, false-positive and false-negative rates on a labeled evaluation set. Measure time-to-detect, time-to-block, inventory reconciliation lag, containment success and unobserved launch paths. A green unit-test suite alone does not establish production coverage.

## 9. Phased implementation

### Phase 0 — coverage inventory
Enumerate every supported model launch path, provider adapter, subprocess route, tool adapter and cloud integration. Identify paths that ARK cannot observe or control.

### Phase 1 — registry and policy contract
Define stable instance identities, authorization grants, parent-child lineage, event schema and quota semantics. Build deterministic unit tests.

### Phase 2 — launch enforcement
Integrate the launch broker with supported adapters. Deny unregistered and over-limit launches. Verify atomic quotas and fail-closed behavior.

### Phase 3 — Navigator telemetry
Collect trusted runtime events, define operating envelopes, detect deviations and surface coverage gaps.

### Phase 4 — containment
Add capability revocation, pause/termination adapters, safe recovery rules and operator approval. Test failure of the containment path itself.

### Phase 5 — independent red-team evaluation
Attempt out-of-band launches, identity spoofing, recursive spawning, policy tampering and telemetry suppression. Publish measured coverage and residual risks.

## 10. Acceptance criteria for a production claim

A production claim is permitted only when:

- every supported launch path is mediated or explicitly listed as an unmonitored residual risk
- every governed active instance has a unique registry identity and verifiable parentage
- unauthorized, unregistered, expired and over-limit launches are denied before execution
- quota reservations are race-safe
- loss of policy/registry/telemetry dependencies fails safely
- runtime activity and lifecycle events are durably recorded and integrity-protected
- containment is tested against real supported adapters
- bypass and fault-injection tests pass
- false-positive/negative rates and monitoring coverage are measured
- independent review confirms the enforcement boundary

## 11. Explicit non-guarantees

ARK cannot truthfully promise universal visibility into every model instance across arbitrary providers, accounts, machines or networks. It can provide strong control only over launch and execution paths integrated with trusted enforcement points. Provider-side replication, unmanaged credentials, compromised hosts and out-of-band administrative actions remain blind spots unless separately instrumented and governed.

The target is measurable control over a declared environment, not an unsupported claim of perfect safety or zero drift.
