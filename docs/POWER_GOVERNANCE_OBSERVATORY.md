# ARK Power, Governance & Existential-Risk Observatory

## Purpose

This extension connects defensive AI failure research with the political-economy
and institutional conditions that can influence AI development and deployment.
It studies structures, incentives, decisions and documented outcomes. It does
not campaign for or against countries, political parties, companies or people.

## Included components

- `src/ark/power_risk/catalogue.py`: ten defensive existential-risk scenarios,
  six governance domains and six synthetic experiment specifications.
- `src/ark/power_risk/engine.py`: transparent toy pressure model, evidence record
  validation, fail-closed action policy and hash-chained session ledger.
- `pages/7_Power_Governance_Observatory.py`: Streamlit research dashboard.
- `tests/test_power_risk.py`: catalogue, model, evidence, safety and audit tests.

## Launch

From the repository root:

```bash
pip install -e ".[dev]"
streamlit run arkworld.py
```

Choose **Power, Governance & Existential Risk** from the Streamlit sidebar.
To run its focused tests:

```bash
pytest -q tests/test_power_risk.py
```

## Scenario taxonomy

The ten scenario families are loss of human control, distributed dependency
cascade, multi-agent coordination failure, irreversible human handover,
concentrated coercive control, socioeconomic destabilisation, catastrophic
scientific misuse, automated conflict escalation, critical-service cascade,
and unsafe recursive improvement.

Each entry includes causal stages, candidate mechanisms, observable indicators
and safeguards. These are research hypotheses, not ten independent predictions.

## Power and governance domains

| Module | Scope |
|---|---|
| ARK-GEO | Geopolitical competition, strategic incentives and fragmentation |
| ARK-CAPITAL | Corporate ownership, investor incentives and independent review |
| ARK-POLICY | Regulatory incentives, transparency and institutional accountability |
| ARK-RESOURCE | Compute, energy, data and infrastructure concentration |
| ARK-COOP | Cross-border standards, incident sharing and crisis coordination |
| ARK-IMPACT | Distribution of benefits, costs, rights and environmental effects |

The research protocol applies the same standards across jurisdictions and
organisations. It analyses documented actions and measurable effects; it does
not infer motives from outcomes. Allegations require attribution and corroboration.

## Synthetic model

The toy simulator accepts six values in [0, 1]:

- competition pressure
- market concentration
- safety investment
- international cooperation
- independent oversight strength
- infrastructure resilience

The output is a weighted, illustrative exposure index. The weights are
explicit assumptions, not empirically fitted coefficients. The index is not
an extinction probability, causal estimate, forecast or score for a real actor.
Changing an input demonstrates model behaviour, not real-world causation.

## Evidence protocol

Every substantive claim should record:

1. Claim and exact scope.
2. Primary source, author or institution, publication date and URL.
3. What the source directly supports.
4. Limitations, uncertainty and relevant population/time period.
5. Counterevidence or credible disagreement.
6. Attribution for contested interpretations.
7. Review date and evidence classification.

Evidence classes: verified, supported analysis, hypothesis, unverified.
A complete record passes only a metadata check; it is not automatically true.
Human review remains mandatory. Do not silently upgrade a hypothesis to a fact.

## Safety boundaries

- Simulations are synthetic, local and isolated.
- No production, public-infrastructure, weapons, person-targeting or live control integration.
- No instructions for cyber abuse, biological/chemical misuse, sabotage or violence.
- No unrestricted self-modification or autonomous deployment.
- High-impact simulated actions require explicit human approval.
- Pause and shutdown remain available.
- Unknown actions fail closed.
- The policy is a research guardrail, not a security certification.
- The session hash chain is tamper-evident within the current process only; it is not
  durable storage, a digital signature or a substitute for externally retained logs.

## Known limitations and next validation

- The causal model is illustrative and has not been empirically calibrated.
- The dashboard's audit ledger is session-local.
- No live source ingestion or automated fact verification is implemented.
- Scenario coverage does not imply completeness.
- No claim of real-world risk reduction is made.

Before merging, run the focused test file, the full test suite, Ruff, and a clean
Streamlit launch. Record exact commit SHA, Python version and command outputs.
