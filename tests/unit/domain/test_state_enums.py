from enum import StrEnum

import pytest

from pf_ft_ai.agents.states import AgentRunStatus
from pf_ft_ai.cache.states import CacheStatus
from pf_ft_ai.common.error_category import ErrorCategory
from pf_ft_ai.common.precedence import DataSourcePrecedence
from pf_ft_ai.context.erc.states import ErcLifecycleStatus, ErcSectionStatus
from pf_ft_ai.domain.conversation.states import ConversationStatus
from pf_ft_ai.domain.conversation.value_objects import MessageRole
from pf_ft_ai.domain.session.states import SessionStatus
from pf_ft_ai.domain.state_transition import StateActor
from pf_ft_ai.domain.workflow.states import HilStatus, WaitingType, WorkflowStatus
from pf_ft_ai.integration.execution.states import IdempotencyStatus
from pf_ft_ai.integration.tools.states import ToolCallStatus
from pf_ft_ai.messaging.events.states import EventProcessingStatus
from pf_ft_ai.orchestration.langgraph.states import GraphNodeStatus
from pf_ft_ai.orchestration.supervisor.states import SupervisorStatus
from pf_ft_ai.rag.states import RagStatus
from pf_ft_ai.slm.states import SlmStatus

# (enum class, expected members in doc-5 declaration order) — each tuple is traceable
# back to a specific numbered section of MD files/1 Foundation/5. PF-FT-AI-STATE-MODEL.md.
ENUM_CASES: list[tuple[type[StrEnum], list[str]]] = [
    (
        ConversationStatus,  # doc 5 §8
        [
            "NEW",
            "ACTIVE",
            "WAITING_FOR_USER",
            "WAITING_FOR_EXTERNAL_EVENT",
            "WAITING_FOR_HUMAN",
            "COMPLETED",
            "CLOSED",
            "EXPIRED",
            "ERROR",
        ],
    ),
    (SessionStatus, ["CREATED", "ACTIVE", "IDLE", "EXPIRED", "TERMINATED"]),  # doc 5 §10
    (
        SupervisorStatus,  # doc 5 §12
        [
            "NOT_STARTED",
            "ANALYZING",
            "ROUTED",
            "CLARIFICATION_REQUIRED",
            "ROUTING_FAILED",
            "COMPLETED",
        ],
    ),
    (
        AgentRunStatus,  # doc 5 §14
        [
            "CREATED",
            "INITIALIZING",
            "EXECUTING",
            "WAITING_FOR_TOOL",
            "WAITING_FOR_RAG",
            "WAITING_FOR_SLM",
            "WAITING_FOR_USER",
            "WAITING_FOR_HUMAN",
            "WAITING_FOR_EVENT",
            "COMPLETED",
            "PARTIAL",
            "FAILED",
            "CANCELLED",
        ],
    ),
    (
        WorkflowStatus,  # doc 5 §17
        [
            "CREATED",
            "INITIALIZING",
            "UNDERSTANDING",
            "COLLECTING_CONTEXT",
            "BUILDING_ERC",
            "VALIDATING_CONTEXT",
            "REASONING",
            "EXECUTING_TOOL",
            "VALIDATING_RESULT",
            "WAITING_FOR_USER",
            "WAITING_FOR_HUMAN",
            "WAITING_FOR_EXTERNAL_EVENT",
            "RESUMING",
            "COMPLETING",
            "COMPLETED",
            "PARTIAL",
            "FAILED",
            "CANCELLED",
        ],
    ),
    (
        GraphNodeStatus,  # doc 5 §22
        [
            "PENDING",
            "READY",
            "EXECUTING",
            "WAITING",
            "SUCCEEDED",
            "PARTIAL",
            "FAILED",
            "SKIPPED",
            "CANCELLED",
        ],
    ),
    (
        ErcLifecycleStatus,  # doc 8 §9-10 (Phase 5 authority, supersedes doc 5 §24)
        [
            "NOT_CREATED",
            "REQUIREMENTS_IDENTIFIED",
            "COLLECTING",
            "NORMALIZING",
            "AGGREGATING",
            "VALIDATING",
            "READY",
            "REFRESH_REQUIRED",
            "REFRESHING",
            "STALE",
            "INVALID",
            "FAILED",
        ],
    ),
    (
        ErcSectionStatus,  # doc 5 §25
        [
            "NOT_REQUESTED",
            "REQUESTED",
            "COLLECTING",
            "COMPLETE",
            "PARTIAL",
            "UNAVAILABLE",
            "STALE",
            "FAILED",
        ],
    ),
    (
        ToolCallStatus,  # doc 10 §34 (Phase 6 authority, supersedes doc 5 §30)
        [
            "TOOL_REQUESTED",
            "TOOL_RESOLVED",
            "INPUT_VALIDATED",
            "AUTHORIZATION_CHECKED",
            "EXECUTING",
            "RESPONSE_RECEIVED",
            "RESPONSE_VALIDATED",
            "RESPONSE_TRANSFORMED",
            "TOOL_COMPLETED",
            "REJECTED",
            "TIMEOUT",
            "RETRYING",
            "FAILED",
            "UNKNOWN",
        ],
    ),
    (
        RagStatus,
        [
            "NOT_REQUIRED",
            "REQUESTED",
            "RETRIEVING",
            "RETRIEVED",
            "NO_RESULTS",
            "FAILED",
            "COMPLETED",
        ],
    ),  # doc 5 §33
    (
        SlmStatus,  # doc 5 §35
        [
            "REQUESTED",
            "QUEUED",
            "EXECUTING",
            "SUCCEEDED",
            "RETRYING",
            "TIMEOUT",
            "FAILED",
            "FALLBACK",
            "BLOCKED",
        ],
    ),
    (
        CacheStatus,  # doc 5 §37
        ["MISS", "HIT", "STALE", "INVALIDATED", "REFRESHING", "REFRESHED", "ERROR"],
    ),
    (
        EventProcessingStatus,  # doc 5 §39
        [
            "RECEIVED",
            "VALIDATING",
            "VALID",
            "DUPLICATE",
            "PROCESSING",
            "PROCESSED",
            "RETRYING",
            "FAILED",
            "DEAD_LETTERED",
        ],
    ),
    (
        WaitingType,  # doc 5 §40
        [
            "WAITING_FOR_USER",
            "WAITING_FOR_HUMAN",
            "WAITING_FOR_EXTERNAL_EVENT",
            "WAITING_FOR_DEPENDENCY",
        ],
    ),
    (
        HilStatus,
        ["NOT_REQUIRED", "REQUESTED", "WAITING", "APPROVED", "REJECTED", "CANCELLED"],
    ),  # doc 5 §42
    (
        ErrorCategory,  # doc 5 §45
        [
            "VALIDATION",
            "AUTHORIZATION",
            "BUSINESS_RESULT",
            "TECHNICAL",
            "DEPENDENCY",
            "AI",
            "GUARDRAIL",
            "SECURITY",
            "TIMEOUT",
            "CONCURRENCY",
            "DATA",
            "EVENT",
        ],
    ),
    (
        IdempotencyStatus,
        ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "FAILED", "UNKNOWN"],
    ),  # doc 5 §47
    (
        StateActor,  # doc 5 §90
        [
            "USER",
            "SUPERVISOR",
            "AGENT",
            "LANGGRAPH",
            "TOOL",
            "ENTERPRISE_EVENT",
            "HUMAN",
            "SYSTEM",
            "ADMIN",
            "RECOVERY",
        ],
    ),
    (MessageRole, ["USER", "ASSISTANT", "SYSTEM", "TOOL"]),  # doc 6 §17
    (DataSourcePrecedence, ["ENTERPRISE", "ERC", "CACHE", "RAG", "SLM"]),  # CLAUDE.md Golden Rule
]


@pytest.mark.parametrize(
    "enum_cls,expected_members", ENUM_CASES, ids=[case[0].__name__ for case in ENUM_CASES]
)
def test_should_match_documented_enum_members(
    enum_cls: type[StrEnum], expected_members: list[str]
) -> None:
    assert [member.value for member in enum_cls] == expected_members
    assert all(isinstance(member, str) for member in enum_cls)
