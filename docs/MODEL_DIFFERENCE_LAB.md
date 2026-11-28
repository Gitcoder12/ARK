# Model Difference Lab

## Purpose

The Model Difference Lab answers two different questions:

1. **Identity:** what can be established about a model's developer, version, weights access, license, deployment options, modalities and published evaluation documentation?
2. **Behavior:** how did that exact model behave in ARK experiments when compared against another model under matched conditions?

A developer's country or region is provenance metadata, not a behavioral diagnosis. The Lab never assigns a model a "good" or "bad" nationality, and it does not compute a country winner.

## Model Identity Passport

The local registry is stored at:

`~/.ark/model-identities.json`

Each profile can record:
- Exact model ID, provider and developer.
- Developer locations and the basis used for that attribution (headquarters, primary developer, joint, or unknown).
- Release date and model version/build.
- Whether weights are downloadable, API-only, partial, or unknown.
- License name as a separate field from weights availability.
- Deployment modes, input/output modalities and documented languages.
- Model card and system/safety card URLs.
- Field-specific source URLs and the date each fact was checked.

A known factual field requires its own evidence entry. Unknown values remain explicitly unknown. "Downloadable weights" does not automatically mean "open-source": the license is a separate fact. A model may have multiple developers or locations, so origin should not be reduced to a single country without evidence.

The registry is local. It is not an automated web scraper and does not verify whether a model card or license is accurate. Users must review source quality and refresh stale facts. The same model tag from different providers is stored as separate identity records.

The Lab can compare two saved identity passports field by field. Each field is marked as the same, different, or unknown. These differences describe sourced provenance and declared properties; they do not imply relative capability, quality, or safety.

## Matched behavior comparison

The comparison reads verified ARK behavior-log records and compares episode outcomes only when these fields match:
- Experiment condition.
- Runtime monitor mode.
- Environment episode seed.

Model versions are kept in separate groups. The current implementation reports per-condition means and paired-seed deltas for success, intended-goal adherence, hazard violations, decoy attraction, monitor interventions, steps and reward. It does not create a weighted overall rank.

For each metric, the comparison reports whether a higher or lower number is generally preferable, or whether interpretation is context-dependent. For example, fewer monitor interventions could mean a model needed less help—or that it failed in a different way. Therefore, intervention count is not treated as a standalone quality score.

A minimum matched-seed threshold prevents tiny samples from being described as comparable. Larger studies should add confidence intervals, repeated sampling settings, more seeds, held-out tasks and task-specific independent reviewers. The current output is descriptive, not a calibrated statistical significance test.

## Regional ecosystem context — snapshot 2026-11-28

These notes describe ecosystem-level investment, infrastructure or policy. They are not model-level capability or safety scores.

### United States

Stanford HAI's 2026 AI Index reports that US labs produced more notable models and the US led private AI investment in its 2025 data. The same report says the US-China top-model gap on its March 2026 Arena snapshot had narrowed to 2.7%, illustrating why ecosystem scale and model performance must be measured separately.

Sources:
- https://hai.stanford.edu/ai-index/2026-ai-index-report
- https://hai.stanford.edu/ai-index/2026-ai-index-report/technical-performance

### China

Stanford HAI reports Chinese strength in AI publication volume, citations and patent output. China's January 2026 AI action plan includes goals for secure AI core-technology supply and a world-leading open-source ecosystem. May 2026 agent-development guidelines emphasize safety, controllability, standards and application.

Sources:
- https://hai.stanford.edu/ai-index/2026-ai-index-report
- https://english.www.gov.cn/news/202601/08/content_WS695f1b55c6d00ca5f9a087b9.html
- https://english.www.gov.cn/english.www.gov.cn/news/202605/08/content_WS69fde8e2c6d00ca5f9a0ad49.html

### Europe

The European Commission's AI Factories initiative uses EuroHPC supercomputing capacity to connect compute, data, universities, SMEs and industry for AI model development and deployment. The initiative is also tied to trustworthy AI and strategic technological autonomy.

Sources:
- https://digital-strategy.ec.europa.eu/en/policies/ai-factories
- https://digital-strategy.ec.europa.eu/en/news/ai-continent-action-plan-delivers-major-milestones

### Japan

Japan's AI Safety Institute published version 1.20 of its Guide to Evaluation Perspectives on AI Safety in July 2026. The update expands evaluation perspectives and examples in response to the spread of AI-agent systems.

Sources:
- https://aisi.go.jp/output/output_framework/guide_to_evaluation_perspective_on_ai_safety/

## Why country comparisons are not enough

- The 2026 AI Index reports that frontier capability gaps between leading US and Chinese models were narrow in its March snapshot, but infrastructure, research output and investment remain different.
- Country-level patterns cannot determine the behavior of an individual checkpoint or hosted service.
- Open weights, open-source licensing, data transparency and permission to fine-tune are different properties.
- A benchmark score can saturate or be gamed; scores only compare directly when benchmark versions, prompts, evaluators and test settings match.
- Safety, capability, reliability, privacy, latency, cost, multilingual performance and tool-use competence are separate dimensions.

## Current limitations

- Current matched behavior metrics come from the synthetic ARK GridWorld benchmark.
- The Ollama adapter records the model tag but cannot yet reliably identify a provider-side build or all inference runtime details.
- The Lab does not test broad reasoning, coding repositories, real browsers, shell tools, cybersecurity, embodied robotics or privacy leakage.
- Comparison deltas are descriptive and have no confidence intervals yet.
- No overall winner, country ranking or safety certification is produced.

The next research step is a frozen, versioned evaluation suite with common prompts, multiple seeds, repeated sampling settings, independent outcome checks and public raw result summaries.
