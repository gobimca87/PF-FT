from pff_fa_ai.performance.states import (
    COST_OPTIMIZATION_PRIORITY,
    CostOptimizationCategory,
    LoadTestProfile,
)


def test_should_define_the_seven_documented_load_test_profiles() -> None:
    assert len(LoadTestProfile) == 7


def test_cost_optimization_priority_should_cover_every_category_exactly_once() -> None:
    assert set(COST_OPTIMIZATION_PRIORITY) == set(CostOptimizationCategory)
    assert len(COST_OPTIMIZATION_PRIORITY) == len(set(COST_OPTIMIZATION_PRIORITY))


def test_cost_optimization_priority_should_start_with_removing_unnecessary_work() -> None:
    """doc 26 §142's numbered list starts here — never with a model-quality change."""
    assert COST_OPTIMIZATION_PRIORITY[0] is CostOptimizationCategory.REMOVE_UNNECESSARY_WORK


def test_cost_optimization_category_should_have_no_model_quality_degradation_option() -> None:
    """doc 26 §142: "never start by degrading model quality" — structurally enforced
    by the category simply not existing."""
    values = {category.value for category in CostOptimizationCategory}
    assert not any("QUALITY" in value or "DEGRADE" in value for value in values)
