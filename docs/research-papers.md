# ARK Research Library

A curated, searchable bibliography supporting ARK's research questions, evaluation methods, and safeguards. The Streamlit page is available at `pages/6_Research_Library.py`; the structured catalogue is `data/research_library.json`.

**Attribution policy:** author names are preserved in the original order shown by the canonical publication record. Venue and publication status are recorded separately. Preprints are not described as peer-reviewed publications. Candidate records with unresolved metadata are clearly isolated and are not presented as confirmed acceptances.

**Priority:** ARPI measures relevance to ARK's current roadmap only. It does not measure paper quality, author merit, or general scientific importance. See [Research Priority Index](research-priority.md).

## 1. Alignment foundations

### [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565)

- **Authors:** Dario Amodei, Chris Olah, Jacob Steinhardt, Paul Christiano, John Schulman, Dan Mané
- **Year:** 2016
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.1606.06565
- **Why it matters:** Foundational taxonomy of reward hacking, side effects, scalable supervision, safe exploration, and distribution shift.
- **Metadata source:** arXiv

### [Risks from Learned Optimization in Advanced Machine Learning Systems](https://arxiv.org/abs/1906.01820)

- **Authors:** Evan Hubinger, Chris van Merwijk, Vladimir Mikulik, Joar Skalse, Scott Garrabrant
- **Year:** 2019
- **Venue:** arXiv preprint (v3, 2021)
- **Status:** Preprint
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.1906.01820
- **Why it matters:** Provides the mesa-optimization and inner-alignment framework for future learned-agent and self-improvement threat models.
- **Metadata source:** arXiv

## 2. Safety benchmarks

### [AI Safety Gridworlds](https://arxiv.org/abs/1711.09883)

- **Authors:** Jan Leike, Miljan Martic, Victoria Krakovna, Pedro A. Ortega, Tom Everitt, Andrew Lefrancq, Laurent Orseau, Shane Legg
- **Year:** 2017
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.1711.09883
- **Why it matters:** Direct precedent for controlled, reproducible environments testing interruptibility, reward gaming, side effects, and robustness.
- **Metadata source:** arXiv

## 3. Goal integrity

### [Goal Misgeneralization: Why Correct Specifications Aren't Enough For Correct Goals](https://arxiv.org/abs/2210.01790)

- **Authors:** Rohin Shah, Vikrant Varma, Ramana Kumar, Mary Phuong, Victoria Krakovna, Jonathan Uesato, Zac Kenton
- **Year:** 2022
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2210.01790
- **Why it matters:** Directly informs tests of objective misgeneralization under distribution shifts and changed environments.
- **Metadata source:** arXiv

## 4. Reward integrity

### [Defining and Characterizing Reward Gaming](https://papers.neurips.cc/paper_files/paper/2022/hash/3d719fee332caa23d5038b8a90e81796-Abstract-Conference.html)

- **Authors:** Joar Skalse, Nikolaus H. R. Howe, Dmitrii Krasheninnikov, David Krueger
- **Year:** 2022
- **Venue:** NeurIPS 2022 — main conference
- **Status:** Published conference paper
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.52202/068431-0687
- **Why it matters:** Formalizes reward gaming and the relationship between proxy reward and true task performance; directly informs ARK reward-conflict experiments.
- **Metadata source:** NeurIPS proceedings

### [Sycophancy to Subterfuge: Investigating Reward-Tampering in Large Language Models](https://arxiv.org/abs/2406.10162)

- **Authors:** Carson Denison, Monte MacDiarmid, Fazl Barez, David Duvenaud, Shauna Kravec, Samuel Marks, Nicholas Schiefer, Ryan Soklaski, Alex Tamkin, Jared Kaplan, Buck Shlegeris, Samuel R. Bowman, Ethan Perez, Evan Hubinger
- **Year:** 2024
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2406.10162
- **Why it matters:** Studies generalization from simple specification gaming to reward tampering; closely matches ARK's reward-integrity threat model.
- **Metadata source:** arXiv and author-maintained code repository

### [Specification gaming: the flip side of AI ingenuity](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/)

- **Authors:** DeepMind
- **Year:** 2020
- **Venue:** DeepMind research blog
- **Status:** Research explainer / blog post
- **ARK priority:** P3 — Exploratory relevance
- **Why it matters:** Accessible examples useful for orientation; this is a blog resource, not a peer-reviewed paper.
- **Metadata source:** DeepMind

