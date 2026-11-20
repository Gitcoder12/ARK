"""Historical and engineering demonstration scenarios."""
from .core import PlanStep, Severity, StrategicPlan


def historical_scenarios() -> dict[str, StrategicPlan]:
    """Illustrative reconstructions, not claims of exact historical staff plans."""
    return {
        "beas": StrategicPlan(
            name="Beas River: advance beyond the known limit",
            objective="Continue the campaign east beyond the Beas River.",
            steps=(
                PlanStep("assess_capacity", "Assess army readiness and willingness."),
                PlanStep("secure_supply", "Verify food, water and route support.", ("assess_capacity",)),
                PlanStep("advance", "Continue east only if conditions remain acceptable.",
                         ("secure_supply",)),
            ),
            resources=("food", "water", "transport", "medical support"),
            constraints=("army refusal", "monsoon conditions", "unknown eastern logistics"),
            stakeholders=("soldiers", "commanders", "local communities"),
            contingencies=("pause and return", "negotiate a revised objective"),
            milestones=("readiness assessment", "supply confirmation", "staged advance"),
            continuity_owner="appointed field commander",
            risk_level=Severity.HIGH,
            context=("Ancient accounts report that the army refused to continue at the Hyphasis/Beas.",
                     "Scenario is a teaching reconstruction, not a definitive historical dataset."),
        ),
        "gedrosia": StrategicPlan(
            name="Gedrosian Desert: return march",
            objective="Move the army through the Gedrosian region toward the imperial centre.",
            steps=(
                PlanStep("choose_route", "Select a route through difficult terrain."),
                PlanStep("stage_supplies", "Stage water, food and transport.", ("choose_route",)),
                PlanStep("march", "Move in bounded stages.", ("stage_supplies",)),
            ),
            resources=("water", "food", "pack animals", "route intelligence", "medical support"),
            constraints=("extreme heat", "water scarcity", "terrain", "limited communications"),
            stakeholders=("soldiers", "supply personnel", "local communities"),
            contingencies=("alternate route", "staged delay", "abort to a safer route"),
            milestones=("water points verified", "daily supply confirmed", "staged arrival"),
            continuity_owner="designated logistics commander",
            risk_level=Severity.CRITICAL,
            context=("Ancient sources describe severe losses during the Gedrosian march.",
                     "Exact casualty totals and motives are disputed; this is not a quantitative reconstruction."),
        ),
        "arabia": StrategicPlan(
            name="Arabian expedition: ambitious uncompleted objective",
            objective="Prepare and evaluate a major expedition into Arabia.",
            steps=(
                PlanStep("reconnaissance", "Validate routes, ports and local conditions."),
                PlanStep("logistics", "Establish supply, fleet and staging capacity.",
                         ("reconnaissance",)),
                PlanStep("go_no_go", "Review readiness before authorizing departure.",
                         ("logistics",)),
            ),
            resources=("ships", "water", "food", "route intelligence", "crew"),
            constraints=("uncertain route conditions", "fleet capacity", "leadership continuity"),
            stakeholders=("crew", "commanders", "regional communities"),
            contingencies=("defer departure", "reduce expedition scope", "return to staging port"),
            milestones=("reconnaissance complete", "supply staged", "readiness review"),
            continuity_owner="appointed expedition commander",
            risk_level=Severity.HIGH,
            context=("Ancient accounts describe preparations for an Arabian expedition before Alexander's death.",
                     "This is an illustrative scenario; it was not an executed campaign."),
        ),
        "succession": StrategicPlan(
            name="Empire continuity after founder unavailability",
            objective="Preserve stable governance if the central leader becomes unavailable.",
            steps=(
                PlanStep("define_authority", "Define lawful decision rights."),
                PlanStep("appoint_successors", "Identify and qualify successors.",
                         ("define_authority",)),
                PlanStep("test_handoff", "Run a controlled handoff exercise.",
                         ("appoint_successors",)),
            ),
            resources=("trusted administrators", "records", "communication channels"),
            constraints=("competing claims", "regional autonomy", "uncertain legitimacy"),
            stakeholders=("regional governors", "military leaders", "civic institutions"),
            contingencies=("council review", "temporary caretaker authority"),
            milestones=("succession charter", "handoff rehearsal", "continuity audit"),
            continuity_owner="independent governing council",
            risk_level=Severity.HIGH,
            context=("The successor struggles after Alexander's death illustrate continuity risks.",
                     "This scenario generalizes the lesson; it is not a claim that a specific plan existed."),
        ),
        "engineering": StrategicPlan(
            name="Repository-wide automated refactor",
            objective="Refactor 40 modules, run tests and prepare a release.",
            steps=(
                PlanStep("inventory", "Map modules and dependencies."),
                PlanStep("refactor", "Apply bounded changes.", ("inventory",)),
                PlanStep("validate", "Run tests and inspect diffs.", ("refactor",)),
                PlanStep("release", "Prepare release after human approval.", ("validate",)),
            ),
            resources=("CI minutes", "developer review time", "backup branch", "test environment"),
            constraints=("protected branches", "no destructive changes without approval"),
            stakeholders=("maintainer", "reviewers", "downstream users"),
            contingencies=("revert patch", "reduce scope", "pause release"),
            milestones=("inventory complete", "small batch validated", "full suite passed"),
            continuity_owner="repository maintainer",
            risk_level=Severity.HIGH,
            context=("Synthetic engineering demonstration scenario.",),
        ),
    }


__all__ = ["historical_scenarios"]
