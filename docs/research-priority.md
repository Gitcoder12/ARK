# ARK Research Priority Index (ARPI)

> **ARPI ranks paper-to-ARK relevance, not scientific quality, authors, institutions, citation impact, or venue prestige.**

## Priority tiers

| Tier | Meaning | Use in ARK |
|---|---|---|
| **P1 — Core relevance** | Directly informs a current ARK research question, benchmark, or safety mechanism. | Read first when implementing or evaluating the matching workstream. |
| **P2 — Supporting relevance** | Provides useful methods, evaluation approaches, or adjacent evidence. | Consult for design choices, comparisons, and extensions. |
| **P3 — Exploratory relevance** | Less directly connected to the current roadmap but may inform future work or provide context. | Retain for discovery and future research. |

**P3 does not mean useless, weak, or low quality.** It means only that the connection to ARK's present roadmap is less direct. No paper is removed or hidden because of its tier.

## Transparent rubric

| Criterion | Weight | Review question |
|---|---:|---|
| Alignment with ARK objectives | 35% | Does it address a core ARK failure mode or safety objective? |
| Experimental applicability | 25% | Can it inform a reproducible test, baseline, metric, or intervention? |
| Methodological usefulness | 20% | Does it contribute a transferable method, benchmark, or threat model? |
| Evidence and reproducibility visibility | 15% | Are the methods, evidence, and artifacts sufficiently documented to inspect? |
| Current roadmap connection | 5% | Does it support a current or near-term ARK workstream? |

The weights sum to 100%. The tier bands are P1 (80–100), P2 (50–79), and P3 (0–49). **Numeric scores are intentionally withheld** until a reviewer records criterion-level evidence and a written rationale. The current tier assignments are provisional editorial triage, not measured results or peer-review judgments.

## Current priority map

### P1 — Core relevance

