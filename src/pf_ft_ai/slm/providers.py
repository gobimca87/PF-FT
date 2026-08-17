from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

import httpx

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.common.exceptions import IntegrationError
from pf_ft_ai.slm.models import SlmRequest, SlmResponse, SlmUsage
from pf_ft_ai.slm.states import ProviderHealthStatus


class SLMProvider(Protocol):
    """Doc 15 / DEVELOPMENT-GUIDE Phase 9 — agents call this abstraction only, never a
    hard-coded provider (doc 15 core principle)."""

    async def generate(self, request: SlmRequest) -> SlmResponse: ...

    def stream(self, request: SlmRequest) -> AsyncIterator[str]: ...

    async def health(self) -> ProviderHealthStatus: ...


class MockSLMProvider:
    """Deterministic provider for tests/evaluation — doc 15 requires this alongside the
    real provider, mirroring `MockEmbeddingProvider` (doc 14)."""

    def __init__(self, *, model_version: str = "1.0.0") -> None:
        self._model_version = model_version

    async def generate(self, request: SlmRequest) -> SlmResponse:
        last_user_message = next(
            (m.content for m in reversed(request.messages) if m.role == "user"), ""
        )
        output = f"[mock response to: {last_user_message}]"
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        completion_tokens = len(output.split())
        return SlmResponse(
            request_id=new_id("slm-req"),
            model_id=request.model_id,
            model_version=self._model_version,
            output=output,
            usage=SlmUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            finish_reason="stop",
        )

    async def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        response = await self.generate(request)
        for word in response.output.split():
            yield word + " "

    async def health(self) -> ProviderHealthStatus:
        return ProviderHealthStatus.HEALTHY


class HuggingFaceSLMProvider:
    """Doc 15: initial provider is the Hugging Face Inference API."""

    def __init__(self, client: httpx.AsyncClient, *, model_version: str) -> None:
        self._client = client
        self._model_version = model_version

    async def generate(self, request: SlmRequest) -> SlmResponse:
        response = await self._client.post(
            f"/models/{request.model_id}",
            json={
                "inputs": [
                    {"role": message.role, "content": message.content}
                    for message in request.messages
                ],
                "parameters": {
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "max_new_tokens": request.max_output_tokens,
                },
            },
        )
        if response.status_code >= 400:
            raise IntegrationError(
                f"Hugging Face SLM request failed with status {response.status_code}",
                details={"status_code": response.status_code},
            )
        body = response.json()
        usage = body.get("usage", {})
        return SlmResponse(
            request_id=new_id("slm-req"),
            model_id=request.model_id,
            model_version=self._model_version,
            output=body["output"],
            usage=SlmUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            finish_reason=body.get("finish_reason", "stop"),
        )

    async def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        response = await self.generate(request)
        for word in response.output.split():
            yield word + " "

    async def health(self) -> ProviderHealthStatus:
        try:
            response = await self._client.get(f"/models/{self._model_version}")
        except httpx.HTTPError:
            return ProviderHealthStatus.UNAVAILABLE
        return (
            ProviderHealthStatus.HEALTHY
            if response.status_code < 400
            else ProviderHealthStatus.DEGRADED
        )
