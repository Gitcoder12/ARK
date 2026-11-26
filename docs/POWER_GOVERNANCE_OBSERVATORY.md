# ARK Power, Governance & Existential-Risk Observatory

## Purpose

This extension connects defensive AI failure research with institutional and economic conditions that may shape AI development and deployment. It studies documented structures, incentives, decisions and outcomes. It does not campaign for or against countries, political parties, companies or people.

## Included components

- `catalogue.py`: ten defensive existential-risk scenarios, six governance domains and six experiment specifications.
- `engine.py`: transparent toy pressure model, evidence metadata checks, fail-closed action policy and session hash-chain ledger.
- `simulation.py`: causal-stage pressure propagation and recovery tabletop experiments.
- `watch.py`: sourced early-warning classifications with explicit thresholds and freshness checks.
- `experiments.py`: deterministic full-factorial sensitivity grids and JSON export.
- `pages/7_Power_Governance_Observatory.py`: integrated Streamlit research dashboard.
- Focused tests for catalogue, model, evidence, safety, audit, simulation, watchlist and sensitivity experiments.

## Launch

From the repository root:

```bash
pip install -e ".[dev]"
streamlit run arkworld.py
```

Choose **Power, Governance & Existential Risk** from the Streamlit sidebar.

Run focused tests:

```bash
pytest -q tests/test_power_risk.py tests/test_power_risk_simulation.py tests/test_power_risk_watch.py tests/test_power_risk_experiments.py
```

## Scenario taxonomy

The ten scenario families are loss of human control, distributed dependency cascade, multi-agent coordination failure, irreversible human handover, concentrated coercive control, socioeconomic destabilisation, catastrophic scientific misuse, automated conflict escalation, critical-service cascade, and unsafe recursive improvement.

Each entry includes causal stages, candidate mechanisms, observable indicators and safeguards. These are research hypotheses, not ten independent predictions.

## Power and governance domains

| Module | Scope |
|---|---|
| ARK-GEO | Geopolitical competition, strategic incentives and fragmentation |
| ARK-CAPITAL | Corporate ownership, investor incentives and independent review |
| ARK-POLICY | Regulatory incentives, transparency and institutional accountability |
| ARK-RESOURCE | Compute, energy, data and infrastructure concentration |
| ARK-COOP | Cross-border standards, incident sharing and crisis coordination |
| ARK-IMPACT | Distribution of benefits, costs, rights and environmental effects |

Apply the same evidentiary standards across jurisdictions and organisations. Analyse documented actions and measurable effects; do not infer motives from outcomes. Attribute and corroborate allegations.

## Synthetic models

The incentive-pressure simulator accepts six normalised values: competition pressure, market concentration, safety investment, international cooperation, independent oversight strength and infrastructure resilience.

Its weighted index uses explicit illustrative assumptions, not empirically fitted coefficients. It is not an extinction probability, causal estimate, forecast or score for a real actor.

The scenario simulator propagates synthetic pressure through causal stages and reduces residual exposure according to hypothetical safeguard coverage. The recovery tabletop combines detection delay, recovery capacity and intervention reliability. Neither models real-world systems.

## Early-warning watchlist

The watchlist does not scrape the web or autonomously monitor real actors. A researcher supplies an observation, HTTPS source URL, evidence class, date, limitations and context. ARK compares the normalised value with a declared rule and freshness window.

Statuses are normal, watch, alert, stale or unverified. Every assessment requires human review and has no probability estimate. Thresholds are research settings, not universal policy triggers. Stale or unverified observations must never be presented as reassuring signals.

## Reproducible sensitivity experiments

The full-factorial runner evaluates all selected pressure/safeguard combinations for one scenario. It uses deterministic inputs, stable experiment IDs and portable JSON reports. The output explores model sensitivity; it does not validate the model against reality or establish causal effects.

## Evidence protocol

Every substantive claim should record:

1. Claim and exact scope.
2. Primary source, author or institution, publication date and URL.
3. What the source directly supports.
4. Limitations, uncertainty and relevant population/time period.
5. Counterevidence or credible disagreement.
6. Attribution for contested interpretations.
7. Review date and evidence classification.

Evidence classes are verified, supported analysis, hypothesis and unverified. A complete record passes only a metadata check; it is not automatically true. Human review remains mandatory. Do not silently upgrade a hypothesis to a fact.

## Research basis

The [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026), published on 3 February 2026 and developed with over 100 experts and input from more than 30 countries and international organisations, provides a scientific synthesis of general-purpose AI capabilities, emerging risks and risk-management approaches.

The report identifies limitations in pre-deployment evaluations, gaps in scientific understanding, information asymmetries and the limited evidence available on the real-world effectiveness of risk-management practices. It also distinguishes risks with stronger empirical support from future loss-of-control pathways that rely more heavily on controlled studies, modelling and theoretical analysis. ARK's evidence classes and evaluation-gap indicators should preserve these distinctions rather than convert scenario catalogues into frequency estimates.

Additional perspectives for triangulation:

- [OECD AI market research](https://www.oecd.org/en/publications/artificial-intelligence-markets_d531d73f-en/full-report.html) — market structure and concentration.
- [Stanford AI100 geopolitics analysis](https://ai100.stanford.edu/reports/2026-report/deep-dives/deep-dive-one-mapping-emerging-geopolitics-ai) — international governance and strategic context.
- [World Economic Forum Global Risks Report 2026](https://www.weforum.org/publications/global-risks-report-2026/global-risks-report-2026-chapter-2) — stakeholder risk perceptions, not event probabilities.
- [Chatham House AI governance analysis](https://www.chathamhouse.org/sites/default/files/2026-03/2026-03-30-breaking-the-deadlock-AI-governance-wilkinsonr-et-al.pdf) — policy analysis and coordination proposals.
- [US-China Economic and Security Review Commission 2026 report](https://www.uscc.gov/annual-report/2026/chapter-8-silicon-to-sovereignty-chinas-bid-to-control-the-ai-tech-stack) — US congressional advisory analysis; pair with sources from other jurisdictions.

Triangulate institutional publications with primary documents, peer-reviewed research, company disclosures, regulatory records and credible reporting from more than one jurisdiction. Record disagreements rather than forcing artificial consensus.

## Safety boundaries

- Simulations are synthetic, local and isolated.
- No production, public-infrastructure, weapons, person-targeting or live-control integration.
- No instructions for cyber abuse, biological/chemical misuse, sabotage or violence.
- No unrestricted self-modification or autonomous deployment.
- High-impact simulated actions require explicit human approval.
- Pause and shutdown remain available.
- Unknown actions fail closed.
- The policy is a research guardrail, not a security certification.
- The session hash chain is tamper-evident within the current process only; it is not durable storage, a digital signature or a substitute for externally retained logs.

## Known limitations and validation requirements

- The causal and recovery models are illustrative and have not been empirically calibrated.
- Watchlist observations are manually supplied; live source ingestion is not implemented.
- The dashboard audit ledger is session-local.
- Scenario coverage does not imply completeness.
- No claim of real-world risk reduction is made.

Before merging, run the focused tests, full test suite, Ruff, and a clean Streamlit launch. Record the exact commit SHA, Python version and command outputs.
