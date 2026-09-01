from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.common.exceptions import WorkflowError


class Versioned(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: int = Field(ge=1, default=1)


def assert_expected_version(*, current_version: int, expected_version: int) -> None:
    if current_version != expected_version:
        raise WorkflowError(
            f"Concurrency conflict: expected version {expected_version}, found {current_version}",
            details={"current_version": current_version, "expected_version": expected_version},
        )
