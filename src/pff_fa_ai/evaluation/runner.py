from __future__ import annotations

from collections.abc import Sequence

from pff_fa_ai.common.correlation import new_id
from pff_fa_ai.evaluation.models import EvaluationResult, GoldenCase
from pff_fa_ai.evaluation.states import EvaluationStatus


def check_expected_outcome(
    case: GoldenCase,
    *,
    actual_workflow: str,
    actual_context: Sequence[str],
    actual_tools: Sequence[str],
) -> tuple[str, ...]:
    """doc 21 §64: deterministic assertions are preferred over an AI judge for exact
    requirements. Returns failure reason codes — empty means every check passed."""
    failures: list[str] = []
    if case.expected.workflow != actual_workflow:
        failures.append(
            f"WORKFLOW_MISMATCH: expected={case.expected.workflow} actual={actual_workflow}"
        )
    missing_context = sorted(set(case.expected.required_context) - set(actual_context))
    if missing_context:
        failures.append(f"MISSING_REQUIRED_CONTEXT: {missing_context}")
    missing_tools = sorted(set(case.expected.expected_tools) - set(actual_tools))
    if missing_tools:
        failures.append(f"MISSING_EXPECTED_TOOLS: {missing_tools}")
    return tuple(failures)


class EvaluationRunner:
    """doc 21 §64-65: combines deterministic assertions with an optional judge score
    into the standard `EvaluationResult` (doc 21 §65), stamped with the versions that
    produced it so a result is always reproducible."""

    def __init__(
        self,
        *,
        model_version: str | None = None,
        prompt_version: str | None = None,
        agent_version: str | None = None,
        guardrail_version: str | None = None,
    ) -> None:
        self._model_version = model_version
        self._prompt_version = prompt_version
        self._agent_version = agent_version
        self._guardrail_version = guardrail_version

    def evaluate(
        self,
        case: GoldenCase,
        *,
        actual_workflow: str,
        actual_context: Sequence[str] = (),
        actual_tools: Sequence[str] = (),
        judge_score: float | None = None,
    ) -> EvaluationResult:
        failures = check_expected_outcome(
            case,
            actual_workflow=actual_workflow,
            actual_context=actual_context,
            actual_tools=actual_tools,
        )
        metrics = {"judge_score": judge_score} if judge_score is not None else {}

        if failures:
            status = EvaluationStatus.FAIL
            score = 0.0
        else:
            status = EvaluationStatus.PASS
            score = judge_score if judge_score is not None else 1.0

        return EvaluationResult(
            evaluation_id=new_id("eval"),
            case_id=case.case_id,
            status=status,
            score=score,
            metrics=metrics,
            failures=failures,
            model_version=self._model_version,
            prompt_version=self._prompt_version,
            agent_version=self._agent_version,
            guardrail_version=self._guardrail_version,
        )
