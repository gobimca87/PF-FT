"""doc 22 §20-21: reusable enterprise-API mock transport builders, shared across the
contract/component/resilience test layers so every layer mocks at the same boundary
with realistic, consistent response shapes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


def status_transport(
    status_code: int, *, json_body: Any = None, headers: Mapping[str, str] | None = None
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=json_body, headers=headers)

    return httpx.MockTransport(handler)


def text_transport(status_code: int, *, text_body: str) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, text=text_body)

    return httpx.MockTransport(handler)


def empty_transport(status_code: int = 200) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    return httpx.MockTransport(handler)


def timeout_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("simulated enterprise API timeout", request=request)

    return httpx.MockTransport(handler)
