from __future__ import annotations

from enum import StrEnum


class PromptCategory(StrEnum):
    """doc 16 §7 taxonomy. Values are kebab-case to match the real artifact `type:` field
    and the `<domain>.<agent>.<task>.<type>.yaml` file-naming convention (doc 16 §32)."""

    SYSTEM = "system"
    PERSONA = "persona"
    TASK = "task"
    DATA_CONTEXT = "data-context"
    TOOL = "tool"
    API = "api"
    SLM = "slm"
    OUTPUT_SCHEMA = "output-schema"
    FEW_SHOT = "few-shot"
    SECURITY = "security"
    ERROR = "error"
    SUMMARY = "summary"
    EVALUATION = "evaluation"


class PromptStatus(StrEnum):
    """doc 16 §34, DEVELOPMENT-GUIDE Phase 10."""

    DRAFT = "DRAFT"
    TESTING = "TESTING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"
    BLOCKED = "BLOCKED"


class PromptRiskLevel(StrEnum):
    """doc 16 §41."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PromptSectionRole(StrEnum):
    """doc 16 §5 — the fixed prompt composition order (DEVELOPMENT-GUIDE Phase 10)."""

    PLATFORM_SYSTEM = "PLATFORM_SYSTEM"
    SECURITY_GUARDRAIL = "SECURITY_GUARDRAIL"
    AGENT_PERSONA = "AGENT_PERSONA"
    WORKFLOW_TASK = "WORKFLOW_TASK"
    TOOL_API_INSTRUCTIONS = "TOOL_API_INSTRUCTIONS"
    DATA_CONTEXT = "DATA_CONTEXT"
    USER_REQUEST = "USER_REQUEST"
    MODEL_OUTPUT_REQUIREMENTS = "MODEL_OUTPUT_REQUIREMENTS"


class PromptTrustLevel(StrEnum):
    """doc 16 §6 — coarse trust classification used during prompt composition."""

    TRUSTED = "TRUSTED"
    CONTROLLED = "CONTROLLED"
    UNTRUSTED = "UNTRUSTED"


_TRUST_RANK: dict[PromptTrustLevel, int] = {
    PromptTrustLevel.UNTRUSTED: 0,
    PromptTrustLevel.CONTROLLED: 1,
    PromptTrustLevel.TRUSTED: 2,
}


def trust_rank(level: PromptTrustLevel) -> int:
    return _TRUST_RANK[level]
