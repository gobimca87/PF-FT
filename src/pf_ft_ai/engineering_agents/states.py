from __future__ import annotations

from enum import IntEnum, StrEnum

from pf_ft_ai.evaluation.states import EvaluationStatus
from pf_ft_ai.guardrails.states import GuardrailSeverity
from pf_ft_ai.prompt_engineering.states import PromptRiskLevel

# doc 23 §57: PASS/FAIL/WARNING/ERROR/SKIPPED/NOT_APPLICABLE — identical in meaning and
# membership to doc 21's evaluation status (both answer "did this check pass"), so it is
# reused here rather than duplicated (mirrors the `guardrails`/`prompt_engineering`
# reuse pattern already established between those two packages).
AgentResultStatus = EvaluationStatus

# doc 23 §18's Code Review severities (CRITICAL/HIGH/MEDIUM/LOW/INFO) are identical to
# doc 18's `GuardrailSeverity` — reused rather than duplicated. `None` on a result means
# "no findings" (doc 23 §56 example shows a bare `"severity": "NONE"` for that case).
FindingSeverity = GuardrailSeverity

# doc 18 §100 already ranks this exact severity set for guardrail decisions; the same
# ranking applies unchanged to engineering-agent findings (doc 23 §18). Shared here so
# `gate.py` and every agent that needs "worst severity among these findings" logic use
# one explicit ranking rather than relying on enum declaration order.
FINDING_SEVERITY_RANK: dict[FindingSeverity, int] = {
    FindingSeverity.INFO: 0,
    FindingSeverity.LOW: 1,
    FindingSeverity.MEDIUM: 2,
    FindingSeverity.HIGH: 3,
    FindingSeverity.CRITICAL: 4,
}

# doc 23 §130: "Each engineering agent must be governed like a production AI capability"
# — reuses the same LOW/MEDIUM/HIGH/CRITICAL risk vocabulary doc 16 already assigns to
# governed prompt artifacts, rather than a second identical enum.
EngineeringAgentRisk = PromptRiskLevel


class ExecutionMode(StrEnum):
    """doc 23 §10. Default is READ_ONLY/VALIDATE (DEVELOPMENT-GUIDE Phase 18)."""

    READ_ONLY = "READ_ONLY"
    ANALYZE = "ANALYZE"
    VALIDATE = "VALIDATE"
    GENERATE = "GENERATE"
    SUGGEST_REMEDIATION = "SUGGEST_REMEDIATION"
    CONTROLLED_MODIFY = "CONTROLLED_MODIFY"


class PermissionLevel(IntEnum):
    """doc 23 §11 — ordered so `level >= PermissionLevel.LEVEL_3` style checks work."""

    LEVEL_0_READ_ONLY = 0
    LEVEL_1_REPORT = 1
    LEVEL_2_GENERATE_TEST_OR_DOCS = 2
    LEVEL_3_PROPOSE_CHANGES = 3
    LEVEL_4_CREATE_PR_CHANGES = 4
    LEVEL_5_APPROVED_AUTOMATED_REMEDIATION = 5


class RemediationMode(StrEnum):
    """doc 23 §61. Default is REPORT_ONLY."""

    REPORT_ONLY = "REPORT_ONLY"
    SUGGEST = "SUGGEST"
    CREATE_PATCH = "CREATE_PATCH"
    CREATE_BRANCH = "CREATE_BRANCH"
    CREATE_PR = "CREATE_PR"


class AgentLifecycleStatus(StrEnum):
    """doc 23 §83."""

    PROPOSED = "PROPOSED"
    DESIGNED = "DESIGNED"
    DEVELOPED = "DEVELOPED"
    TESTED = "TESTED"
    EVALUATED = "EVALUATED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class GateStatus(StrEnum):
    """doc 23 §58 — the aggregate outcome across every agent result in a run."""

    PASS = "PASS"  # noqa: S105 -- gate outcome, not a credential
    WARNING = "WARNING"
    FAIL = "FAIL"


class ChangedComponent(StrEnum):
    """doc 23 §8 — the artifact categories change-impact analysis classifies a diff
    into, driving which agents doc 23 §9 selects."""

    PYTHON_CODE = "PYTHON_CODE"
    FASTAPI = "FASTAPI"
    LANGGRAPH = "LANGGRAPH"
    AGENTS = "AGENTS"
    PROMPTS = "PROMPTS"
    MODELS = "MODELS"
    SLM_CONFIGURATION = "SLM_CONFIGURATION"
    RAG = "RAG"
    EMBEDDINGS = "EMBEDDINGS"
    VECTOR = "VECTOR"
    TOOLS = "TOOLS"
    MCP = "MCP"
    SERVICE_BUS = "SERVICE_BUS"
    ERC = "ERC"
    MEMORY = "MEMORY"
    CACHE = "CACHE"
    GUARDRAILS = "GUARDRAILS"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CONFIGURATION = "CONFIGURATION"
    TESTS = "TESTS"
    DOCUMENTATION = "DOCUMENTATION"
