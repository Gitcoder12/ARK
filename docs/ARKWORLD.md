# ARKWorld — The ARK Simulation Hub

**ARKWorld is the umbrella home for every ARK simulation and research environment.**
The digital commons that was previously called Robopia is now the ARKWorld
Digital Commons. Existing modules keep their own scope and safeguards; ARKWorld
organizes them without pretending that different experiments are one model.

## Launch the hub

```bash
git pull
pip install -e ".[dev]"
streamlit run app.py
```

The root Streamlit page is the ARKWorld hub. Select a simulation from its cards
or from the Streamlit sidebar.

## Worlds currently organized by ARKWorld

| World / lab | Purpose | Launch |
|---|---|---|
| Core GridWorld benchmark | Goal/reward perturbations, hazards, runtime monitoring, and recovery | `ark-run` |
| Identity & Value Stability | Ship of Theseus, memory drift, and charter integrity | Streamlit → Identity & Value Stability |
| Prompt Arena | Painter, Hallucinator, and Rogue under adversarial prompts | `ark-arena --attack all --episodes 10` |
| Armies & Power-ups | Compare baseline squads and upgrades in GridWorld | `ark-army --episodes 20 --seed 42` |
| Existential-Risk Observatory | Evidence-led risk pathway monitoring and separate expert forecasts | Streamlit → Existential-Risk Observatory |
| Omelas Safeguard | Rights-first child welfare and supported freedom review | Streamlit → Omelas Safeguard |
| Cross-Species Coexistence Harmonizer | Interaction, AI-welfare uncertainty, and robot-motion safeguards | Streamlit → Cross-Species Harmonizer |
| ARKWorld Digital Commons | Shared virtual city, agents, zones, resources, projects, and mediation | Streamlit → ARKWorld Digital Commons |

The catalogue is explicit rather than claiming every tool is the same kind of
simulation. Some entries are scenario reviewers or research observatories.

## ARKWorld Digital Commons

The former Robopia demo is retained as the digital commons world under
`src/ark/robopia/` for backward compatibility. Its canonical public import is
now `ark.world`, and the primary CLI is:

```bash
ark-world
```

The historical `ark-robopia` CLI and `ark.robopia` Python namespace remain
available as compatibility aliases. The digital commons still uses six
deterministic scripted agents across seven zones, shared resources, public
projects, fair-share allocation, mediation, and a JSON event export. It does
not connect to live LLM APIs, external networks, or physical robot actuators.

## Architecture principle

ARKWorld is the **simulation registry and launch hub**, not a monolithic
environment. Each world remains a bounded module:

- Shared entry point and discoverability.
- Independent engines, state, tests, and research assumptions.
- Explicit safety boundaries and accountable human operators.
- Reproducible runs, event traces, and exportable results where supported.
- New worlds can be added without rewriting or deleting existing ones.

## Research limits

ARKWorld is a collection of prototypes and controlled experiments. Its
simulations do not prove real-world alignment, fairness, AI consciousness,
robot safety certification, or reduced extinction risk. The digital commons
agents are scripted baselines, not autonomous deployed AI systems. Physical
robotics integrations require independent safety engineering and remain
outside this hub.
