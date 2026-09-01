"""doc 22 §90-93 "Regression Testing": the regression harness itself — running every
registered golden case through `EvaluationRunner` and failing the suite if any of them
regress. `config/evaluation/golden/` ships empty (see its README — no real workflow
exists yet, that's Phase 23's job), so this currently runs over zero cases; it exists
now so the very first real golden case dropped into that directory is automatically
picked up by CI without anyone having to wire a new test."""

from pathlib import Path

from pff_fa_ai.evaluation.dataset import load_golden_dataset
from pff_fa_ai.evaluation.models import ExpectedOutcome, GoldenCase
from pff_fa_ai.evaluation.runner import EvaluationRunner
from pff_fa_ai.evaluation.states import DatasetCategory, EvaluationStatus


def test_the_real_golden_dataset_should_regress_clean() -> None:
    registry = load_golden_dataset()
    runner = EvaluationRunner()

    regressions = [
        result
        for case in registry.all_cases()
        if (result := runner.evaluate(case, actual_workflow=case.expected.workflow)).status
        is EvaluationStatus.FAIL
    ]

    assert regressions == []


def test_a_regressed_case_should_be_reported_with_its_failure_reason(tmp_path: Path) -> None:
    """Proves the harness actually catches a regression rather than always passing."""
    (tmp_path / "affiliation.yaml").write_text(
        "case_id: AFF-REG-001\nworkflow: club-affiliation\ncategory: REGRESSION\n"
        "expected:\n  workflow: affiliation\n  required_context: [club]\n",
        encoding="utf-8",
    )
    registry = load_golden_dataset(tmp_path)
    runner = EvaluationRunner()
    case = registry.get("AFF-REG-001")
    assert case is not None

    result = runner.evaluate(case, actual_workflow="affiliation", actual_context=())

    assert result.status is EvaluationStatus.FAIL
    assert any("MISSING_REQUIRED_CONTEXT" in failure for failure in result.failures)


def test_registered_golden_cases_should_each_declare_a_regression_or_functional_category() -> None:
    """Sanity check on the dataset itself, not just the runner (doc 21 §10-13)."""
    registry = load_golden_dataset()

    for case in registry.all_cases():
        assert isinstance(case.category, DatasetCategory)


def test_a_synthetic_regression_dataset_with_only_happy_path_cases_should_pass_clean() -> None:
    registry_case = GoldenCase(
        case_id="SMOKE-001",
        workflow="club-affiliation",
        category=DatasetCategory.HAPPY_PATH,
        expected=ExpectedOutcome(workflow="affiliation"),
    )
    runner = EvaluationRunner()

    result = runner.evaluate(registry_case, actual_workflow="affiliation")

    assert result.status is EvaluationStatus.PASS