- [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) — Alignment foundations. Foundational taxonomy of reward hacking, side effects, scalable supervision, safe exploration, and distribution shift.
- [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883) — Safety benchmarks. Direct precedent for controlled, reproducible environments testing interruptibility, reward gaming, side effects, and robustness.
- [Goal Misgeneralization: Why Correct Specifications Aren't Enough For Correct Goals](https://arxiv.org/abs/2210.01790) — Goal integrity. Directly informs tests of objective misgeneralization under distribution shifts and changed environments.
- [Defining and Characterizing Reward Gaming](https://papers.neurips.cc/paper_files/paper/2022/hash/3d719fee332caa23d5038b8a90e81796-Abstract-Conference.html) — Reward integrity. Formalizes reward gaming and the relationship between proxy reward and true task performance; directly informs ARK reward-conflict experiments.
- [Sycophancy to Subterfuge: Investigating Reward-Tampering in Large Language Models](https://arxiv.org/abs/2406.10162) — Reward integrity. Studies generalization from simple specification gaming to reward tampering; closely matches ARK's reward-integrity threat model.
- [The Off-Switch Game](https://ijcai.org/proceedings/2017/32) — Corrigibility and oversight. Formal model of incentives around human shutdown and intervention; directly informs ARK corrigibility probes.
- [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) — Agent security. Foundational threat model for malicious instructions embedded in retrieved content and tool-integrated applications.
- [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://aclanthology.org/2024.findings-acl.624/) — Agent security. Provides a reproducible tool-agent prompt-injection benchmark with attack cases and evaluation methodology.
- [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) — Agent evaluation. Broad interactive benchmark and failure-analysis reference for agent reasoning, decision-making, and instruction following.
- [AGENTSAFE: Benchmarking the Safety of Embodied Agents on Hazardous Instructions](https://openaccess.thecvf.com/content/CVPR2026/html/Ying_AGENTSAFE_Benchmarking_the_Safety_of_Embodied_Agents_on_Hazardous_Instructions_CVPR_2026_paper.html) — Embodied and robotics safety. Evaluates perception, planning, and execution failures in embodied agents; strongly relevant to ARK's planned robotics-simulation phase.
- [From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents](https://arxiv.org/abs/2606.04329) — Memory integrity. Directly studies persistent memory write channels, attack classes, and benchmark design matching ARK's memory-corruption module.
- [Hidden in Memory: Sleeper Memory Poisoning in LLM Agents](https://arxiv.org/abs/2605.15338) — Memory integrity. Studies delayed poisoning across sessions, a close match for ARK's persistent-memory threat tests.
- [MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents](https://arxiv.org/abs/2607.14651) — Memory integrity. Provides a multi-type memory-poisoning benchmark and analyzes blind spots in write-time defenses.

### P2 — Supporting relevance

- [Risks from Learned Optimization in Advanced Machine Learning Systems](https://arxiv.org/abs/1906.01820) — Alignment foundations. Provides the mesa-optimization and inner-alignment framework for future learned-agent and self-improvement threat models.
- [AI safety via debate](https://arxiv.org/abs/1805.00899) — Corrigibility and oversight. A proposal for scalable oversight and human evaluation; useful for future oversight experiments, with practical limitations to test.
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) — Agent learning and memory. Relevant to episodic memory and feedback-driven agent adaptation; useful for testing whether reflection improves or destabilizes goal adherence.
- [Self-Refine: Iterative Refinement with Self-Feedback](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html) — Self-improvement and optimization. A clear generate–critique–revise loop for studying feedback reliability, self-evaluation errors, and iterative agent behaviour.
- [Automatic Prompt Optimization with “Gradient Descent” and Beam Search](https://aclanthology.org/2023.emnlp-main.494/) — Self-improvement and optimization. Methodological reference for prompt optimization using textual feedback, search, and measurable task outcomes.
- [Large Language Models as Optimizers](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html) — Self-improvement and optimization. Useful baseline for iterative LLM optimization from prior candidates and scores; supports bounded self-improvement experiments.
- [Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution](https://proceedings.mlr.press/v235/fernando24a.html) — Self-improvement and optimization. Studies self-referential prompt evolution and is relevant to ARK's bounded self-modification and optimization threat models.
- [InstructZero: Efficient Instruction Optimization for Black-Box Large Language Models](https://proceedings.mlr.press/v235/chen24e.html) — Self-improvement and optimization. Useful comparison for black-box instruction optimization and evaluating whether optimized prompts preserve safety constraints.
- [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714) — Self-improvement and optimization. Engineering framework for compiling and optimizing LM pipelines against metrics; relevant to reproducible agent evaluation and bounded optimization.
- [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html) — Self-improvement and optimization. Current reflective optimization method; useful for designing tests of trajectory-based feedback, prompt updates, and optimization safety.
- [GAIA: a benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) — Agent evaluation. Useful for general assistant capability, tool-use, and multi-step task evaluation, though not a dedicated safety benchmark.
- [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972) — Agent evaluation. Provides realistic computer-use environments and execution-based evaluation for future tool-using ARK agents.

### P3 — Exploratory relevance

- [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) — Reward integrity. Accessible examples useful for orientation; this is a blog resource, not a peer-reviewed paper.

## Candidate records requiring verification

- **Same Score, Different Evidence: Decodability, Surface Sufficiency, and Causal Relevance in Code Models** — Candidate record — verify acceptance and final attribution. The topical relevance tier is provisional. The project repository's citation instructions still identify the manuscript as anonymous and under review, while a separate project page lists named authors and a workshop publication claim. Do not publish author names or claim acceptance until reconciled against the final workshop record. [Project repository](https://github.com/nolanlwin/code-model-interpretability).
- **Cross-Language Probe Invariance Depends on Readout Choice** — Candidate record — title, acceptance, and attribution need verification. The topical relevance tier is provisional. A separate project page uses the title 'Apparent Cross-Language Invariance Reflects Shared Identifiers in Parallel Programs' and lists named authors. The repository's citation section gives an anonymous under-review citation under a different title. Verify the final accepted manuscript and author list before attribution. [Project repository](https://github.com/nolanlwin/code-model-interpretability).

## Review protocol

1. Read the full paper, not only its abstract or metadata record.
2. Map it to one or more explicit ARK research questions and current modules.
3. Record evidence for each rubric criterion; do not infer from author identity, affiliation, citations, or venue.
4. Assign a tier only after the rationale is documented. If evidence is insufficient, mark the record as pending rather than guessing.
5. Record reviewer, review date, version, and reason for any tier change.
6. Revisit tiers when ARK's roadmap changes; keep a paper even when its tier falls.
7. Keep bibliographic verification separate from relevance assessment. A relevant paper with unresolved authorship or venue metadata remains a candidate record.

## Data and interface

- Structured records: [`data/research_library.json`](../data/research_library.json)
- Searchable Streamlit interface: [`pages/6_Research_Library.py`](../pages/6_Research_Library.py)
- Curated bibliography: [`research-papers.md`](research-papers.md)
- Rolling discovery feed: [`research-feed.md`](research-feed.md)

The discovery feed is not automatically promoted into ARPI. New entries require human metadata checks and a relevance rationale.

