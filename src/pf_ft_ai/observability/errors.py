from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from pf_ft_ai.common.exceptions import (
    ConfigurationError,
    GuardrailError,
    IntegrationError,
    ModelError,
    PlatformError,
    RAGError,
    ToolError,
    ValidationError,
    WorkflowError,
)


class ErrorCategory(StrEnum):
    """doc 24 §51 standardized error taxonomy."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    API_ERROR = "API_ERROR"
    TOOL_ERROR = "TOOL_ERROR"
    MCP_ERROR = "MCP_ERROR"
    RAG_ERROR = "RAG_ERROR"
    VECTOR_ERROR = "VECTOR_ERROR"
    SLM_ERROR = "SLM_ERROR"
    MODEL_ERROR = "MODEL_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    SERVICE_BUS_ERROR = "SERVICE_BUS_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"
    GUARDRAIL_ERROR = "GUARDRAIL_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorSeverity(StrEnum):
    """doc 24 §53."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredError(BaseModel):
    """doc 24 §52."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    error_code: str
    category: ErrorCategory
    severity: ErrorSeverity
    retryable: bool
    correlation_id: str | None = None
    workflow_instance_id: str | None = None
    message: str


# doc 24 §51 maps directly onto this platform's existing `PlatformError` hierarchy
# (CLAUDE.md's fixed exception tree) — no new exception types are introduced here, only
# a classification of the ones that already exist. Order matters: subclasses are
# checked before their base classes below.
_CATEGORY_BY_EXCEPTION: tuple[tuple[type[PlatformError], ErrorCategory], ...] = (
    (ValidationError, ErrorCategory.VALIDATION_ERROR),
    (ConfigurationError, ErrorCategory.CONFIGURATION_ERROR),
    (GuardrailError, ErrorCategory.GUARDRAIL_ERROR),
    (ToolError, ErrorCategory.TOOL_ERROR),
    (ModelError, ErrorCategory.MODEL_ERROR),
    (RAGError, ErrorCategory.RAG_ERROR),
    (WorkflowError, ErrorCategory.WORKFLOW_ERROR),
    (IntegrationError, ErrorCategory.DEPENDENCY_ERROR),
)


def classify_platform_error(exc: PlatformError) -> ErrorCategory:
    for exception_type, category in _CATEGORY_BY_EXCEPTION:
        if isinstance(exc, exception_type):
            return category
    return ErrorCategory.INTERNAL_ERROR
