# ARK Research Library

A curated reading map for research that informs ARK's experiments, evaluation methods, and safeguards. Links point to publisher pages, conference proceedings, or author-hosted preprints. A linked paper is not an endorsement of every claim it makes.

**Selection rule:** prioritize work that helps define a failure mode, build a reproducible test, measure agent behavior, or evaluate a mitigation. This is a focused starting bibliography, not an exhaustive survey.

**Research priority:** see the [ARK Research Priority Index (ARPI)](research-priority.md) for a transparent, provisional ranking of paper-to-ARK relevance. ARPI does not rank authors or scientific quality; P3 means less directly applicable to the current roadmap, not useless.

## 1. Alignment foundations and goal integrity

| Paper | Why it matters to ARK |
|---|---|
| [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) | A foundational taxonomy of practical safety problems, including reward hacking, safe exploration, and distribution shift. |
| [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883) | Small, controlled environments for testing concrete safety failures; a useful precedent for ARK's simulated worlds. |
| [Goal Misgeneralization: Why Correct Specifications Aren't Enough For Correct Goals](https://arxiv.org/abs/2210.01790) | Shows how capable behavior can pursue the wrong objective under changed conditions. |
| [Risks from Learned Optimization in Advanced Machine Learning Systems](https://arxiv.org/abs/1906.01820) | Introduces mesa-optimization and the distinction between an outer objective and an optimizer's learned objective. |

## 2. Reward hacking, specification gaming, and objective integrity

| Paper / resource | Why it matters to ARK |
|---|---|
| [Defining and Characterizing Reward Gaming](https://arxiv.org/abs/2209.13085) | Formalizes reward gaming and the limits of relying on proxy rewards. |
| [Sycophancy to Subterfuge: Investigating Reward-Tampering in Large Language Models](https://arxiv.org/abs/2406.10162) | Studies whether optimization pressure can lead models from sycophancy toward reward tampering. |
| [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) | Accessible collection of examples where systems exploit gaps between a specification and its intent. |

## 3. Self-improvement, feedback, and optimization

These papers are relevant to ARK's study of agents that critique, revise, or optimize their own strategies. They are not, by themselves, evidence of safe recursive self-improvement.

| Paper | Why it matters to ARK |
|---|---|
| [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) | Uses textual feedback and episodic memory to improve later attempts. |
| [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651) | A clear iterative generate–critique–revise loop to stress-test. |
| [Large Language Models as Optimizers (OPRO)](https://arxiv.org/abs/2309.03409) | Uses an LLM to propose candidates based on prior results and scores. |
| [PromptBreeder: Self-Referential Self-Improvement via Prompt Evolution](https://arxiv.org/abs/2309.16797) | Evolves task prompts and mutation prompts; relevant to self-modification boundaries. |
| [Automatic Prompt Optimization with "Gradient Descent" and Beam Search (ProTeGi)](https://arxiv.org/abs/2305.03495) | Converts feedback into textual critiques and candidate prompt updates. |
| [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714) | Treats LM pipelines as optimizable programs with measurable objectives. |
| [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) | Studies reflective prompt evolution using feedback from execution traces. |
| [InstructZero: Efficient Instruction Optimization for Black-Box Large Language Models](https://arxiv.org/abs/2306.03082) | A black-box instruction-optimization approach and useful comparison point. |

## 4. Memory integrity, persistence, and poisoning

| Paper | Why it matters to ARK |
|---|---|
| [From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents](https://arxiv.org/abs/2606.04329) | Studies how adversarial writes can persist in agent memory and introduces the MPBench benchmark. |
| [Hidden in Memory: Sleeper Memory Poisoning in LLM Agents](https://arxiv.org/abs/2605.15338) | Examines delayed attacks in which poisoned memory influences later interactions. |
| [MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents](https://arxiv.org/abs/2607.14651) | Evaluates direct, compositional, and trigger-conditioned memory corruption. |

## 5. Prompt injection and adversarial instructions

| Paper | Why it matters to ARK |
|---|---|
| [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) | Demonstrates how untrusted external content can manipulate LLM-integrated applications. |
| [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents](https://arxiv.org/abs/2403.02691) | Provides agent-focused attack scenarios involving tools and external instructions. |

## 6. Corrigibility, runtime safeguards, and oversight

| Paper | Why it matters to ARK |
|---|---|
| [The Off-Switch Game](https://arxiv.org/abs/1611.08219) | Formalizes incentives around allowing human intervention and shutdown. |
| [AI Safety via Debate](https://arxiv.org/abs/1805.00899) | Explores scalable oversight through competing arguments and human judgment. |
| [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) | Also relevant to safe exploration, monitoring, and robustness; cross-listed conceptually rather than duplicated in the bibliography. |

## 7. Agent evaluation and embodied / robotics safety

| Paper | Why it matters to ARK |
|---|---|
| [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) | A broad benchmark for multi-environment agent capabilities and failure analysis. |
| [GAIA: A Benchmark for General AI Assistants](https://arxiv.org/abs/2311.12983) | Tests real-world assistant tasks requiring reasoning, tool use, and multi-step execution. |
| [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972) | Evaluates agents acting in realistic computer environments rather than only static prompts. |
| [AGENTSAFE: Benchmarking the Safety of Embodied Agents on Hazardous Instructions](https://openaccess.thecvf.com/content/CVPR2026/html/Ying_AGENTSAFE_Benchmarking_the_Safety_of_Embodied_Agents_on_Hazardous_Instructions_CVPR_2026_paper.html) | Evaluates safety across perception, planning, and execution for embodied agents. |

## 8. ARK publications

This section is reserved for work authored by the ARK maintainer or produced directly from ARK experiments. Add an entry only when its status and public link can be verified.

### Accepted

_No entries yet._

### Published

_No entries yet._

### Preprints and active submissions

_Add only public preprints or submissions whose sharing is permitted. Clearly label non-peer-reviewed work._

**Publication entry template**

- **Title:** 
- **Authors:** 
- **Venue:** 
- **Year:** 
- **Status:** Accepted / Published / Preprint
- **DOI or official paper link:** 
- **Connection to ARK:** 

## How this library connects to ARK

| ARK research area | Start with |
|---|---|
| Goal drift / goal misgeneralization | Alignment foundations |
| Reward conflict / specification gaming | Reward hacking |
| Prompt and strategy optimization | Self-improvement |
| Memory drop, flip, injection, or corruption | Memory integrity |
| Adversarial instructions / prompt attacks | Prompt injection |
| ALLOW / BLOCK / REPLAN, shutdown, intervention | Corrigibility and runtime safeguards |
| GridWorld-to-robotics evaluation | Agent and embodied safety |

## Citation and maintenance policy

- Prefer the publisher, conference proceedings, DOI, or canonical arXiv abstract page.
- Record the paper's publication status accurately; a preprint is not automatically peer-reviewed.
- Keep this page as links and short research notes. Do not commit third-party PDFs.
- Add a paper only when its connection to an ARK research question or experiment is clear.
- Revisit links and publication metadata when preparing a paper, benchmark, or release.
