from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from pff_fa_ai.api.v1.envelope import ErrorDetail, ResponseEnvelope
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

_STATUS_BY_EXCEPTION: tuple[tuple[type[PlatformError], int], ...] = (
    (ValidationError, status.HTTP_400_BAD_REQUEST),
    (GuardrailError, status.HTTP_400_BAD_REQUEST),
    (WorkflowError, status.HTTP_409_CONFLICT),
    (ToolError, status.HTTP_502_BAD_GATEWAY),
    (IntegrationError, status.HTTP_502_BAD_GATEWAY),
    (ModelError, status.HTTP_502_BAD_GATEWAY),
    (RAGError, status.HTTP_502_BAD_GATEWAY),
    (ConfigurationError, status.HTTP_500_INTERNAL_SERVER_ERROR),
)


def _status_code_for(error: PlatformError) -> int:
    for exception_type, http_status in _STATUS_BY_EXCEPTION:
        if isinstance(error, exception_type):
            return http_status
    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def platform_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, PlatformError):
        raise exc
    request_id = getattr(request.state, "request_id", "unknown")
    envelope = ResponseEnvelope[None](
        request_id=request_id,
        status="FAILED",
        errors=[ErrorDetail(error_code=type(exc).__name__, message=exc.message)],
    )
    return JSONResponse(status_code=_status_code_for(exc), content=envelope.model_dump(mode="json"))
