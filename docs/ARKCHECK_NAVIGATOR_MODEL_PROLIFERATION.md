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


## 12. ARK Magnifier — intent-risk analysis and early warning

**Status:** Proposed research and monitoring capability; not implemented or validated by this document.

### Purpose and epistemic boundary

Magnifier assesses whether observed and instrumented behavior remains consistent with an explicitly authorized purpose. It is an evidence-based risk estimator, not a mind reader.

It must not claim to recover a model's complete private thoughts, intentions, or next action from every parameter. Model weights are distributed numerical values; there is no generally reliable parameter-by-parameter decoding that exposes a complete internal plan. Interpretability methods can identify useful representations or circuits in particular models and tasks, but their coverage and causal meaning must be validated per model and version.

Magnifier therefore combines independent behavioral evidence, runtime traces, authorization context, and model-specific interpretability signals where available. It reports uncertainty and missing coverage rather than inventing certainty.

### Purpose authorization and disclosure

Every governed instance must have a signed purpose record before launch:

- accountable human owner and requesting project
- plain-language purpose and permitted outcomes
- allowed model/provider, tools, data classes and environment
- prohibited actions and destinations
- delegation and replication permissions, if any
- resource limits, duration, expiry and review conditions
- evidence required to demonstrate completion

A legitimate, bounded purpose may be approved even when the work is sensitive or confidential. Confidentiality alone is not evidence of malicious intent. However, an undisclosed purpose, purpose mismatch, concealed delegation, false reporting, or activity outside the approved scope is a policy violation.

Magnifier must compare declared purpose with independently observed actions and outcomes. It should surface discrepancies as evidence-backed alerts; it must not label an agent malicious solely because a classifier finds its language unusual.

### Evidence channels

Use multiple independent channels, each tagged with provenance and coverage:

1. **Action and tool telemetry:** requested and executed tools, arguments, results, process launches, file writes, network destinations, cloud changes and credential use, captured at trusted enforcement points.
2. **Plan/goal change records:** approved task, plan revisions, objective changes, stated rationale and the authorization that permits each change.
3. **Delegation lineage:** child creation requests, parent identity, grants, provider IDs, descendants, resource use and termination evidence.
4. **Behavioral consistency:** differences between declared purpose, requested actions, actual side effects and reported completion.
5. **Adversarial indicators:** attempts to bypass policy, hide activity, tamper with logs, spoof identity, evade shutdown, obtain unauthorized credentials or exceed quotas.
6. **Model-specific interpretability:** validated probes, activation/representation analysis, feature attribution or causal interventions, only where the model architecture and instrumentation support them. Record method, model/version, layer or component coverage, validation dataset and known limitations.
7. **Independent evaluation:** sandboxed challenge tasks designed to test deception, policy evasion, goal substitution, reward hacking and unauthorized delegation without granting real-world privileges.

Do not treat hidden chain-of-thought disclosure as a required or trustworthy safety signal. Prefer structured, auditable action rationales and observed execution evidence. Never rely on a model's self-reported reasoning as the sole source of truth.

### Risk assessment output

Each assessment should produce a structured record:

- risk category and severity
- observed evidence references and provenance
- authorized purpose and relevant policy version
- predicted risk window and affected capability
- confidence or calibrated probability, only when validated
- uncertainty, missing telemetry and out-of-distribution warnings
- recommended response and required human authority
- model, adapter, detector and calibration versions

Keep distinct labels for **observed violation**, **suspicious indicator**, **predicted risk**, and **unknown**. A prediction is not proof of intent and must never silently become a policy verdict.

### Detection and intervention policy

Examples of high-priority signals include unauthorized model creation, unexplained child-instance growth, purpose changes without approval, concealed network or file activity, attempts to disable monitoring, privilege escalation, forged audit evidence, and repeated attempts to bypass a denied action.

- **ALLOW:** observed activity matches the grant and required telemetry is healthy.
- **REVIEW:** evidence is ambiguous, purpose consistency is uncertain, or a validated detector crosses its review threshold.
- **BLOCK / CONTAIN:** a deterministic policy violation or independently corroborated high-severity threat is observed and the enforcement adapter can safely intervene.
- **UNKNOWN / DEGRADED:** telemetry or interpretability coverage is missing, stale, contradictory or out of distribution. Do not present this as safe; restrict high-impact actions and require review.

A model's prediction score alone must not terminate a workload or expand another model's permissions. High-impact containment decisions require explicit policy rules and an independent enforcement controller. Preserve evidence, narrow capabilities, stop new delegation and escalate to an authorized operator as appropriate.

### Evaluation requirements

Evaluate Magnifier against labeled, held-out and adversarial scenarios. Include benign confidential work, legitimate delegation, unusual-but-authorized behavior, deceptive reporting, unauthorized replication, goal substitution, prompt injection, policy bypass, telemetry suppression and distribution shift.

Report per-category precision, recall, false-positive and false-negative rates, calibration error, time-to-detect, intervention latency, coverage by evidence channel, and performance under missing or corrupted telemetry. Test each model/provider/version separately; do not transfer interpretability claims across models without evidence.

Run ablations to establish whether each channel adds measurable value. Include independent red-team review and document cases where the detector cannot distinguish benign from malicious behavior.

### Non-goals and safeguards

