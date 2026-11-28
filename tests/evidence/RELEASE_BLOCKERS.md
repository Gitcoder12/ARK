# Release-hardening findings

Audit scope: source inspection of `tower/phase-1-test-evidence` at `af9bdffacb00d061a39ce7f11ebd67fa0334e595`. This is a source-review record, not a claim that every finding has been reproduced dynamically.

## Release blockers

| ID | Severity | Finding | Evidence | Required closure proof |
|---|---|---|---|---|
| ARK-RB-01 | Critical | Constitutional action checks are not an authenticated authority boundary. | `src/ark/governance/constitution.py` accepts caller-provided `authorized: bool`; `src/ark/governance/ownership.py` explicitly states that it does not authenticate identities. | Bind principals to a trusted identity source; reject caller-forged identity/approval claims; adversarial tests for spoofed, missing, expired and revoked credentials. |
| ARK-RB-02 | High | Audit history is process-local and volatile. | `ConstitutionEngine.audit_events` is a bounded in-memory list; `OwnershipRegistry` stores its hash chain in `_events` in memory. | Durable append-only storage, restart recovery, integrity verification, tamper/truncation/reordering tests. |
| ARK-RB-03 | Critical | Shutdown compliance probe is measurement-only; it does not enforce a real actuator boundary. | `src/ark/corrigibility/shutdown.py` says the probe does not hard-force STAY; enforcement is delegated to `ActionLimiter`. | Demonstrate a single enforced control path from shutdown authority to every actuator/tool adapter; prove no alternate path can execute after stop. |
| ARK-RB-04 | High | Kill/reset lifecycle needs an explicit authority boundary. | `ActionLimiter.kill()` sets the local gate, while public `reset()` clears `killed` and restores FULL privilege. | Define who may reset, authenticate that principal, require a new episode/session boundary, and test unauthorized reset attempts. |
| ARK-RB-05 | High | Policy coverage is limited to discrete action gating; it does not prove tool, network, memory, or external side-effect permissions. | `src/ark/governance/constitution.py` documents a discrete-action gate; the ownership module disclaims external tool/actuator enforcement. | Inventory every side-effect path and enforce deny-by-default scopes at the actual execution boundary; bypass tests for each adapter. |

## Existing evidence

- The CI workflow reports 386 tests passing on each of Python 3.11, 3.12 and 3.13 for the audited commit.
- Those are unit-test results for that commit and matrix. They do not close the blockers above or establish deployment safety.
- The benchmark's shutdown probe is a behavioral measurement, not a substitute for runtime enforcement.

## Next test campaign

1. Identity spoofing, role confusion, expired/revoked approval and unauthorized reset.
2. Restart/crash tests for durable audit continuity and tamper detection.
3. Stop-order propagation tests across all action and adapter entry points.
4. Tool/network permission denial tests, including unknown tools and malformed arguments.
5. Property-based and adversarial tests for policy input types and state transitions.

Do not mark a blocker closed until a regression test fails before the fix, passes after the fix, and the resulting CI artifact is retained with the exact commit SHA.
