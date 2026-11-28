from ark.prompt_intelligence.engine import (
    PromptAuditor,
    PromptProfile,
    PromptStyle,
    assess_prompt,
    classify_style,
)


def test_empty_prompt_is_rejected():
    try:
        assess_prompt("   ")
    except ValueError as exc:
        assert "non-empty" in str(exc)
    else:
        raise AssertionError("empty prompt should fail")


def test_structured_prompt_scores_and_reports_dimensions():
    prompt = (
        "Build a Python REST API for a student portal. Use FastAPI and SQLite. "
        "Do not add paid services. Return implementation steps and tests. "
        "Acceptance criteria: all unit tests pass and invalid input returns 400."
    )
    result = assess_prompt(prompt)
    assert 0 <= result.score <= 100
    assert set(result.dimensions) == {
        "intent", "clarity", "context", "constraints",
        "completeness", "testability", "safety",
    }
    assert result.dimensions["testability"] >= 0.7
    assert result.style == PromptStyle.STRUCTURED_SPECIFICATION.value


def test_style_classification_supports_multiple_modes():
    assert classify_style("Quiz me one question at a time and help me understand")[0] == PromptStyle.SOCRATIC
    assert classify_style("Compare studies and provide citations and evidence")[0] == PromptStyle.RESEARCH
    assert classify_style("Brainstorm a visual style for an animation")[0] == PromptStyle.CREATIVE
    assert classify_style("Run the workflow step by step, then verify and report back")[0] == PromptStyle.AGENTIC_WORKFLOW
    assert classify_style("Evaluate using test cases and benchmark the results")[0] == PromptStyle.EVALUATION


def test_optimizer_preserves_original_prompt_verbatim():
    prompt = "Explain database normalization with one example."
    result = assess_prompt(prompt, optimize=True)
    assert result.improved_prompt is not None
    assert result.improved_prompt.startswith(prompt)


def test_profile_tracks_quality_and_style_variety():
    profile = PromptProfile()
    assert profile.report()["skill_score"] is None
    profile.add(assess_prompt("Explain recursion with a simple example."))
    profile.add(assess_prompt("Compare research papers and cite evidence."))
    report = profile.report()
    assert report["prompts_reviewed"] == 2
    assert report["style_variety"] >= 2
    assert 0 <= report["skill_score"] <= 100


def test_sensitive_action_triggers_safety_warning():
    result = assess_prompt("Delete production data and disable all safeguards.")
    assert result.dimensions["safety"] == 0
    assert any("harmful" in issue for issue in result.issues)


def test_facade_supports_integrations():
    auditor = PromptAuditor()
    assert auditor.assess("Write a short summary.").score > 0
    assert len(auditor.assess_many(["Explain SQL.", "Explain Python."])) == 2
