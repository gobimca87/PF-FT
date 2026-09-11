from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

import httpx

from pff_fa_ai.common.correlation import new_id
from pff_fa_ai.common.exceptions import IntegrationError
from pff_fa_ai.slm.models import SlmRequest, SlmResponse, SlmUsage
from pff_fa_ai.slm.states import ProviderHealthStatus


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
    """Dormant abstraction adapter — NOT a declared provider (ADR-D3-29 supersedes ADR-D3-13).

    The hosted-first plane is Azure AI Foundry (in-tenancy) and all evaluation/experimentation
    runs in-tenancy on Foundry too, so the design has no active external SLM path. This adapter
    is kept behind the ADR-D3-14 abstraction only so an external provider could be reintroduced
    in future without a rewrite; if ever activated it is `EXTERNAL` placement and MUST be wrapped
    by the mandatory masking boundary (ADR-D6-19)."""

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


class AzureAIFoundrySLMProvider:
    """ADR-D3-29: the hosted-first inference plane is Azure AI Foundry (in-tenancy Azure),
    superseding the Hugging Face Inference API as the production/hosted path (ADR-D3-13 is
    superseded).

    This is the hosted-first plane for both production and evaluation/experimentation — the
    design has no active external SLM path (the Hugging Face adapter is dormant).

    Calls the OpenAI-compatible Azure AI Model Inference chat-completions API. The shared
    httpx client carries the Foundry endpoint (base_url) and the Entra ID / managed-identity
    bearer token (or key), resolved from Key Vault via `*_secret_ref` (ADR-D5-07); no
    provider SDK is imported past this adapter (ADR-D3-14, ADR-D2-01). Because Foundry runs
    in-tenancy, its placement is `SlmPlacement.MANAGED_IN_TENANCY`, so the mandatory
    external-masking boundary (ADR-D6-19 / `MaskedExternalSLMProvider`) does not wrap it —
    masking is applied per task class, as for a self-hosted SLM.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        model_version: str,
        api_version: str = "2024-05-01-preview",
    ) -> None:
        self._client = client
        self._model_version = model_version
        self._api_version = api_version

    async def generate(self, request: SlmRequest) -> SlmResponse:
        response = await self._client.post(
            "/models/chat/completions",
            params={"api-version": self._api_version},
            json={
                "model": request.model_id,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in request.messages
                ],
                "temperature": request.temperature,
                "top_p": request.top_p,
                "max_tokens": request.max_output_tokens,
            },
        )
        if response.status_code >= 400:
            raise IntegrationError(
                f"Azure AI Foundry SLM request failed with status {response.status_code}",
                details={"status_code": response.status_code},
            )
        body = response.json()
        choice = body["choices"][0]
        usage = body.get("usage", {})
        return SlmResponse(
            request_id=new_id("slm-req"),
            model_id=request.model_id,
            model_version=self._model_version,
            output=choice["message"]["content"],
            usage=SlmUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    async def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        response = await self.generate(request)
        for word in response.output.split():
            yield word + " "

    async def health(self) -> ProviderHealthStatus:
        try:
            response = await self._client.get(
                "/models", params={"api-version": self._api_version}
            )
        except httpx.HTTPError:
            return ProviderHealthStatus.UNAVAILABLE
        return (
            ProviderHealthStatus.HEALTHY
            if response.status_code < 400
            else ProviderHealthStatus.DEGRADED
        )
