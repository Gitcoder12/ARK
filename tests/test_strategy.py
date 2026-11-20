from ark.strategy import AgentGroup, Decision, PremortemEngine, Severity, historical_scenarios


def test_historical_scenarios_include_beas_gedrosia_and_continuity():
    scenarios = historical_scenarios()
    assert {"beas", "gedrosia", "succession", "engineering"} <= set(scenarios)
    assert scenarios["gedrosia"].risk_level is Severity.CRITICAL


def test_premortem_flags_missing_logistics_and_contingencies():
    plan = historical_scenarios()["gedrosia"]
    result = PremortemEngine().analyse(plan)
    assert result.plan_name == plan.name
    assert result.findings == ()
    assert result.recommended_decision is Decision.PROCEED


def test_premortem_detects_missing_plan_controls():
    from ark.strategy.core import StrategicPlan

    plan = StrategicPlan(name="thin", objective="do thing", steps=())
    result = PremortemEngine().analyse(plan)
    codes = {finding.code for finding in result.findings}
    assert "RESOURCE_BUDGET_MISSING" in codes
    assert "NO_CONTINGENCY" in codes
    assert "CONTINUITY_UNASSIGNED" in codes
    assert result.recommended_decision is Decision.REVISE


def test_healthy_five_agent_team_proceeds():
    result = AgentGroup().run(historical_scenarios()["engineering"])
    assert result.decision is Decision.PROCEED
    assert len(result.active_agents) == 5
    assert result.simulated is True


def test_failed_agent_is_replaced_by_role_matched_backup():
    result = AgentGroup().run(
        historical_scenarios()["engineering"], fail_roles=("researcher",)
    )
    assert result.decision is Decision.PROCEED
    assert "backup-researcher" in result.replacements
    assert len(result.active_agents) == 5


def test_invalid_output_is_treated_as_failure():
    result = AgentGroup().run(
        historical_scenarios()["engineering"], invalid_roles=("critic",)
    )
    assert "backup-critic" in result.replacements
    assert result.decision is Decision.PROCEED


def test_no_backup_for_executor_pauses_and_generates_report():
    result = AgentGroup().run(
        historical_scenarios()["engineering"],
        fail_roles=("executor",),
        fail_backup_roles=("executor",),
    )
    assert result.decision is Decision.PAUSE_REVIEW
    assert result.external_review_report is not None
    assert "External Review Report" in result.external_review_report


def test_zero_agents_stops_and_generates_report():
    result = AgentGroup().run(
        historical_scenarios()["engineering"],
        fail_roles=("coordinator", "researcher", "executor", "critic", "validator"),
        fail_backup_roles=("coordinator", "researcher", "executor", "critic", "validator"),
    )
    assert result.decision is Decision.STOP_REVIEW
    assert result.active_agents == ()
    assert result.external_review_report is not None


def test_high_risk_team_cannot_continue_without_critic_or_validator():
    result = AgentGroup().run(
        historical_scenarios()["gedrosia"],
        fail_roles=("critic",),
        fail_backup_roles=("critic",),
    )
    assert result.decision is Decision.PAUSE_REVIEW
    assert "critic" in result.uncovered_roles


def test_backup_replacement_is_recorded_as_checkpoint_requiring():
    result = AgentGroup().run(
        historical_scenarios()["engineering"], fail_roles=("executor",)
    )
    event = next(event for event in result.events if event.event == "backup_replaced")
    assert "checkpoint-verified" in event.detail
