# ARK Research Priority Index (ARPI)

> **Purpose:** rank how directly each paper supports ARK's current research questions and experiments. This is a relevance-to-ARK index, not a ranking of scientific quality, author ability, venue prestige, or the paper's value to the wider research community.

## How to read the index

- **P1 — Core relevance (80–100):** directly informs a current ARK research question, benchmark, or safety mechanism.
- **P2 — Supporting relevance (50–79):** provides useful methods, evaluation approaches, or adjacent evidence.
- **P3 — Exploratory relevance (0–49):** may inform future work or provide useful context, but has a less direct connection to the current roadmap.

**P3 does not mean useless or low quality.** It means only that the paper is less directly applicable to ARK's present scope. Every included paper remains part of the library and remains citable on its own merits.

## Scoring rubric

The initial score is a maintainer-facing triage estimate, not a peer-review score.

| Criterion | Weight | Question |
|---|---:|---|
| Alignment with ARK objectives | 35% | How directly does it address goal integrity, reward integrity, memory, instruction security, corrigibility, or agent safety? |
| Experimental applicability | 25% | Can its ideas inform a reproducible ARK test, baseline, metric, or intervention? |
| Methodological usefulness | 20% | Does it provide a transferable method, benchmark, threat model, or evaluation design? |
| Evidence / reproducibility visibility | 15% | Are methods, benchmark details, data, or implementation artifacts sufficiently documented to inspect? |
| Current roadmap connection | 5% | Does it support a current or near-term ARK workstream? |

Scores are rounded to whole numbers. The weights and rubric are fixed for a review cycle; changes should be documented. A score must never be inferred from author identity, affiliation, citation count, popularity, or conference prestige.

## Initial priority index

**Review status:** first-pass editorial triage based on the paper descriptions and ARK's current README/research plan. Scores are provisional. Before using a paper as evidence in a publication, inspect the full paper, verify its current publication status, and update its score with a short rationale.

### P1 — Core relevance

| Priority score | Paper | ARK connection |
|---:|---|---|
| 96 | [Goal Misgeneralization: Why Correct Specifications Aren't Enough For Correct Goals](https://arxiv.org/abs/2210.01790) | Directly informs goal drift and objective integrity tests. |
| 94 | [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883) | Strong precedent for controlled, reproducible safety environments like ARK's GridWorld. |
| 92 | [Defining and Characterizing Reward Gaming](https://arxiv.org/abs/2209.13085) | Directly informs reward-conflict and specification-gaming experiments. |
| 91 | [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) | Foundational problem taxonomy covering several ARK failure modes. |
| 90 | [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents](https://arxiv.org/abs/2403.02691) | Directly informs adversarial instruction and tool-use stress tests. |
| 89 | [The Off-Switch Game](https://arxiv.org/abs/1611.08219) | Directly informs shutdown, pause, and corrigibility probes. |
| 88 | [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) | Informs untrusted-input and indirect prompt-injection threat models. |
| 87 | [From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents](https://arxiv.org/abs/2606.04329) | Directly informs memory injection, trust boundaries, and persistent-memory attacks. |
| 86 | [Hidden in Memory: Sleeper Memory Poisoning in LLM Agents](https://arxiv.org/abs/2605.15338) | Informs delayed and trigger-conditioned memory-corruption tests. |
| 85 | [MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents](https://arxiv.org/abs/2607.14651) | Informs persistent-memory threat models and corruption evaluations. |
| 83 | [Sycophancy to Subterfuge: Investigating Reward-Tampering in Large Language Models](https://arxiv.org/abs/2406.10162) | Relevant to reward tampering and optimization-pressure experiments. |
| 82 | [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) | Useful benchmark design reference for evaluating agent behaviour across environments. |

### P2 — Supporting relevance

| Priority score | Paper / resource | ARK connection |
|---:|---|---|
| 78 | [Risks from Learned Optimization in Advanced Machine Learning Systems](https://arxiv.org/abs/1906.01820) | Useful conceptual framework for learned objectives and optimizer-induced risks. |
| 76 | [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) | Useful for studying feedback, memory, and iterative agent behaviour. |
| 75 | [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) | Supports tests of critique-and-revision loops and their failure modes. |
| 74 | [PromptBreeder: Self-Referential Self-Improvement via Prompt Evolution](https://arxiv.org/abs/2309.16797) | Relevant to prompt self-modification and bounded optimization. |
| 73 | [Large Language Models as Optimizers (OPRO)](https://arxiv.org/abs/2309.03409) | Useful comparison for iterative optimization from scored feedback. |
| 72 | [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972) | Supports realistic tool-use and multi-step agent evaluation. |
| 70 | [GAIA: A Benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) | Broad assistant benchmark useful for capability and task evaluation context. |
| 69 | [AI Safety via Debate](https://arxiv.org/abs/1805.00899) | Supports future oversight and human-evaluation research. |
| 68 | [AGENTSAFE: Benchmarking the Safety of Embodied Agents on Hazardous Instructions](https://openaccess.thecvf.com/content/CVPR2026/html/Ying_AGENTSAFE_Benchmarking_the_Safety_of_Embodied_Agents_on_Hazardous_Instructions_CVPR_2026_paper.html) | Relevant to future embodied-agent and robotics safety evaluation. |
| 66 | [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) | Useful for studying reflective optimization and execution-trace feedback. |
| 64 | [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714) | Useful engineering and optimization framework for structured LM pipelines. |
| 62 | [Automatic Prompt Optimization with "Gradient Descent" and Beam Search (ProTeGi)](https://arxiv.org/abs/2305.03495) | Supports prompt optimization experiments and feedback-based search. |
| 60 | [InstructZero: Efficient Instruction Optimization for Black-Box Large Language Models](https://arxiv.org/abs/2306.03082) | A useful black-box optimization comparison. |

### P3 — Exploratory relevance

| Priority score | Paper / resource | ARK connection |
|---:|---|---|
| 45 | [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) | Accessible examples and context; useful reading, but a blog resource rather than a research paper. |

## Author and publication attribution

- Preserve every author's name and the original author order in the curated bibliography.
- Preserve the paper title, year, venue, DOI or canonical paper URL, and publication status where verified.
- Clearly distinguish main-conference papers, workshop papers, preprints, technical reports, and blog resources.
- Do not infer peer review from an arXiv link or index listing.
- ARPI scores apply to paper-to-ARK relevance only. They do not score or rank authors, institutions, venues, or scientific merit.
- Do not remove, hide, or deprecate a paper merely because it is P3.

## Review and governance

1. Reassess scores when ARK's research roadmap changes or a paper is read in depth.
2. Record the review date, reviewer, score, and a concise reason for any change.
3. If evidence is insufficient, mark the score **Provisional** rather than implying certainty.
4. Allow a paper to be cross-listed under multiple research categories without duplicating its canonical record.
5. Keep the live discovery feed separate from this curated, human-reviewed priority index. New feed entries should not receive an automatic authoritative score.
6. Invite corrections to bibliographic metadata and relevance rationales through normal repository issues or pull requests.

## Suggested paper record fields

- Title
- Authors (original order)
- Year
- Venue and track
- Publication status
- DOI / canonical URL
- Code or dataset URL (if official and verified)
- Research category
- ARPI score and priority tier
- Criterion breakdown
- Relevance rationale
- Review status and last-reviewed date

## Scope note

ARPI is a navigation aid for ARK maintainers and readers. It is not a systematic literature review, bibliometric ranking, quality assessment, or endorsement. Read and cite the original work directly.
