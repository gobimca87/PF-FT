from __future__ import annotations

from enum import StrEnum


class IntegrationErrorCode(StrEnum):
    """doc 10 §40."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    BAD_GATEWAY = "BAD_GATEWAY"
    SCHEMA_ERROR = "SCHEMA_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    UNKNOWN = "UNKNOWN"


_RETRYABLE_CODES = frozenset({
    IntegrationErrorCode.TIMEOUT,
    IntegrationErrorCode.SERVICE_UNAVAILABLE,
    IntegrationErrorCode.BAD_GATEWAY,
    IntegrationErrorCode.RATE_LIMITED,
    IntegrationErrorCode.DEPENDENCY_ERROR,
})

_STATUS_TO_ERROR_CODE: dict[int, IntegrationErrorCode] = {
    400: IntegrationErrorCode.VALIDATION_ERROR,
    401: IntegrationErrorCode.AUTHENTICATION_ERROR,
    403: IntegrationErrorCode.AUTHORIZATION_ERROR,
    404: IntegrationErrorCode.NOT_FOUND,
    409: IntegrationErrorCode.CONFLICT,
    429: IntegrationErrorCode.RATE_LIMITED,
    500: IntegrationErrorCode.DEPENDENCY_ERROR,
    502: IntegrationErrorCode.BAD_GATEWAY,
    503: IntegrationErrorCode.SERVICE_UNAVAILABLE,
    504: IntegrationErrorCode.TIMEOUT,
}


def classify_http_status(status_code: int) -> IntegrationErrorCode:
    """doc 10 §39: translate enterprise-specific errors to stable platform categories."""
    return _STATUS_TO_ERROR_CODE.get(status_code, IntegrationErrorCode.UNKNOWN)


def is_retryable(code: IntegrationErrorCode) -> bool:
    """doc 10 §42-43."""
    return code in _RETRYABLE_CODES
