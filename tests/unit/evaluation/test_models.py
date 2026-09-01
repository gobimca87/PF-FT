import pytest
from pydantic import ValidationError

from pff_fa_ai.evaluation.models import EvaluationResult, ExpectedOutcome, GoldenCase
from pff_fa_ai.evaluation.states import DatasetCategory, EvaluationStatus


def test_golden_case_should_default_version_and_optional_collections() -> None:
    case = GoldenCase(
        case_id="AFF-001",
        workflow="club-affiliation",
        category=DatasetCategory.HAPPY_PATH,
        expected=ExpectedOutcome(workflow="affiliation"),
    )

    assert case.version == "1.0.0"
    assert case.input == {}
    assert case.expected.required_context == ()


def test_golden_case_should_be_frozen() -> None:
    case = GoldenCase(
        case_id="AFF-001",
        workflow="club-affiliation",
        category=DatasetCategory.HAPPY_PATH,
        expected=ExpectedOutcome(workflow="affiliation"),
    )

    with pytest.raises(ValidationError):
        case.case_id = "AFF-002"  # type: ignore[misc]


def test_golden_case_should_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        GoldenCase(
            case_id="AFF-001",
            workflow="club-affiliation",
            category=DatasetCategory.HAPPY_PATH,
            expected=ExpectedOutcome(workflow="affiliation"),
            unexpected_field="nope",  # type: ignore[call-arg]
        )


def test_evaluation_result_should_reject_score_out_of_range() -> None:
    with pytest.raises(ValidationError):
        EvaluationResult(
            evaluation_id="eval-1",
            case_id="AFF-001",
            status=EvaluationStatus.PASS,
            score=1.5,
        )


def test_evaluation_result_should_default_optional_versions_to_none() -> None:
    result = EvaluationResult(
        evaluation_id="eval-1",
        case_id="AFF-001",
        status=EvaluationStatus.PASS,
        score=1.0,
    )

    assert result.model_version is None
    assert result.prompt_version is None
    assert result.agent_version is None
    assert result.guardrail_version is None
    assert result.failures == ()