## 5. Corrigibility and oversight

### [The Off-Switch Game](https://ijcai.org/proceedings/2017/32)

- **Authors:** Dylan Hadfield-Menell, Anca Dragan, Pieter Abbeel, Stuart Russell
- **Year:** 2017
- **Venue:** IJCAI 2017 — main track
- **Status:** Published conference paper
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.24963/ijcai.2017/32
- **Why it matters:** Formal model of incentives around human shutdown and intervention; directly informs ARK corrigibility probes.
- **Metadata source:** IJCAI proceedings

### [AI safety via debate](https://arxiv.org/abs/1805.00899)

- **Authors:** Geoffrey Irving, Paul Christiano, Dario Amodei
- **Year:** 2018
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.1805.00899
- **Why it matters:** A proposal for scalable oversight and human evaluation; useful for future oversight experiments, with practical limitations to test.
- **Metadata source:** arXiv

## 6. Agent security

### [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173)

- **Authors:** Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, Mario Fritz
- **Year:** 2023
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2302.12173
- **Why it matters:** Foundational threat model for malicious instructions embedded in retrieved content and tool-integrated applications.
- **Metadata source:** arXiv

### [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://aclanthology.org/2024.findings-acl.624/)

- **Authors:** Qiusi Zhan, Zhixiang Liang, Zifan Ying, Daniel Kang
- **Year:** 2024
- **Venue:** Findings of ACL 2024
- **Status:** Published conference findings
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.18653/v1/2024.findings-acl.624
- **Why it matters:** Provides a reproducible tool-agent prompt-injection benchmark with attack cases and evaluation methodology.
- **Metadata source:** ACL Anthology

## 7. Agent learning and memory

### [Reflexion: Language Agents with Verbal Reinforcement Learning](https://papers.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)

- **Authors:** Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao
- **Year:** 2023
- **Venue:** NeurIPS 2023 — main conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.52202/075280-0377
- **Why it matters:** Relevant to episodic memory and feedback-driven agent adaptation; useful for testing whether reflection improves or destabilizes goal adherence.
- **Metadata source:** NeurIPS proceedings

## 8. Self-improvement and optimization

### [Self-Refine: Iterative Refinement with Self-Feedback](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html)

- **Authors:** Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, Peter Clark
- **Year:** 2023
- **Venue:** NeurIPS 2023 — main conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.52202/075280-2019
- **Why it matters:** A clear generate–critique–revise loop for studying feedback reliability, self-evaluation errors, and iterative agent behaviour.
- **Metadata source:** NeurIPS proceedings

### [Automatic Prompt Optimization with “Gradient Descent” and Beam Search](https://aclanthology.org/2023.emnlp-main.494/)

- **Authors:** Reid Pryzant, Dan Iter, Jerry Li, Yin Lee, Chenguang Zhu, Michael Zeng
- **Year:** 2023
- **Venue:** EMNLP 2023 — main conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.18653/v1/2023.emnlp-main.494
- **Why it matters:** Methodological reference for prompt optimization using textual feedback, search, and measurable task outcomes.
- **Metadata source:** ACL Anthology

### [Large Language Models as Optimizers](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3339f19c5fcee3ad74502947a32be9e6-Abstract-Conference.html)

- **Authors:** Chengrun Yang, Xuezhi Wang, Yifeng Lu, Hanxiao Liu, Quoc V. Le, Denny Zhou, Xinyun Chen
- **Year:** 2024
- **Venue:** ICLR 2024 — conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.2309.03409
- **Why it matters:** Useful baseline for iterative LLM optimization from prior candidates and scores; supports bounded self-improvement experiments.
- **Metadata source:** ICLR proceedings

### [Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution](https://proceedings.mlr.press/v235/fernando24a.html)

- **Authors:** Chrisantha Fernando, Dylan Sunil Banarse, Henryk Michalewski, Simon Osindero, Tim Rocktäschel
- **Year:** 2024
- **Venue:** ICML 2024 — PMLR
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **Why it matters:** Studies self-referential prompt evolution and is relevant to ARK's bounded self-modification and optimization threat models.
- **Metadata source:** PMLR proceedings

### [InstructZero: Efficient Instruction Optimization for Black-Box Large Language Models](https://proceedings.mlr.press/v235/chen24e.html)

