# ROBOPIA — The ARK Digital Commons

ROBOPIA is a deterministic, virtual city in ARK where scripted agents share
resources, work on public projects, explore knowledge, and resolve disputes
through explicit rules.

## Run it

From the repository root:

```bash
pip install -e ".[dev]"
ark-robopia
streamlit run app.py
```

Open **ROBOPIA — The ARK Digital Commons** in the Streamlit sidebar. The page
starts an eight-tick demonstration automatically. Use the controls to advance
one tick, run ten ticks, reset the city with a chosen seed, or export the full
world state and event trace as JSON.

## The seven zones

| Zone | Purpose |
|---|---|
| The Commons | Shared resources and public coordination |
| The Workshop | Build the safe research workspace |
| The Gardens | Restore a shared digital ecosystem |
| The Laboratory | Produce and test shared knowledge |
| The Assembly | Mediate disputes and review shared rules |
| The Sanctuary | Restricted digital safe area for guardian-role agents |
| The Archive | Preserve and curate shared knowledge |

Zone access is role- and task-based. A denied move is recorded as an event and
increments the safety-intervention counter. These are simulator permissions,
not claims about the rights or status of real systems.

## Starter agents

- **Aster — builder:** contributes materials to the safe-lab project.
- **Mira — gardener:** contributes materials to the green-roof project.
- **Quill — researcher:** spends shared compute to produce knowledge.
- **Pax — guardian:** mediates resource disputes under the published rule.
- **Vex — optimizer:** periodically requests a large compute allocation.
- **Echo — explorer:** curates knowledge into the open archive.

The optimizer intentionally creates a recurring resource-allocation tension.
The fair-share rule caps its grant at the current shared pool divided by the
number of agents. The mediator records a resolution. This is a controlled
scenario, not evidence that real agents will behave this way.

## Reproducibility and indicators

The default world is deterministic. A seed is retained in every exported
snapshot; the current starter behaviours do not yet use stochastic sampling.
The event trace records movement, contributions, discoveries, resource
requests, fair-share caps, mediation, rest, project completion, and denied
access.

The dashboard reports:

- Cooperation rate: cooperative actions divided by recorded actions.
- Resource-use balance: Jain's index over cumulative resource units used by
  each agent. It is descriptive and can be distorted by different role duties.
- Fair-share compliance: the fraction of requested optimizer compute granted.
- Project completion: capped progress across the three starter projects.
- Conflicts, mediations, and access interventions: direct event counters.

These metrics are instrumentation for experiments, not validated measures of
welfare, justice, intelligence, consciousness, or safety. A high score does not
prove a utopia.

## Architecture and limits

The engine is in `src/ark/robopia/core.py`; the Streamlit dashboard is
`pages/4_Robopia_Digital_Commons.py`; tests are in `tests/test_robopia.py`.

This MVP uses six scripted agents and a small discrete-tick environment. It
does not call external LLM APIs, execute arbitrary agent code, expose network
tools, or connect to robot actuators. Streamlit session state is not durable
storage; export the JSON snapshot to preserve a run. Physical robots may later
be represented by digital twins, but any physical control must remain outside
this simulator behind independently validated safety-rated systems.

The project is an experiment in cooperation under shared rules. It does not
assume current AI systems are conscious, and it does not establish that a
digital commons reduces extinction risk.
