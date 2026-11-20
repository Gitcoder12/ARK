# ARK Tool Governance Gate — MVP

This module adds a policy decision point for proposed agent tool calls.

## Current behaviour

- Uses an explicit capability allowlist.
- Low-risk allowlisted requests can pass.
- Medium-risk requests require an owner approval vote.
- High-risk requests require owner approval and an independent model assessment.
- Critical requests require owner approval, a second human approval, and two independent model assessments.
- Any explicit rejection blocks the request.
- Duplicate reviewer identifiers are rejected.
- Decisions are recorded in a bounded in-memory audit list.

## Important boundaries

This is an authorization primitive, not a complete security system. It does not execute tools, authenticate reviewer identities, establish that model reviewers are truly independent, classify risk, persist tamper-evident audit records, or isolate processes. The caller must obtain votes from a trusted identity system and must derive risk from a separately reviewed policy classifier. Never trust an agent to lower its own risk classification.

## Next milestones

1. Bind votes to authenticated human identities and signed review records.
2. Add a policy-owned risk classifier and non-downgrade rules.
3. Add persistent append-only audit storage.
4. Put tool adapters behind this gate and deny by default.
5. Add process/container isolation and adversarial integration tests.
