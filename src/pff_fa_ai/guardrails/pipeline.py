from __future__ import annotations

from collections import defaultdict

from pff_fa_ai.common.exceptions import ConfigurationError
from pff_fa_ai.guardrails.models import GuardrailContext, GuardrailResult
from pff_fa_ai.guardrails.policy import GuardrailPolicy
from pff_fa_ai.guardrails.states import (
    GuardrailBoundary,
    GuardrailDecision,
    GuardrailSeverity,
    is_blocking,
    is_fail_open_eligible,
)

_PIPELINE_GUARDRAIL_ID = "guardrail-pipeline"
_PIPELINE_GUARDRAIL_VERSION = "1.0.0"

# doc 18 §9 — used only to pick the "worst" non-blocking result among several ALLOW/WARN
# results from parallel-eligible policies (doc 18 §159); BLOCK/ESCALATE always short-circuit.
_DECISION_RANK: dict[GuardrailDecision, int] = {
    GuardrailDecision.ALLOW: 0,
    GuardrailDecision.ALLOW_WITH_TRANSFORMATION: 1,
    GuardrailDecision.RETRY: 2,
    GuardrailDecision.FALLBACK: 3,
    GuardrailDecision.WARN: 4,
    GuardrailDecision.BLOCK: 5,
    GuardrailDecision.ESCALATE: 5,
}


class GuardrailPipeline:
    """doc 18 §95/§97: the fixed boundary chain (DEVELOPMENT-GUIDE Phase 11) — Input →
    Injection → Authorization Context → Data → Prompt → Tool → Model → Output → Response.

    Fail-closed by default (doc 18 §98): if a registered policy raises instead of
    returning a `GuardrailResult`, the boundary BLOCKs unless it was explicitly opted
    into fail-open (doc 18 §99) — and doc 18 §145's mandatory-fail-closed boundaries can
    never be opted in at all.
    """

    def __init__(self) -> None:
        self._policies: dict[GuardrailBoundary, list[GuardrailPolicy]] = defaultdict(list)
        self._fail_open_boundaries: set[GuardrailBoundary] = set()

    def register(self, boundary: GuardrailBoundary, policy: GuardrailPolicy) -> None:
        self._policies[boundary].append(policy)

    def allow_fail_open(self, boundary: GuardrailBoundary) -> None:
        """Only call this for an explicitly approved, documented low-risk boundary."""
        if not is_fail_open_eligible(boundary):
            raise ConfigurationError(
                f"Boundary '{boundary}' must always fail closed (doc 18 §145) and cannot "
                "be opted into fail-open behavior"
            )
        self._fail_open_boundaries.add(boundary)

    async def evaluate(
        self, boundary: GuardrailBoundary, context: GuardrailContext
    ) -> GuardrailResult:
        worst: GuardrailResult | None = None
        for policy in self._policies.get(boundary, ()):
            try:
                result = await policy.evaluate(context)
            except Exception:
                result = self._policy_failure_result(boundary)
            if is_blocking(result.decision):
                return result
            if worst is None or _DECISION_RANK[result.decision] > _DECISION_RANK[worst.decision]:
                worst = result
        return worst or GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            guardrail_id=_PIPELINE_GUARDRAIL_ID,
            guardrail_version=_PIPELINE_GUARDRAIL_VERSION,
            severity=GuardrailSeverity.INFO,
        )

    def _policy_failure_result(self, boundary: GuardrailBoundary) -> GuardrailResult:
        if boundary in self._fail_open_boundaries:
            return GuardrailResult(
                decision=GuardrailDecision.WARN,
                guardrail_id=_PIPELINE_GUARDRAIL_ID,
                guardrail_version=_PIPELINE_GUARDRAIL_VERSION,
                reason_codes=("GR-CONFIG-001",),
                severity=GuardrailSeverity.MEDIUM,
            )
        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            guardrail_id=_PIPELINE_GUARDRAIL_ID,
            guardrail_version=_PIPELINE_GUARDRAIL_VERSION,
            reason_codes=("GR-CONFIG-001",),
            severity=GuardrailSeverity.CRITICAL,
        )
