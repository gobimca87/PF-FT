from __future__ import annotations

from enum import StrEnum


class GuardrailDecision(StrEnum):
    """doc 18 §9, DEVELOPMENT-GUIDE Phase 11."""

    ALLOW = "ALLOW"
    ALLOW_WITH_TRANSFORMATION = "ALLOW_WITH_TRANSFORMATION"
    WARN = "WARN"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"


_BLOCKING_DECISIONS = frozenset({GuardrailDecision.BLOCK, GuardrailDecision.ESCALATE})


def is_blocking(decision: GuardrailDecision) -> bool:
    return decision in _BLOCKING_DECISIONS


class GuardrailSeverity(StrEnum):
    """doc 18 §100."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GuardrailBoundary(StrEnum):
    """doc 18 §97 guardrail chain, DEVELOPMENT-GUIDE Phase 11's fixed middleware order."""

    INPUT = "INPUT"
    INJECTION = "INJECTION"
    AUTHORIZATION_CONTEXT = "AUTHORIZATION_CONTEXT"
    DATA = "DATA"
    PROMPT = "PROMPT"
    TOOL = "TOOL"
    MODEL = "MODEL"
    OUTPUT = "OUTPUT"
    RESPONSE = "RESPONSE"


# doc 18 §145: these boundaries must ALWAYS fail closed — no documented exception may
# opt them into fail-open behavior (unlike every other boundary, which fails closed by
# default per doc 18 §98 but *may* be explicitly opted into fail-open per doc 18 §99).
_MANDATORY_FAIL_CLOSED_BOUNDARIES = frozenset({
    GuardrailBoundary.AUTHORIZATION_CONTEXT,
    GuardrailBoundary.TOOL,
    GuardrailBoundary.MODEL,
    GuardrailBoundary.DATA,
})


def is_fail_open_eligible(boundary: GuardrailBoundary) -> bool:
    return boundary not in _MANDATORY_FAIL_CLOSED_BOUNDARIES


class TrustClassification(StrEnum):
    """doc 18 §7-8 — assigned by the application, never by the model or the user."""

    SYSTEM_TRUSTED = "SYSTEM_TRUSTED"
    APPLICATION_TRUSTED = "APPLICATION_TRUSTED"
    ENTERPRISE_AUTHORITATIVE = "ENTERPRISE_AUTHORITATIVE"
    CONTROLLED_CONTEXT = "CONTROLLED_CONTEXT"
    UNTRUSTED_USER = "UNTRUSTED_USER"
    UNTRUSTED_EXTERNAL = "UNTRUSTED_EXTERNAL"
    UNKNOWN = "UNKNOWN"
