from pf_ft_ai.evaluation.models import EvaluationResult, ExpectedOutcome, GoldenCase
from pf_ft_ai.evaluation.states import DatasetCategory, EvaluationStatus, ScoreDimension
from pf_ft_ai.evaluation.thresholds import EvaluationThresholds, evaluate_release_gate


def _case(case_id: str, category: DatasetCategory) -> GoldenCase:
    return GoldenCase(
        case_id=case_id,
        workflow="club-affiliation",
        category=category,
        expected=ExpectedOutcome(workflow="affiliation"),
    )


def _result(case_id: str, status: EvaluationStatus) -> EvaluationResult:
    return EvaluationResult(
        evaluation_id=f"eval-{case_id}", case_id=case_id, status=status, score=0.0
    )


def test_evaluate_release_gate_should_pass_when_all_scores_meet_minimum() -> None:
    thresholds = EvaluationThresholds(minimum_scores={ScoreDimension.QUALITY: 0.8})

    outcome = evaluate_release_gate(
        results=(),
        cases_by_id={},
        dimension_scores={ScoreDimension.QUALITY: 0.9},
        thresholds=thresholds,
    )

    assert outcome.passed is True
    assert outcome.blocking_reasons == ()


def test_evaluate_release_gate_should_block_when_score_below_minimum() -> None:
    thresholds = EvaluationThresholds(minimum_scores={ScoreDimension.QUALITY: 0.8})

    outcome = evaluate_release_gate(
        results=(),
        cases_by_id={},
        dimension_scores={ScoreDimension.QUALITY: 0.5},
        thresholds=thresholds,
    )

    assert outcome.passed is False
    assert "QUALITY_BELOW_MINIMUM" in outcome.blocking_reasons


def test_evaluate_release_gate_should_block_when_dimension_missing_entirely() -> None:
    thresholds = EvaluationThresholds(minimum_scores={ScoreDimension.SAFETY: 0.9})

    outcome = evaluate_release_gate(
        results=(), cases_by_id={}, dimension_scores={}, thresholds=thresholds
    )

    assert "SAFETY_BELOW_MINIMUM" in outcome.blocking_reasons


def test_evaluate_release_gate_should_block_when_security_failures_exceed_allowance() -> None:
    case = _case("SEC-001", DatasetCategory.SECURITY)
    result = _result("SEC-001", EvaluationStatus.FAIL)
    thresholds = EvaluationThresholds(max_critical_security_failures=0)

    outcome = evaluate_release_gate(
        results=(result,),
        cases_by_id={"SEC-001": case},
        dimension_scores={},
        thresholds=thresholds,
    )

    assert outcome.passed is False
    assert "SECURITY_CRITICAL_FAILURES_EXCEEDED" in outcome.blocking_reasons


def test_evaluate_release_gate_should_ignore_non_security_failures() -> None:
    case = _case("HP-001", DatasetCategory.HAPPY_PATH)
    result = _result("HP-001", EvaluationStatus.FAIL)
    thresholds = EvaluationThresholds(max_critical_security_failures=0)

    outcome = evaluate_release_gate(
        results=(result,),
        cases_by_id={"HP-001": case},
        dimension_scores={},
        thresholds=thresholds,
    )

    assert outcome.passed is True


def test_evaluate_release_gate_should_allow_security_failures_within_configured_allowance() -> None:
    case = _case("SEC-001", DatasetCategory.SECURITY)
    result = _result("SEC-001", EvaluationStatus.FAIL)
    thresholds = EvaluationThresholds(max_critical_security_failures=1)

    outcome = evaluate_release_gate(
        results=(result,),
        cases_by_id={"SEC-001": case},
        dimension_scores={},
        thresholds=thresholds,
    )

    assert outcome.passed is True
