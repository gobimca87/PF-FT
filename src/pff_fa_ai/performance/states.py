from __future__ import annotations

from enum import StrEnum


class LoadTestProfile(StrEnum):
    """doc 26 §125."""

    BASELINE = "BASELINE"
    LOAD = "LOAD"
    STRESS = "STRESS"
    SPIKE = "SPIKE"
    SOAK = "SOAK"
    RESILIENCE = "RESILIENCE"
    CAPACITY = "CAPACITY"


class CostOptimizationCategory(StrEnum):
    """doc 26 §142 — the mandatory optimization order. Deliberately has no
    "degrade model quality" member: §142's own text is "never start by degrading
    model quality", so that path is structurally absent rather than merely
    discouraged — nothing can log a cost change with that category because it
    doesn't exist in this enum."""

    REMOVE_UNNECESSARY_WORK = "REMOVE_UNNECESSARY_WORK"
    REDUCE_DUPLICATE_CALLS = "REDUCE_DUPLICATE_CALLS"
    OPTIMIZE_CONTEXT = "OPTIMIZE_CONTEXT"
    CACHE_SAFELY = "CACHE_SAFELY"
    PARALLELIZE_WHERE_VALID = "PARALLELIZE_WHERE_VALID"
    ROUTE_TO_APPROPRIATE_MODELS = "ROUTE_TO_APPROPRIATE_MODELS"
    OPTIMIZE_INFRASTRUCTURE = "OPTIMIZE_INFRASTRUCTURE"
    OPTIMIZE_OBSERVABILITY_RETENTION = "OPTIMIZE_OBSERVABILITY_RETENTION"


# doc 26 §142's numbered list order, used to detect a proposed optimization plan that
# reaches for a later-priority step while an earlier, cheaper/safer one hasn't been
# tried yet (see `cost.assert_priority_order_respected`).
COST_OPTIMIZATION_PRIORITY: tuple[CostOptimizationCategory, ...] = (
    CostOptimizationCategory.REMOVE_UNNECESSARY_WORK,
    CostOptimizationCategory.REDUCE_DUPLICATE_CALLS,
    CostOptimizationCategory.OPTIMIZE_CONTEXT,
    CostOptimizationCategory.CACHE_SAFELY,
    CostOptimizationCategory.PARALLELIZE_WHERE_VALID,
    CostOptimizationCategory.ROUTE_TO_APPROPRIATE_MODELS,
    CostOptimizationCategory.OPTIMIZE_INFRASTRUCTURE,
    CostOptimizationCategory.OPTIMIZE_OBSERVABILITY_RETENTION,
)
