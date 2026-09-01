from pathlib import Path

import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.evaluation.dataset import GoldenDatasetRegistry, load_golden_dataset
from pff_fa_ai.evaluation.models import ExpectedOutcome, GoldenCase
from pff_fa_ai.evaluation.states import DatasetCategory


def _case(
    case_id: str = "AFF-001", category: DatasetCategory = DatasetCategory.HAPPY_PATH
) -> GoldenCase:
    return GoldenCase(
        case_id=case_id,
        workflow="club-affiliation",
        category=category,
        input={"query": "Start affiliation for club ABC"},
        expected=ExpectedOutcome(
            workflow="affiliation",
            required_context=("club", "officials", "course"),
            expected_tools=("club-details", "official-details", "course-details"),
        ),
    )


def test_should_register_and_fetch_a_case() -> None:
    registry = GoldenDatasetRegistry()
    registry.register(_case())

    fetched = registry.get("AFF-001")

    assert fetched is not None
    assert fetched.workflow == "club-affiliation"


def test_should_reject_a_duplicate_case_id() -> None:
    registry = GoldenDatasetRegistry()
    registry.register(_case())

    with pytest.raises(ConfigurationError, match="Duplicate golden case"):
        registry.register(_case())


def test_should_filter_by_category() -> None:
    registry = GoldenDatasetRegistry()
    registry.register(_case("AFF-001", DatasetCategory.HAPPY_PATH))
    registry.register(_case("AFF-002", DatasetCategory.SECURITY))

    happy_path_cases = registry.by_category(DatasetCategory.HAPPY_PATH)

    assert len(happy_path_cases) == 1
    assert happy_path_cases[0].case_id == "AFF-001"


def test_load_golden_dataset_should_return_empty_registry_for_missing_directory(
    tmp_path: Path,
) -> None:
    registry = load_golden_dataset(tmp_path / "does-not-exist")

    assert registry.all_cases() == ()


def test_load_golden_dataset_should_load_a_yaml_file(tmp_path: Path) -> None:
    (tmp_path / "affiliation.yaml").write_text(
        "case_id: AFF-001\nworkflow: club-affiliation\ncategory: HAPPY_PATH\n"
        "input:\n  query: test\nexpected:\n  workflow: affiliation\n",
        encoding="utf-8",
    )

    registry = load_golden_dataset(tmp_path)

    assert len(registry.all_cases()) == 1
    assert registry.get("AFF-001") is not None


def test_load_golden_dataset_should_load_a_list_of_cases_from_one_file(tmp_path: Path) -> None:
    (tmp_path / "affiliation.yaml").write_text(
        "- case_id: AFF-001\n  workflow: club-affiliation\n  category: HAPPY_PATH\n"
        "  expected:\n    workflow: affiliation\n"
        "- case_id: AFF-002\n  workflow: club-affiliation\n  category: SECURITY\n"
        "  expected:\n    workflow: affiliation\n",
        encoding="utf-8",
    )

    registry = load_golden_dataset(tmp_path)

    assert len(registry.all_cases()) == 2


def test_load_golden_dataset_should_skip_an_empty_yaml_file(tmp_path: Path) -> None:
    (tmp_path / "empty.yaml").write_text("", encoding="utf-8")

    registry = load_golden_dataset(tmp_path)

    assert registry.all_cases() == ()


def test_load_golden_dataset_should_raise_a_sanitized_error_for_invalid_content(
    tmp_path: Path,
) -> None:
    (tmp_path / "broken.yaml").write_text("case_id: broken\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Invalid golden case"):
        load_golden_dataset(tmp_path)


def test_the_real_golden_dataset_directory_should_currently_be_empty() -> None:
    """config/evaluation/golden/README.md explains why: no real workflow exists yet."""
    registry = load_golden_dataset()

    assert registry.all_cases() == ()
