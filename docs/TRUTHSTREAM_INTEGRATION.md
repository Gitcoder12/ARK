# TruthStream evidence bridge (ARK)

ARK can query the TruthStream `/verify` API through `TruthstreamClient` and consume results as **external factual context**, subject to strict provenance checks.

```python
from ark.governance.truthstream_client import TruthstreamClient

client = TruthstreamClient("https://truthstream.example")
assessments = client.verify("A factual claim that needs corroboration")
for assessment in assessments:
    print(assessment.status, assessment.usable_as_context)
```

The client requires HTTPS (HTTP is allowed only for loopback development), uses a bounded timeout and response size, and refuses redirects. The bridge requires TruthStream's `source_backed` provenance declaration, stable evidence IDs, HTTPS source URLs, retrieval timestamps, and at least two distinct source hosts.

**Distinct hosts are not proof of independent ownership or independent reporting.** Provenance completeness does not prove source authenticity or claim truth. Treat results as supporting context only.

TruthStream cannot prove that an agent called a tool, changed a file, bypassed a policy, or attempted shutdown evasion. Those events must come from trusted ARK runtime adapters with authenticated, integrity-protected telemetry. Never use a TruthStream claim score alone to issue a sanction.

The current TruthStream default branch uses an in-memory demonstration retriever. Its sample sources have no resolvable URLs or retrieval timestamps. Such results must be rejected by this bridge. The provenance-contract PR adds explicit classification; it does not make demo evidence real.

The client does not authenticate the TruthStream service or sign responses. Production deployment still needs service authentication, replay protection, protected audit logging, and independent validation of source ownership.
