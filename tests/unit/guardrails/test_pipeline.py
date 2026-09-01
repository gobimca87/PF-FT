import pytest

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.pipeline import GuardrailPipeline
from pff_fa_ai.guardrails.states import GuardrailBoundary, GuardrailDecision, GuardrailSeverity


class _StaticPolicy:
    def __init__(self, decision: GuardrailDecision, *, guardrail_id: str = "static") -> None:
        self._decision = decision
        self.guardrail_id = guardrail_id
        self.guardrail_version = "1.0.0"
        self.calls = 0

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        self.calls += 1
        return GuardrailResult(
            decision=self._decision,
            guardrail_id=self.guardrail_id,
            guardrail_version=self.guardrail_version,
            severity=GuardrailSeverity.INFO,
        )


class _RaisingPolicy:
    guardrail_id = "raising"
    guardrail_version = "1.0.0"

    async def evaluate(self, context: GuardrailContext) -> GuardrailResult:
        raise RuntimeError("classifier unavailable")


def _context(boundary: GuardrailBoundary) -> GuardrailContext:
    return GuardrailContext(boundary=boundary)


async def test_should_allow_when_no_policies_are_registered_for_a_boundary() -> None:
    pipeline = GuardrailPipeline()

    result = await pipeline.evaluate(GuardrailBoundary.INPUT, _context(GuardrailBoundary.INPUT))

    assert result.decision is GuardrailDecision.ALLOW


async def test_should_run_all_registered_policies_for_a_boundary() -> None:
    pipeline = GuardrailPipeline()
    first = _StaticPolicy(GuardrailDecision.ALLOW, guardrail_id="first")
    second = _StaticPolicy(GuardrailDecision.ALLOW, guardrail_id="second")
    pipeline.register(GuardrailBoundary.INPUT, first)
    pipeline.register(GuardrailBoundary.INPUT, second)

    await pipeline.evaluate(GuardrailBoundary.INPUT, _context(GuardrailBoundary.INPUT))

    assert first.calls == 1
    assert second.calls == 1


async def test_should_short_circuit_on_the_first_blocking_result() -> None:
    pipeline = GuardrailPipeline()
    blocking = _StaticPolicy(GuardrailDecision.BLOCK, guardrail_id="blocking")
    never_called = _StaticPolicy(GuardrailDecision.ALLOW, guardrail_id="never-called")
    pipeline.register(GuardrailBoundary.INPUT, blocking)
    pipeline.register(GuardrailBoundary.INPUT, never_called)

    result = await pipeline.evaluate(GuardrailBoundary.INPUT, _context(GuardrailBoundary.INPUT))

    assert result.decision is GuardrailDecision.BLOCK
    assert never_called.calls == 0


async def test_should_return_the_worst_non_blocking_decision() -> None:
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.OUTPUT, _StaticPolicy(GuardrailDecision.ALLOW))
    pipeline.register(GuardrailBoundary.OUTPUT, _StaticPolicy(GuardrailDecision.WARN))

    result = await pipeline.evaluate(GuardrailBoundary.OUTPUT, _context(GuardrailBoundary.OUTPUT))

    assert result.decision is GuardrailDecision.WARN


async def test_should_fail_closed_when_a_policy_raises_on_a_mandatory_boundary() -> None:
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.AUTHORIZATION_CONTEXT, _RaisingPolicy())

    result = await pipeline.evaluate(
        GuardrailBoundary.AUTHORIZATION_CONTEXT, _context(GuardrailBoundary.AUTHORIZATION_CONTEXT)
    )

    assert result.decision is GuardrailDecision.BLOCK
    assert result.severity is GuardrailSeverity.CRITICAL


async def test_should_fail_closed_by_default_on_a_non_mandatory_boundary_too() -> None:
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.INPUT, _RaisingPolicy())

    result = await pipeline.evaluate(GuardrailBoundary.INPUT, _context(GuardrailBoundary.INPUT))

    assert result.decision is GuardrailDecision.BLOCK


async def test_should_fail_open_only_when_explicitly_opted_in() -> None:
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.INPUT, _RaisingPolicy())
    pipeline.allow_fail_open(GuardrailBoundary.INPUT)

    result = await pipeline.evaluate(GuardrailBoundary.INPUT, _context(GuardrailBoundary.INPUT))

    assert result.decision is GuardrailDecision.WARN


async def test_should_reject_opting_a_mandatory_boundary_into_fail_open() -> None:
    pipeline = GuardrailPipeline()

    with pytest.raises(ConfigurationError, match="must always fail closed"):
        pipeline.allow_fail_open(GuardrailBoundary.TOOL)


async def test_mandatory_boundaries_should_still_fail_closed_even_after_a_rejected_opt_in() -> None:
    pipeline = GuardrailPipeline()
    pipeline.register(GuardrailBoundary.MODEL, _RaisingPolicy())
    with pytest.raises(ConfigurationError):
        pipeline.allow_fail_open(GuardrailBoundary.MODEL)

    result = await pipeline.evaluate(GuardrailBoundary.MODEL, _context(GuardrailBoundary.MODEL))

    assert result.decision is GuardrailDecision.BLOCK
