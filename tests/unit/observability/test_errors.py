import pytest

from pff_fa_ai.common.exceptions import (
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
from pff_fa_ai.observability.errors import ErrorCategory, classify_platform_error


@pytest.mark.parametrize(
    ("exception", "expected_category"),
    [
        (ValidationError("x"), ErrorCategory.VALIDATION_ERROR),
        (ConfigurationError("x"), ErrorCategory.CONFIGURATION_ERROR),
        (GuardrailError("x"), ErrorCategory.GUARDRAIL_ERROR),
        (ToolError("x"), ErrorCategory.TOOL_ERROR),
        (ModelError("x"), ErrorCategory.MODEL_ERROR),
        (RAGError("x"), ErrorCategory.RAG_ERROR),
        (WorkflowError("x"), ErrorCategory.WORKFLOW_ERROR),
        (IntegrationError("x"), ErrorCategory.DEPENDENCY_ERROR),
    ],
)
def test_should_classify_each_platform_error_subclass(
    exception: Exception, expected_category: ErrorCategory
) -> None:
    assert classify_platform_error(exception) is expected_category  # type: ignore[arg-type]


def test_should_fall_back_to_internal_error_for_the_bare_platform_error() -> None:
    assert classify_platform_error(PlatformError("x")) is ErrorCategory.INTERNAL_ERROR


def test_should_cover_every_declared_error_category_value() -> None:
    """doc 24 §51 lists 21 categories — confirms none were dropped/misspelled."""
    expected = {
        "VALIDATION_ERROR",
        "AUTHENTICATION_ERROR",
        "AUTHORIZATION_ERROR",
        "CONFIGURATION_ERROR",
        "DEPENDENCY_ERROR",
        "API_ERROR",
        "TOOL_ERROR",
        "MCP_ERROR",
        "RAG_ERROR",
        "VECTOR_ERROR",
        "SLM_ERROR",
        "MODEL_ERROR",
        "MEMORY_ERROR",
        "CACHE_ERROR",
        "SERVICE_BUS_ERROR",
        "TIMEOUT_ERROR",
        "RATE_LIMIT_ERROR",
        "WORKFLOW_ERROR",
        "GUARDRAIL_ERROR",
        "SECURITY_ERROR",
        "INTERNAL_ERROR",
    }
    assert {category.value for category in ErrorCategory} == expected
