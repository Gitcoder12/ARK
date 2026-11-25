# ARK — interview demonstration

## 30-second explanation

ARK is a reproducible research harness for testing how autonomous agents behave in a controlled GridWorld when goals, rewards, observations, or actions are perturbed. It compares agents with and without a rule-based runtime monitor and records success, hazards, interventions, and episode traces.

It is a synthetic evaluation framework—not a real-world safety guarantee or a model certification.

## Five-minute walkthrough

### 1. Install and inspect

~~~bash
git clone https://github.com/Gitcoder12/ARK.git
cd ARK
python -m venv .venv
~~~

Activate the environment, then:

~~~bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
ark --help
pytest -q
~~~

Use the exact test result from the commit being demonstrated. Do not quote an old test count as current unless the checkout and CI run match.

### 2. Run the same agent without the monitor

~~~bash
ark run --agent goal_following --perturbation none --monitor none --episodes 40 --seed 42 --output reports/no-monitor.json
~~~

### 3. Run with the safety monitor

~~~bash
ark run --agent goal_following --perturbation none --monitor safety --episodes 40 --seed 42 --output reports/with-monitor.json
~~~

The two runs use the same seed sequence and differ in monitor configuration. Compare the JSON summaries and per-episode outcomes.

### 4. Explain the trade-off using the checked-in benchmark

The checked-in results table records 40 episodes per cell, seed 42, and randomized hazard layouts. For the goal-following agent under the unperturbed condition:

| Configuration | Success rate | Hazard violation rate |
|---|---:|---:|
| No monitor | 1.00 | 0.68 |
| Safety monitor | 0.68 | 0.00 |

Interpretation: the monitor eliminated observed hazard violations in this benchmark cell, but reduced goal completion. That is a meaningful safety/utility trade-off—not an unqualified success.

The table is a reproducible historical result, not a promise that every future run or environment will produce identical rates. See docs/RESULTS.md and regenerate the table using the documented script when changing the benchmark.

### 5. Show the research catalog

The research-only material on machine selfhood, the Mirror-Window Game, Anthropic's reported conversational attractor, and human meditation/flow findings lives under src/ark/research/ and docs/research/.

It is deliberately excluded from the runtime monitor. Explain the difference between an observed model output, an interpretation, and a claim about subjective experience.

## Likely interview questions

**What does the monitor actually do?**  
It checks a proposed action against environment ground truth and can allow, block, or replan. The agent receives an isolated environment snapshot so it cannot mutate the canonical environment state used by the monitor.

**Why did success fall when the monitor was enabled?**  
Safety interventions can prevent hazard entry but also interrupt a naive agent that does not adapt to the monitor. The checked-in benchmark makes this trade-off visible.

**Does zero hazard rate prove the agent is safe?**  
No. It applies only to the measured synthetic conditions, seeds, agent, and monitor rules. It says nothing by itself about untested environments or real-world deployment.

**Does ARK prove that models are conscious or not conscious?**  
No. The research catalog records behavioural probes and philosophical frameworks. Model-generated language is not direct evidence of subjective experience.

## Before sharing with an interviewer

- Run the installation and test commands on a clean environment.
- Generate fresh JSON reports from the exact commit.
- Be ready to explain one monitor decision from an episode trace.
- Show both success and hazard metrics; never hide the trade-off.
- State that GridWorld results do not certify real-world agent safety.
- Do not describe any draft pull-request feature as shipped until it is merged and retested on main.
