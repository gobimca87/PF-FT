from pf_ft_ai.evaluation.states import DatasetCategory, EvaluationStatus


def test_should_define_all_sixteen_documented_dataset_categories() -> None:
    """doc 21 §13 / DEVELOPMENT-GUIDE Phase 16."""
    assert len(DatasetCategory) == 16


def test_should_define_the_six_documented_evaluation_statuses() -> None:
    assert {status.value for status in EvaluationStatus} == {
        "PASS",
        "FAIL",
        "WARNING",
        "SKIPPED",
        "ERROR",
        "NOT_APPLICABLE",
    }
