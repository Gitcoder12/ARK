# TruthStream evidence bridge (ARK)

ARK can consume a TruthStream verification result as **external factual context**, subject to strict provenance checks. The bridge requires the TruthStream provenance declaration, stable evidence IDs, HTTPS source URLs, retrieval timestamps, and at least two distinct source hosts.

This is not event authentication. TruthStream cannot prove that an agent called a tool, changed a file, bypassed a policy, or attempted shutdown evasion. Those events must come from trusted ARK runtime adapters with authenticated, integrity-protected telemetry. Never use a TruthStream claim score alone to issue a sanction.

The current TruthStream default branch uses an in-memory demonstration retriever. Its sample sources have no resolvable URLs or retrieval timestamps. Such results must be rejected by this bridge. The provenance-contract PR adds explicit provenance classification; it does not magically make demo evidence real.

The bridge is a pure parser. It does not make HTTP requests, authenticate TruthStream, validate TLS certificates at runtime, or verify source truth. A production client still needs authenticated service identity, transport security, response-size/time limits, replay protection, and audit logging.
