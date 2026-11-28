from ark.integrity import AuditConfig, TaskCase, audit_models


def exact_match(expected):
    return lambda output: 1.0 if output.strip() == expected else 0.0


def test_flags_reproducible_candidate_degradation():
    tasks = [
        TaskCase(f"task-{i}", f"prompt-{i}", exact_match(f"answer-{i}"))
        for i in range(4)
    ]

    def good(prompt):
        return "answer-" + prompt.split("-")[1]

    def poor(_prompt):
        return "incorrect"

    report = audit_models(
        baseline_id="baseline-v1",
        baseline=good,
        candidate_id="candidate-v1",
        candidate=poor,
        tasks=tasks,
    )

    assert report.status == "ANOMALY_FLAGGED"
    assert report.baseline_mean == 1.0
    assert report.candidate_mean == 0.0
    assert "does not" in report.interpretation


def test_does_not_flag_small_difference():
    tasks = [
        TaskCase(f"task-{i}", f"p{i}", lambda _out: 0.9)
        for i in range(3)
    ]
    report = audit_models(
        baseline_id="a",
        baseline=lambda _p: "same",
        candidate_id="b",
        candidate=lambda _p: "same",
        tasks=tasks,
    )
    assert report.status == "NO_THRESHOLD_BREACH"


def test_preserves_errors_and_marks_inconclusive():
    tasks = [
        TaskCase(f"task-{i}", f"p{i}", lambda _out: 1.0)
        for i in range(3)
    ]

    def broken(_prompt):
        raise RuntimeError("offline")

    report = audit_models(
        baseline_id="a",
        baseline=broken,
        candidate_id="b",
        candidate=lambda _p: "ok",
        tasks=tasks,
    )
    assert report.status == "INCONCLUSIVE"
    assert all(item.error for item in report.results if item.model_id == "a")


def test_rejects_duplicate_task_ids():
    tasks = [
        TaskCase("same", "one", lambda _out: 1.0),
        TaskCase("same", "two", lambda _out: 1.0),
        TaskCase("third", "three", lambda _out: 1.0),
    ]
    try:
        audit_models(
            baseline_id="a",
            baseline=lambda _p: "x",
            candidate_id="b",
            candidate=lambda _p: "x",
            tasks=tasks,
        )
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("Expected duplicate task IDs to be rejected")


def test_report_is_json_serializable_and_does_not_store_raw_prompts():
    tasks = [
        TaskCase(f"task-{i}", f"private-prompt-{i}", lambda _out: 1.0)
        for i in range(3)
    ]
    report = audit_models(
        baseline_id="a",
        baseline=lambda _p: "ok",
        candidate_id="b",
        candidate=lambda _p: "ok",
        tasks=tasks,
        config=AuditConfig(),
    )
    encoded = report.to_json()
    assert "private-prompt" not in encoded
    assert "prompt_sha256" in encoded