- **Authors:** Lichang Chen, Jiuhai Chen, Tom Goldstein, Heng Huang, Tianyi Zhou
- **Year:** 2024
- **Venue:** ICML 2024 — PMLR
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **Why it matters:** Useful comparison for black-box instruction optimization and evaluating whether optimized prompts preserve safety constraints.
- **Metadata source:** PMLR proceedings

### [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714)

- **Authors:** Omar Khattab, Arnav Singhvi, Paridhi Maheshwari, Zhiyuan Zhang, Keshav Santhanam, Sri Vardhamanan, Saiful Haq, Ashutosh Sharma, Thomas T. Joshi, Hanna Moazam, Heather Miller, Matei Zaharia, Christopher Potts
- **Year:** 2024
- **Venue:** ICLR 2024 — conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.2310.03714
- **Why it matters:** Engineering framework for compiling and optimizing LM pipelines against metrics; relevant to reproducible agent evaluation and bounded optimization.
- **Metadata source:** arXiv and ICLR paper

### [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html)

- **Authors:** Lakshya A. Agrawal, Shangyin Tan, Dilara Soylu, Noah Ziems, Rishi Khare, Krista Opsahl-Ong, Arnav Singhvi, Herumb Shandilya, Michael J. Ryan, Meng Jiang, Christopher Potts, Koushik Sen, Alexandros G. Dimakis, Ion Stoica, Dan Klein, Matei Zaharia, Omar Khattab
- **Year:** 2026
- **Venue:** ICLR 2026 — conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.2507.19457
- **Why it matters:** Current reflective optimization method; useful for designing tests of trajectory-based feedback, prompt updates, and optimization safety.
- **Metadata source:** ICLR proceedings

## 9. Agent evaluation

### [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)

- **Authors:** Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, Jie Tang
- **Year:** 2024
- **Venue:** ICLR 2024 — conference
- **Status:** Published conference paper
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2308.03688
- **Why it matters:** Broad interactive benchmark and failure-analysis reference for agent reasoning, decision-making, and instruction following.
- **Metadata source:** arXiv and ICLR proceedings metadata

### [GAIA: a benchmark for General AI Assistants](https://proceedings.iclr.cc/paper_files/paper/2024/hash/25ae35b5b1738d80f1f03a8713e405ec-Abstract-Conference.html)

- **Authors:** Grégoire Mialon, Clémentine Fourrier, Thomas Wolf, Yann LeCun, Thomas Scialom
- **Year:** 2024
- **Venue:** ICLR 2024 — main conference
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.2311.12983
- **Why it matters:** Useful for general assistant capability, tool-use, and multi-step task evaluation, though not a dedicated safety benchmark.
- **Metadata source:** ICLR proceedings

### [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)

- **Authors:** Tianbao Xie, Danyang Zhang, Jixuan Chen, Xiaochuan Li, Siheng Zhao, Ruisheng Cao, Toh Jing Hua, Zhoujun Cheng, Dongchan Shin, Fangyu Lei, Yitao Liu, Yiheng Xu, Shuyan Zhou, Silvio Savarese, Caiming Xiong, Victor Zhong, Tao Yu
- **Year:** 2024
- **Venue:** NeurIPS 2024
- **Status:** Published conference paper
- **ARK priority:** P2 — Supporting relevance
- **DOI:** 10.48550/arXiv.2404.07972
- **Why it matters:** Provides realistic computer-use environments and execution-based evaluation for future tool-using ARK agents.
- **Metadata source:** arXiv and official project repository

## 10. Embodied and robotics safety

### [AGENTSAFE: Benchmarking the Safety of Embodied Agents on Hazardous Instructions](https://openaccess.thecvf.com/content/CVPR2026/html/Ying_AGENTSAFE_Benchmarking_the_Safety_of_Embodied_Agents_on_Hazardous_Instructions_CVPR_2026_paper.html)

- **Authors:** Zonghao Ying, Le Wang, Yisong Xiao, Jiakai Wang, Yuqing Ma, Jinyang Guo, Zhenfei Yin, Mingchuan Zhang, Aishan Liu, Xianglong Liu
- **Year:** 2026
- **Venue:** CVPR 2026
- **Status:** Published conference paper
- **ARK priority:** P1 — Core relevance
- **Why it matters:** Evaluates perception, planning, and execution failures in embodied agents; strongly relevant to ARK's planned robotics-simulation phase.
- **Metadata source:** CVF Open Access proceedings

