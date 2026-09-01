import pytest

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.performance.cost import (
    CostOptimizationRecord,
    TokenPricing,
    WorkflowCostSummary,
    assert_priority_order_respected,
    estimate_token_cost,
)
from pff_fa_ai.performance.states import CostOptimizationCategory
from pff_fa_ai.slm.models import SlmUsage


def test_estimate_token_cost_should_apply_input_and_output_rates() -> None:
    usage = SlmUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    pricing = TokenPricing(input_cost_per_1k=0.01, output_cost_per_1k=0.02)

    cost = estimate_token_cost(usage, pricing)

    assert cost == pytest.approx(0.01 + 0.01)


def test_estimate_token_cost_should_be_zero_for_mock_pricing() -> None:
    usage = SlmUsage(prompt_tokens=1000, completion_tokens=1000, total_tokens=2000)
    pricing = TokenPricing(input_cost_per_1k=0.0, output_cost_per_1k=0.0)

    assert estimate_token_cost(usage, pricing) == 0.0


def test_workflow_cost_summary_total_calls_should_sum_every_call_kind() -> None:
    summary = WorkflowCostSummary(
        token_cost=1.5, model_call_count=2, tool_call_count=3, api_call_count=4
    )

    assert summary.total_calls == 9


def test_cost_optimization_record_should_require_all_six_documented_fields() -> None:
    record = CostOptimizationRecord(
        category=CostOptimizationCategory.CACHE_SAFELY,
        change="Cache portal catalog metadata for 5 minutes",
        performance_impact="Reduces API latency for repeat catalog lookups",
        quality_impact="None — catalog metadata changes rarely",
        cost_impact="Fewer enterprise API calls",
        risk="Stale metadata for up to 5 minutes",
        rollback="Set TTL to 0",
    )

    assert record.category is CostOptimizationCategory.CACHE_SAFELY


def test_assert_priority_order_respected_should_allow_the_first_step_with_nothing_applied() -> None:
    assert_priority_order_respected(
        CostOptimizationCategory.REMOVE_UNNECESSARY_WORK, already_applied=()
    )


def test_assert_priority_order_respected_should_allow_a_later_step_once_earlier_applied() -> None:
    assert_priority_order_respected(
        CostOptimizationCategory.ROUTE_TO_APPROPRIATE_MODELS,
        already_applied=(
            CostOptimizationCategory.REMOVE_UNNECESSARY_WORK,
            CostOptimizationCategory.REDUCE_DUPLICATE_CALLS,
            CostOptimizationCategory.OPTIMIZE_CONTEXT,
            CostOptimizationCategory.CACHE_SAFELY,
            CostOptimizationCategory.PARALLELIZE_WHERE_VALID,
        ),
    )


def test_assert_priority_order_respected_should_reject_skipping_ahead() -> None:
    with pytest.raises(GuardrailError, match="Cannot apply"):
        assert_priority_order_respected(
            CostOptimizationCategory.ROUTE_TO_APPROPRIATE_MODELS, already_applied=()
        )


def test_assert_priority_order_respected_error_should_name_every_skipped_step() -> None:
    with pytest.raises(GuardrailError) as exc_info:
        assert_priority_order_respected(
            CostOptimizationCategory.CACHE_SAFELY,
            already_applied=(CostOptimizationCategory.REMOVE_UNNECESSARY_WORK,),
        )

    assert "REDUCE_DUPLICATE_CALLS" in str(exc_info.value)
    assert "OPTIMIZE_CONTEXT" in str(exc_info.value)
