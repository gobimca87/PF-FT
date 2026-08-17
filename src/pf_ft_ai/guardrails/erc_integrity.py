from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pf_ft_ai.context.collection.aggregator import AggregationResult
from pf_ft_ai.guardrails.models import GuardrailResult
from pf_ft_ai.guardrails.states import GuardrailDecision, GuardrailSeverity

_GUARDRAIL_ID = "erc-batch-integrity"
_GUARDRAIL_VERSION = "1.0.0"


def validate_erc_batch_integrity(
    result: AggregationResult[Any],
    *,
    organization_ids: Iterable[str],
    expected_organization_id: str,
) -> GuardrailResult:
    """doc 18 §78-79 — validates the final aggregated ERC context before it reaches the
    model: no cross-club contamination, no missing entities, duplicates surfaced. Wires
    Phase 5's `aggregate_records()`/`AggregationResult` (doc 8 §55-58) into an actual
    enforced guardrail decision, per DEVELOPMENT-GUIDE Phase 11."""
    if any(organization_id != expected_organization_id for organization_id in organization_ids):
        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            guardrail_id=_GUARDRAIL_ID,
            guardrail_version=_GUARDRAIL_VERSION,
            reason_codes=("GR-ERC-CROSS-ORG",),
            severity=GuardrailSeverity.CRITICAL,
        )
    if not result.is_complete:
        return GuardrailResult(
            decision=GuardrailDecision.BLOCK,
            guardrail_id=_GUARDRAIL_ID,
            guardrail_version=_GUARDRAIL_VERSION,
            reason_codes=("GR-ERC-INCOMPLETE",),
            severity=GuardrailSeverity.HIGH,
        )
    if result.duplicate_count > 0:
        return GuardrailResult(
            decision=GuardrailDecision.WARN,
            guardrail_id=_GUARDRAIL_ID,
            guardrail_version=_GUARDRAIL_VERSION,
            reason_codes=("GR-ERC-DUPLICATE",),
            severity=GuardrailSeverity.LOW,
        )
    return GuardrailResult(
        decision=GuardrailDecision.ALLOW,
        guardrail_id=_GUARDRAIL_ID,
        guardrail_version=_GUARDRAIL_VERSION,
        severity=GuardrailSeverity.INFO,
    )
