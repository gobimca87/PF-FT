from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.evaluation.states import DatasetCategory, EvaluationStatus


class ExpectedOutcome(BaseModel):
    """doc 21 §11 golden dataset example's `expected` block."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workflow: str
    required_context: tuple[str, ...] = Field(default_factory=tuple)
    expected_tools: tuple[str, ...] = Field(default_factory=tuple)
    expected_api_calls: tuple[str, ...] = Field(default_factory=tuple)


class GoldenCase(BaseModel):
    """doc 21 §10-11, DEVELOPMENT-GUIDE Phase 16's exact minimum field list."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    case_id: str
    workflow: str
    category: DatasetCategory
    version: str = "1.0.0"
    input: dict[str, Any] = Field(default_factory=dict)
    expected: ExpectedOutcome


class EvaluationResult(BaseModel):
    """doc 21 §65 evaluation result schema."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evaluation_id: str
    case_id: str
    status: EvaluationStatus
    score: float = Field(ge=0, le=1)
    metrics: dict[str, float] = Field(default_factory=dict)
    failures: tuple[str, ...] = Field(default_factory=tuple)
    model_version: str | None = None
    prompt_version: str | None = None
    agent_version: str | None = None
    guardrail_version: str | None = None