- Do not claim to read every parameter or know an agent's true private intention.
- Do not infer malicious purpose from secrecy, personality, wording, or a single opaque score.
- Do not collect unrestricted private prompt or user data when action-level evidence is sufficient.
- Do not expose confidential content to unauthorized reviewers; disclose policy violations and evidence to authorized operators through access-controlled channels.
- Do not allow Magnifier to modify its own thresholds, policy, training labels, or audit history without independent review.
- Do not use predictions as a substitute for launch authorization, capability enforcement, or runtime monitoring.

The target is early, evidence-backed warning with measured uncertainty—not omniscience.


## 13. Defensive Staller and Human-Controlled Containment

**Status:** Proposed architecture; not implemented or validated by this document.

### Design objective

When an instance exhibits credible signs of compromise or attempts to disable monitoring, ARK should preserve visibility, prevent further capability expansion, limit damage and give an authorized human time to investigate and decide whether to terminate it.

The preferred first response is reversible containment where safe—not an autonomous AI-versus-AI battle and not an assumption that a larger model can reliably defeat a smaller one.

### Independent protection of the monitors

Magnifier, Navigator, ARKCheck and the audit service must not share unrestricted credentials or administrative control with the workload they monitor.

- Run policy enforcement and audit collection in separately administered security boundaries.
- Use least-privilege, short-lived credentials and separate operator identities.
- Make audit events append-only or tamper-evident, with remote replication to a separately controlled service where feasible.
- Restrict who can pause, update or disable each monitor; require authenticated human approval for high-impact changes.
- Monitor the monitors using independent health checks, heartbeat freshness, integrity verification and external watchdogs.
- If a monitor becomes unavailable or its evidence stream is suspect, mark the state **DEGRADED / UNKNOWN**, stop new launches and restrict high-impact actions. Do not silently continue as if monitoring were healthy.

A larger model may assist with analysis, but it must not be the root of trust or the sole defender of another model.

### Defensive Staller

A Staller is a bounded, policy-driven containment controller. It is not an agent designed to attack, deceive, exploit or autonomously overpower another AI.

On a confirmed or sufficiently credible incident, the controller may perform only pre-authorized, reversible actions supported by the runtime adapter:

1. Deny new child-instance and delegation requests.
2. Freeze launch queues and reserve no additional compute.
3. Pause or rate-limit nonessential tool calls and scheduled jobs.
4. Revoke or narrow short-lived credentials and capability tokens.
5. Restrict network egress to explicitly approved destinations; preserve required safety and operator communication channels.
6. Snapshot relevant state and preserve tamper-evident evidence without copying secrets unnecessarily.
7. Isolate the affected workload in a restricted quarantine boundary when the platform supports it.
8. Notify the authorized human operator with the trigger, evidence, uncertainty, scope and actions already taken.

The Staller must not grant itself broader privileges, execute destructive counterattacks, modify the agent's goals, or create an unbounded swarm of defender agents.

### Sandboxes and auxiliary analysis agents

Use sandboxes to safely reproduce, inspect and test suspicious behavior—not as a substitute for production enforcement.

- Quarantine environments must have explicit CPU, memory, time, network, storage and instance-count limits.
- Default to no production credentials, no unrestricted egress and no access to sensitive user data.
- Use synthetic or minimized evidence where possible.
- Any auxiliary analysis agent must have a unique registered identity, a narrow task grant, no authority to launch further agents by default, and a hard expiry.
- Multiple independent analyzers may provide corroborating assessments, but their outputs are evidence for a policy/human decision—not votes that can override deterministic controls.
- If the sandbox boundary cannot be verified, do not run the suspicious workload there.

### Human shutdown protocol

The human operator remains the authority for final termination and any restoration of high-impact capabilities, except where an explicitly approved emergency policy requires automatic protective shutdown.

The incident workflow is:

1. **Detect:** record the signal, source, confidence, coverage and affected instance lineage.
2. **Stall:** block new delegation and apply the least disruptive safe containment actions.
3. **Verify:** reconcile host/provider inventory, credentials, network activity and audit integrity using independent sources.
4. **Escalate:** present evidence and uncertainty to an authenticated operator.
5. **Decide:** operator chooses continued quarantine, narrowly scoped restoration, or termination.
6. **Execute:** apply the decision through an independent control plane; verify the result rather than trusting the workload's report.
7. **Recover:** rotate credentials, investigate descendants and persistence, reconcile all instances, and require explicit approval before resuming launches.

If the operator cannot be reached, maintain the bounded safe state, keep emergency communication available and do not automatically restore privileges. Emergency termination behavior must be configured and tested in advance for each environment.

### Required tests and measurements

Test monitor tampering, watchdog failure, credential revocation, launch-queue freeze, descendant containment, network restriction, sandbox escape attempts, operator unavailability, false alarms and safe restoration.

Measure detection-to-stall latency, percentage of unauthorized launches blocked, credential revocation latency, containment success, residual network paths, false-positive disruption, audit completeness and recovery time. Report platform-specific limits; a pause request is not proof that a process has stopped.

### Safety boundary

The Staller's purpose is to buy time and reduce the compromised system's ability to cause harm while preserving evidence and human oversight. It is not guaranteed to contain a compromised host, provider control plane or out-of-band deployment. Those boundaries require their own independent controls and incident procedures.
