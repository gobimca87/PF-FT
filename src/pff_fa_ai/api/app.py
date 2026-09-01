from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

from pff_fa_ai.api.dependencies import build_app_state
from pff_fa_ai.api.errors import platform_error_handler
from pff_fa_ai.api.v1 import chat, conversations, health, sessions
from pff_fa_ai.common.exceptions import PlatformError
from pff_fa_ai.configuration.models import Environment

CallNext = Callable[[Request], Awaitable[Response]]


def create_app(*, environment: Environment = "dev") -> FastAPI:
    app = FastAPI(title="PFF AI", version="0.1.0")
    app.state.app_state = build_app_state(environment=environment)

    app.add_exception_handler(PlatformError, platform_error_handler)

    app.include_router(chat.router)
    app.include_router(conversations.router)
    app.include_router(sessions.router)
    app.include_router(health.router)

    @app.middleware("http")
    async def add_correlation_context(request: Request, call_next: CallNext) -> Response:
        request.state.request_id = uuid.uuid4().hex
        request.state.correlation_id = request.headers.get("x-correlation-id") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        response.headers["x-correlation-id"] = request.state.correlation_id
        return response

    return app
