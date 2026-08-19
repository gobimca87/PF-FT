from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PerformanceBudget(BaseModel):
    """doc 26 §8/§28/§133 — each critical workflow defines these budgets up front;
    `latency_budget_ms` is per named stage (doc 26 §9: APIM/FastAPI/Supervisor/
    Enterprise APIs/RAG/Tools/ERC/SLM/Output), so one dependency can't silently
    consume the whole workflow's latency allowance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    latency_budget_ms: dict[str, int] = Field(default_factory=dict)
    token_budget: int = Field(gt=0)
    model_call_budget: int = Field(gt=0)
    tool_call_budget: int = Field(gt=0)
    cost_budget: float = Field(gt=0)


class WorkflowActuals(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    latency_ms: dict[str, float] = Field(default_factory=dict)
    tokens_used: int = Field(ge=0)
    model_calls: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    cost: float = Field(ge=0)


def check_performance_budget(
    *, actuals: WorkflowActuals, budget: PerformanceBudget
) -> tuple[str, ...]:
    """doc 26 §133-135 performance/cost gate. Returns violation reason codes — empty
    means every budget held."""
    violations: list[str] = []

    for stage, stage_budget_ms in budget.latency_budget_ms.items():
        actual_ms = actuals.latency_ms.get(stage)
        if actual_ms is not None and actual_ms > stage_budget_ms:
            violations.append(f"LATENCY_BUDGET_EXCEEDED:{stage}")

    if actuals.tokens_used > budget.token_budget:
        violations.append("TOKEN_BUDGET_EXCEEDED")
    if actuals.model_calls > budget.model_call_budget:
        violations.append("MODEL_CALL_BUDGET_EXCEEDED")
    if actuals.tool_calls > budget.tool_call_budget:
        violations.append("TOOL_CALL_BUDGET_EXCEEDED")
    if actuals.cost > budget.cost_budget:
        violations.append("COST_BUDGET_EXCEEDED")

    return tuple(violations)
