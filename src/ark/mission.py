"""Mission and long-range purpose for ARK."""

from __future__ import annotations

from typing import Any

PROJECT_PURPOSE = (
    "Build evidence-led methods to evaluate, constrain, and improve autonomous AI "
    "so increasing capability remains accountable to human goals, rights, and safety."
)
NORTH_STAR = (
    "A world where technology expands shared abundance, basic dignity is not gated "
    "by income, and humanity has more room for science, creativity, and space exploration."
)
ABUNDANCE_ASPIRATION = (
    "Our aspiration is a civilization where money is no longer required to access "
    "the essentials of a dignified life. As clean energy, automation, robotics, "
    "open knowledge, and resilient infrastructure grow, money could lose its role "
    "as the gatekeeper to basic opportunity. That is a long-range social goal, not "
    "a forecast or something software can deliver by itself."
)
MISSION_PILLARS = (
    (
        "Build AI that remains accountable",
        "Test goal drift, reward hacking, instruction conflict, memory corruption, "
        "and failures under pressure instead of trusting capability claims.",
    ),
    (
        "Keep people in control",
        "Develop inspectable behavior, bounded permissions, meaningful oversight, "
        "correction, and reliable shutdown paths.",
    ),
    (
        "Turn capability into shared benefit",
        "Support open research and tools that help more people learn, create, solve "
        "problems, and participate in technological progress.",
    ),
    (
        "Protect the foundations of abundance",
        "Treat safety, fairness, privacy, ecological limits, and accountable "
        "governance as engineering requirements—not afterthoughts.",
    ),
    (
        "Make room for the frontier",
        "Help build the trustworthy systems and productive capacity needed for "
        "science, planetary resilience, robotics, and responsible space exploration.",
    ),
)


def render_why_we_build(st: Any) -> None:
    """Render ARK's mission page inside a Streamlit page or tab."""
    st.title("Why We Build ARK")
    st.subheader("Capability should increase human freedom—not reduce it.")
    st.write(PROJECT_PURPOSE)
    st.info(NORTH_STAR)

    st.header("The problem we are working on")
    st.write(
        "AI systems are becoming more capable, but capability alone does not tell us "
        "whether a system follows the right goal, respects constraints, admits failure, "
        "or remains correctable. ARK exists to make those questions measurable through "
        "controlled experiments and inspectable evidence."
    )

    st.header("Our mission pillars")
    for title, description in MISSION_PILLARS:
        with st.container(border=True):
            st.subheader(title)
            st.write(description)

    st.header("The abundance horizon")
    st.write(ABUNDANCE_ASPIRATION)
    st.write(
        "This transition also needs fair institutions, broad access, public "
        "accountability, ecological stewardship, and a just path for people whose "
        "livelihoods change. More automation alone does not guarantee abundance."
    )

    st.header("What ARK does—and does not claim")
    st.write(
        "**ARK contributes:** repeatable evaluations, adversarial stress conditions, "
        "runtime monitoring research, evidence records, and tests of correction and "
        "shutdown behavior."
    )
    st.write(
        "**ARK does not claim:** that a finite benchmark proves general alignment, "
        "that a model is safe in every environment, or that technology alone can "
        "solve economic and political questions."
    )

    st.header("How RepoForge fits")
    st.write(
        "ARK asks whether powerful systems behave reliably and remain accountable. "
        "RepoForge helps people build and maintain useful software with less repetitive "
        "engineering friction. Together, they aim to make trustworthy capability easier "
        "to create and more broadly accessible."
    )
    st.caption(
        "North star: safety before scale · shared benefit before extraction · "
        "human agency before automation · stewardship before waste."
    )
