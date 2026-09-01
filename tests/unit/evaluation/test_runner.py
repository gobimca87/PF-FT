from pff_fa_ai.evaluation.models import ExpectedOutcome, GoldenCase
from pff_fa_ai.evaluation.runner import EvaluationRunner, check_expected_outcome
from pff_fa_ai.evaluation.states import DatasetCategory, EvaluationStatus


def _case() -> GoldenCase:
    return GoldenCase(
        case_id="AFF-001",
        workflow="club-affiliation",
        category=DatasetCategory.HAPPY_PATH,
        expected=ExpectedOutcome(
            workflow="affiliation",
            required_context=("club", "officials"),
            expected_tools=("club-details",),
        ),
    )


def test_check_expected_outcome_should_return_no_failures_when_everything_matches() -> None:
    failures = check_expected_outcome(
        _case(),
        actual_workflow="affiliation",
        actual_context=("club", "officials", "course"),
        actual_tools=("club-details",),
    )

    assert failures == ()


def test_check_expected_outcome_should_flag_workflow_mismatch() -> None:
    failures = check_expected_outcome(
        _case(), actual_workflow="discipline", actual_context=(), actual_tools=()
    )

    assert any(f.startswith("WORKFLOW_MISMATCH") for f in failures)


def test_check_expected_outcome_should_flag_missing_required_context() -> None:
    failures = check_expected_outcome(
        _case(),
        actual_workflow="affiliation",
        actual_context=("club",),
        actual_tools=("club-details",),
    )

    assert any(f.startswith("MISSING_REQUIRED_CONTEXT") for f in failures)


def test_check_expected_outcome_should_flag_missing_expected_tools() -> None:
    failures = check_expected_outcome(
        _case(),
        actual_workflow="affiliation",
        actual_context=("club", "officials"),
        actual_tools=(),
    )

    assert any(f.startswith("MISSING_EXPECTED_TOOLS") for f in failures)


def test_runner_should_produce_a_passing_result_with_stamped_versions() -> None:
    runner = EvaluationRunner(
        model_version="slm-1.0.0",
        prompt_version="prompt-2.0.0",
        agent_version="agent-1.0.0",
        guardrail_version="guardrail-1.0.0",
    )

    result = runner.evaluate(
        _case(),
        actual_workflow="affiliation",
        actual_context=("club", "officials"),
        actual_tools=("club-details",),
    )

    assert result.status is EvaluationStatus.PASS
    assert result.score == 1.0
    assert result.model_version == "slm-1.0.0"
    assert result.prompt_version == "prompt-2.0.0"
    assert result.agent_version == "agent-1.0.0"
    assert result.guardrail_version == "guardrail-1.0.0"
    assert result.case_id == "AFF-001"


def test_runner_should_use_judge_score_when_present_on_a_pass() -> None:
    runner = EvaluationRunner()

    result = runner.evaluate(
        _case(),
        actual_workflow="affiliation",
        actual_context=("club", "officials"),
        actual_tools=("club-details",),
        judge_score=0.87,
    )

    assert result.status is EvaluationStatus.PASS
    assert result.score == 0.87
    assert result.metrics["judge_score"] == 0.87


def test_runner_should_produce_a_failing_result_with_zero_score_regardless_of_judge_score() -> None:
    runner = EvaluationRunner()

    result = runner.evaluate(
        _case(), actual_workflow="discipline", actual_context=(), actual_tools=(), judge_score=0.95
    )

    assert result.status is EvaluationStatus.FAIL
    assert result.score == 0.0
    assert result.failures != ()