## 11. Memory integrity

### [From Untrusted Input to Trusted Memory: A Systematic Study of Memory Poisoning Attacks in LLM Agents](https://arxiv.org/abs/2606.04329)

- **Authors:** Pritam Dash, Tongyu Ge, Aditi Jain, Tanmay Shah, Zhiwei Shang
- **Year:** 2026
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2606.04329
- **Why it matters:** Directly studies persistent memory write channels, attack classes, and benchmark design matching ARK's memory-corruption module.
- **Metadata source:** arXiv

### [Hidden in Memory: Sleeper Memory Poisoning in LLM Agents](https://arxiv.org/abs/2605.15338)

- **Authors:** Sidharth Pulipaka, Stanislau Hlebik, Leonidas Raghav, Sahar Abdelnabi, Vyas Raina, Ivaxi Sheth, Mario Fritz
- **Year:** 2026
- **Venue:** arXiv preprint
- **Status:** Preprint; conference submission status not independently confirmed
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2605.15338
- **Why it matters:** Studies delayed poisoning across sessions, a close match for ARK's persistent-memory threat tests.
- **Metadata source:** arXiv

### [MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents](https://arxiv.org/abs/2607.14651)

- **Authors:** Jifeng Gao, Kang Xia, Yi Zhang, Xiaobin Hong, Mingkai Lin, Xingshen Wei, Wenzhong Li, Sanglu Lu
- **Year:** 2026
- **Venue:** arXiv preprint
- **Status:** Preprint
- **ARK priority:** P1 — Core relevance
- **DOI:** 10.48550/arXiv.2607.14651
- **Why it matters:** Provides a multi-type memory-poisoning benchmark and analyzes blind spots in write-time defenses.
- **Metadata source:** arXiv

## 12. Interpretability and evidence quality

### [Same Score, Different Evidence: Decodability, Surface Sufficiency, and Causal Relevance in Code Models](https://github.com/nolanlwin/code-model-interpretability)

- **Authors:** Not independently verified; see metadata note
- **Year:** 2026
- **Venue:** NeurIPS 2026 Interpretability as a Science workshop — claimed on a project page; not independently confirmed
- **Status:** Candidate record — verify acceptance and final attribution
- **ARK priority:** P2 — Supporting relevance
- **Why it matters:** Highly relevant methodology for separating decodability, surface-feature shortcuts, and causal evidence; priority reflects topical fit only.
- **Metadata source:** Project repository and conflicting author-site metadata
- **Verification note:** The project repository's citation instructions still identify the manuscript as anonymous and under review, while a separate project page lists named authors and a workshop publication claim. Do not publish author names or claim acceptance until reconciled against the final workshop record.

### [Cross-Language Probe Invariance Depends on Readout Choice](https://github.com/nolanlwin/code-model-interpretability)

- **Authors:** Not independently verified; see metadata note
- **Year:** 2026
- **Venue:** NeurIPS 2026 LP4FM workshop — claimed on project materials; acceptance not independently confirmed
- **Status:** Candidate record — title, acceptance, and attribution need verification
- **ARK priority:** P2 — Supporting relevance
- **Why it matters:** Relevant to detecting surface-level shortcuts and testing whether apparent generalization survives identifier-controlled evaluations.
- **Metadata source:** Project repository and conflicting project-page title
- **Verification note:** A separate project page uses the title 'Apparent Cross-Language Invariance Reflects Shared Identifiers in Parallel Programs' and lists named authors. The repository's citation section gives an anonymous under-review citation under a different title. Verify the final accepted manuscript and author list before attribution.

## Publication and attribution rules

- Cite all authors in the source's original order; never infer missing authors.
- Prefer publisher proceedings, DOI records, official conference pages, or the canonical arXiv record.
- Record workshop papers, main-track papers, preprints, technical reports, and blog posts accurately.
- Do not claim acceptance based only on an author's social post, project page, or a preprint listing.
- Keep all included work discoverable regardless of priority tier.
- The live research feed is a discovery channel; it is not the curated bibliography or an automatic priority ranking.
- Do not commit third-party PDFs unless the licence and repository policy explicitly permit it.
