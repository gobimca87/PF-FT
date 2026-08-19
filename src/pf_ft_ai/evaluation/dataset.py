from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.common.validation import format_validation_error
from pf_ft_ai.evaluation.models import GoldenCase
from pf_ft_ai.evaluation.states import DatasetCategory

GOLDEN_DATASET_ROOT = Path(__file__).resolve().parents[3] / "config" / "evaluation" / "golden"


class GoldenDatasetRegistry:
    """doc 21 §10/§12 — `case_id` uniqueness enforced at registration; dataset changes
    must be traceable, so silently overwriting a case is never allowed."""

    def __init__(self) -> None:
        self._cases: dict[str, GoldenCase] = {}

    def register(self, case: GoldenCase) -> None:
        if case.case_id in self._cases:
            raise ConfigurationError(f"Duplicate golden case registered: {case.case_id}")
        self._cases[case.case_id] = case

    def get(self, case_id: str) -> GoldenCase | None:
        return self._cases.get(case_id)

    def by_category(self, category: DatasetCategory) -> tuple[GoldenCase, ...]:
        return tuple(case for case in self._cases.values() if case.category is category)

    def all_cases(self) -> tuple[GoldenCase, ...]:
        return tuple(self._cases.values())


def load_golden_dataset(directory: Path | None = None) -> GoldenDatasetRegistry:
    root = directory or GOLDEN_DATASET_ROOT
    registry = GoldenDatasetRegistry()
    if not root.is_dir():
        return registry
    for path in sorted(root.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not raw:
            continue
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            try:
                case = GoldenCase.model_validate(entry)
            except PydanticValidationError as exc:
                raise ConfigurationError(
                    f"Invalid golden case in {path}: {format_validation_error(exc)}"
                ) from exc
            registry.register(case)
    return registry
