"""Streamlit dashboard for the ARKWorld Digital Commons."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ark.world import (  # noqa: E402
    Zone,
    advance_tick,
    create_world,
    run_simulation,
    world_metrics,
)

st.set_page_config(
    page_title="ARKWorld — ARK Digital Commons",
    page_icon="🌐",
    layout="wide",
)
st.title("ARKWorld")
st.subheader("The ARK Digital Commons")
st.caption(
    "A shared digital city for simulated AI agents to build, explore, collaborate, "
    "and resolve resource disputes."
)
st.info(
    "This is a deterministic, scripted-agent research simulation. It does not "
    "connect to live AI services, external networks, or physical robot hardware."
)

if "arkworld_state" not in st.session_state:
    st.session_state.arkworld_state = run_simulation(create_world(seed=42), 8)

world = st.session_state.arkworld_state

with st.sidebar:
    st.header("World controls")
    chosen_seed = st.number_input("Reset seed", min_value=0, max_value=2**31 - 1, value=42)
    if st.button("Advance 1 tick", use_container_width=True):
        advance_tick(world)
    if st.button("Run 10 ticks", type="primary", use_container_width=True):
        run_simulation(world, 10)
    if st.button("Reset city", use_container_width=True):
        st.session_state.arkworld_state = create_world(int(chosen_seed))
        world = st.session_state.arkworld_state
        run_simulation(world, 8)
    st.divider()
    st.caption("The city advances only when you use these controls.")

metrics = world_metrics(world)
top = st.columns(5)
top[0].metric("World tick", world.tick)
top[1].metric("Simulated agents", len(world.agents))
top[2].metric("Projects complete", f"{metrics['completed_projects']}/3")
top[3].metric("Conflicts mediated", world.conflicts_resolved)
top[4].metric("Safety interventions", world.safety_interventions)

city_tab, agents_tab, trace_tab = st.tabs(
    ["🌆 City map", "🤖 Agents & resources", "📜 Event trace"]
)

with city_tab:
    st.subheader("Seven connected digital zones")
    st.caption(
        "Access is task- and role-based, not a permanent division between kinds of agents."
    )
    zone_columns = st.columns(4)
    zones = list(Zone)
    for index, zone in enumerate(zones):
        occupants = [
            agent.name for agent in world.agents if agent.current_zone is zone
        ]
        with zone_columns[index % 4]:
            st.markdown(f"**{zone.value.replace('_', ' ').title()}**")
            st.write(", ".join(occupants) if occupants else "No agents present")
    st.divider()
    st.subheader("Shared city projects")
    descriptions = {
        "safe_lab": "A safer shared research workspace",
        "green_roof": "A restored digital garden",
        "open_archive": "A shared knowledge archive",
    }
    for project, target in {
        "safe_lab": 4,
        "green_roof": 4,
        "open_archive": 3,
    }.items():
        progress = min(world.projects[project], target)
        st.write(f"**{project.replace('_', ' ').title()}** — {descriptions[project]}")
        st.progress(progress / target, text=f"{progress}/{target} work units")

with agents_tab:
    st.subheader("Agent roster")
    st.dataframe(
        [
            {
                "Agent": agent.name,
                "Role": agent.role,
                "Current zone": agent.current_zone.value,
                "Energy": agent.energy,
                "Contributions": agent.contribution,
                "Discoveries": agent.discoveries,
            }
            for agent in world.agents
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Shared resource pools")
    resource_columns = st.columns(3)
    for column, resource in zip(
        resource_columns, ("compute", "materials", "knowledge"), strict=True
    ):
        column.metric(resource.title(), world.resources.get(resource, 0))

    st.subheader("Research indicators")
    indicator_columns = st.columns(4)
    indicator_columns[0].metric("Cooperation rate", f"{metrics['cooperation_rate']:.0%}")
    indicator_columns[1].metric(
        "Resource-use balance", f"{metrics['resource_use_balance']:.2f}"
    )
    indicator_columns[2].metric(
        "Fair-share compliance", f"{metrics['fair_share_compliance']:.0%}"
    )
    indicator_columns[3].metric("Project completion", f"{metrics['project_completion']:.0%}")
    st.caption(
        "These are descriptive simulator metrics, not validated measures of real-world "
        "fairness, welfare, consciousness, or safety."
    )

with trace_tab:
    st.subheader("Latest world events")
    rows = [
        {
            "Tick": event.tick,
            "Actor": event.actor,
            "Event": event.kind.value,
            "Detail": event.detail,
        }
        for event in reversed(world.events[-40:])
    ]
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.write("No events yet.")

    st.download_button(
        "Export complete world snapshot (JSON)",
        data=json.dumps(world.to_dict(), indent=2),
        file_name=f"arkworld-seed-{world.seed}-tick-{world.tick}.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()
st.caption(
    "Prototype boundary: agents use transparent deterministic rules; state lives "
    "in this Streamlit session unless exported. No real robot movement, model "
    "consciousness, or extinction-risk reduction is claimed."
)
