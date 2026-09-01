from pff_fa_ai.performance.budget import (
    PerformanceBudget,
    WorkflowActuals,
    check_performance_budget,
)


def _budget(**overrides: object) -> PerformanceBudget:
    defaults: dict[str, object] = {
        "latency_budget_ms": {"slm": 5000, "rag": 1500},
        "token_budget": 8000,
        "model_call_budget": 5,
        "tool_call_budget": 10,
        "cost_budget": 1.0,
    }
    defaults.update(overrides)
    return PerformanceBudget.model_validate(defaults)


def _actuals(**overrides: object) -> WorkflowActuals:
    defaults: dict[str, object] = {
        "latency_ms": {"slm": 1000, "rag": 500},
        "tokens_used": 2000,
        "model_calls": 2,
        "tool_calls": 3,
        "cost": 0.1,
    }
    defaults.update(overrides)
    return WorkflowActuals.model_validate(defaults)


def test_should_report_no_violations_when_everything_is_within_budget() -> None:
    violations = check_performance_budget(actuals=_actuals(), budget=_budget())

    assert violations == ()


def test_should_flag_a_specific_stage_latency_overrun() -> None:
    violations = check_performance_budget(
        actuals=_actuals(latency_ms={"slm": 6000, "rag": 500}), budget=_budget()
    )

    assert "LATENCY_BUDGET_EXCEEDED:slm" in violations
    assert "LATENCY_BUDGET_EXCEEDED:rag" not in violations


def test_should_flag_token_budget_overrun() -> None:
    violations = check_performance_budget(actuals=_actuals(tokens_used=9000), budget=_budget())

    assert "TOKEN_BUDGET_EXCEEDED" in violations


def test_should_flag_model_call_budget_overrun() -> None:
    violations = check_performance_budget(actuals=_actuals(model_calls=6), budget=_budget())

    assert "MODEL_CALL_BUDGET_EXCEEDED" in violations


def test_should_flag_tool_call_budget_overrun() -> None:
    violations = check_performance_budget(actuals=_actuals(tool_calls=11), budget=_budget())

    assert "TOOL_CALL_BUDGET_EXCEEDED" in violations


def test_should_flag_cost_budget_overrun() -> None:
    violations = check_performance_budget(actuals=_actuals(cost=1.5), budget=_budget())

    assert "COST_BUDGET_EXCEEDED" in violations


def test_should_ignore_a_stage_not_present_in_actuals() -> None:
    violations = check_performance_budget(
        actuals=_actuals(latency_ms={"slm": 1000}), budget=_budget()
    )

    assert violations == ()


def test_should_report_multiple_violations_simultaneously() -> None:
    violations = check_performance_budget(
        actuals=_actuals(tokens_used=9000, cost=2.0), budget=_budget()
    )

    assert "TOKEN_BUDGET_EXCEEDED" in violations
    assert "COST_BUDGET_EXCEEDED" in violations
