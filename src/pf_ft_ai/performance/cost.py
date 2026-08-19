from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

from pf_ft_ai.common.exceptions import GuardrailError
from pf_ft_ai.performance.states import (
    COST_OPTIMIZATION_PRIORITY,
    CostOptimizationCategory,
)
from pf_ft_ai.slm.models import SlmUsage


class TokenPricing(BaseModel):
    """doc 26 §80/§138: pricing is versioned configuration, never hard-coded into
    application logic. Rates are per 1,000 tokens, matching how providers publish
    pricing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    input_cost_per_1k: float = Field(ge=0)
    output_cost_per_1k: float = Field(ge=0)


def estimate_token_cost(usage: SlmUsage, pricing: TokenPricing) -> float:
    """doc 26 §80."""
    return (usage.prompt_tokens / 1000 * pricing.input_cost_per_1k) + (
        usage.completion_tokens / 1000 * pricing.output_cost_per_1k
    )


class WorkflowCostSummary(BaseModel):
    """doc 26 §77/§146 — cost/workflow is more meaningful than cost/request for
    agentic workloads that span multiple model, tool and API calls."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    token_cost: float = Field(ge=0)
    model_call_count: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    api_call_count: int = Field(ge=0)

    @property
    def total_calls(self) -> int:
        return self.model_call_count + self.tool_call_count + self.api_call_count


class CostOptimizationRecord(BaseModel):
    """doc 26 §143 — every optimization must document these six things; the category
    itself can only be one of `CostOptimizationCategory`'s eight approved steps."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: CostOptimizationCategory
    change: str
    performance_impact: str
    quality_impact: str
    cost_impact: str
    risk: str
    rollback: str


def assert_priority_order_respected(
    proposed: CostOptimizationCategory, *, already_applied: Sequence[CostOptimizationCategory]
) -> None:
    """doc 26 §142: don't reach for a later-priority step (e.g. model routing) while an
    earlier, cheaper/safer one hasn't been tried yet. `already_applied` is the set of
    categories already logged for this workflow/component; this only blocks *skipping
    ahead*, it doesn't require re-doing an earlier step that's genuinely inapplicable —
    callers that determined an earlier step doesn't apply should log it as such rather
    than omit it, so this check stays meaningful."""
    proposed_rank = COST_OPTIMIZATION_PRIORITY.index(proposed)
    earlier_steps = COST_OPTIMIZATION_PRIORITY[:proposed_rank]
    applied = set(already_applied)
    skipped = [step for step in earlier_steps if step not in applied]
    if skipped:
        raise GuardrailError(
            f"Cannot apply '{proposed.value}' before considering: "
            f"{', '.join(step.value for step in skipped)} (doc 26 §142)",
            details={"proposed": proposed.value, "skipped": [s.value for s in skipped]},
        )
