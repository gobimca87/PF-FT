from __future__ import annotations

import hashlib
from typing import Protocol

import httpx

from pff_fa_ai.common.exceptions import IntegrationError


class EmbeddingProvider(Protocol):
    """Doc 14 §9 — the application never depends on one provider directly."""

    async def embed_documents(self, texts: list[str]) -> list[tuple[float, ...]]: ...

    async def embed_query(self, text: str) -> tuple[float, ...]: ...


class MockEmbeddingProvider:
    """Deterministic hash-based embedding — required for reproducible tests/evaluation,
    same rationale as doc 15's mandatory MockSLMProvider. Also the current default
    provider (docs/adr/0003) until a real model has been evaluation-selected (doc 14 §13).
    """

    def __init__(self, *, dimension: int = 32) -> None:
        self._dimension = dimension

    async def embed_documents(self, texts: list[str]) -> list[tuple[float, ...]]:
        return [self._embed(text) for text in texts]

    async def embed_query(self, text: str) -> tuple[float, ...]:
        return self._embed(text)

    def _embed(self, text: str) -> tuple[float, ...]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return tuple(digest[index % len(digest)] / 255.0 for index in range(self._dimension))


class HuggingFaceEmbeddingProvider:
    """Doc 14 §11: initial provider is the Hugging Face Inference API."""

    def __init__(self, client: httpx.AsyncClient, *, model_id: str) -> None:
        self._client = client
        self._model_id = model_id

    async def embed_documents(self, texts: list[str]) -> list[tuple[float, ...]]:
        response = await self._client.post(f"/models/{self._model_id}", json={"inputs": texts})
        if response.status_code >= 400:
            raise IntegrationError(
                f"Hugging Face embedding request failed with status {response.status_code}",
                details={"status_code": response.status_code},
            )
        return [tuple(vector) for vector in response.json()]

    async def embed_query(self, text: str) -> tuple[float, ...]:
        vectors = await self.embed_documents([text])
        return vectors[0]
