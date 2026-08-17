import pytest

from pf_ft_ai.integration.errors.codes import (
    IntegrationErrorCode,
    classify_http_status,
    is_retryable,
)


@pytest.mark.parametrize(
    "status_code,expected",
    [
        (400, IntegrationErrorCode.VALIDATION_ERROR),
        (401, IntegrationErrorCode.AUTHENTICATION_ERROR),
        (403, IntegrationErrorCode.AUTHORIZATION_ERROR),
        (404, IntegrationErrorCode.NOT_FOUND),
        (409, IntegrationErrorCode.CONFLICT),
        (429, IntegrationErrorCode.RATE_LIMITED),
        (500, IntegrationErrorCode.DEPENDENCY_ERROR),
        (502, IntegrationErrorCode.BAD_GATEWAY),
        (503, IntegrationErrorCode.SERVICE_UNAVAILABLE),
        (504, IntegrationErrorCode.TIMEOUT),
        (418, IntegrationErrorCode.UNKNOWN),
    ],
)
def test_should_classify_http_status_codes(
    status_code: int, expected: IntegrationErrorCode
) -> None:
    assert classify_http_status(status_code) == expected


@pytest.mark.parametrize(
    "code,expected",
    [
        (IntegrationErrorCode.TIMEOUT, True),
        (IntegrationErrorCode.SERVICE_UNAVAILABLE, True),
        (IntegrationErrorCode.BAD_GATEWAY, True),
        (IntegrationErrorCode.RATE_LIMITED, True),
        (IntegrationErrorCode.DEPENDENCY_ERROR, True),
        (IntegrationErrorCode.VALIDATION_ERROR, False),
        (IntegrationErrorCode.AUTHENTICATION_ERROR, False),
        (IntegrationErrorCode.AUTHORIZATION_ERROR, False),
        (IntegrationErrorCode.NOT_FOUND, False),
        (IntegrationErrorCode.CONFLICT, False),
        (IntegrationErrorCode.SCHEMA_ERROR, False),
        (IntegrationErrorCode.UNKNOWN, False),
    ],
)
def test_should_classify_retryability_per_doc10_section42_43(
    code: IntegrationErrorCode, expected: bool
) -> None:
    assert is_retryable(code) is expected
