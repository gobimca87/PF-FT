from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.integration.api.catalog import ApiCatalogEntry


class EnterpriseApiResponse(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    status_code: int
    body: Any = None
    headers: dict[str, str] = Field(default_factory=dict)


class EnterpriseHttpClient(Protocol):
    async def request(
        self,
        *,
        entry: ApiCatalogEntry,
        path_params: Mapping[str, str] | None = None,
        query_params: Mapping[str, str] | None = None,
        body: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> EnterpriseApiResponse: ...


def _resolve_path(template: str, path_params: Mapping[str, str] | None) -> str:
    resolved = template
    for key, value in (path_params or {}).items():
        resolved = resolved.replace(f"{{{key}}}", value)
    return resolved


class HttpxEnterpriseHttpClient:
    """doc 10 §81: centralized enterprise HTTP client abstraction."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def request(
        self,
        *,
        entry: ApiCatalogEntry,
        path_params: Mapping[str, str] | None = None,
        query_params: Mapping[str, str] | None = None,
        body: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> EnterpriseApiResponse:
        response = await self._client.request(
            entry.endpoint.method,
            _resolve_path(entry.endpoint.path, path_params),
            params=query_params,
            json=body,
            headers=headers,
        )
        try:
            parsed_body: Any = response.json()
        except ValueError:
            parsed_body = response.text
        return EnterpriseApiResponse(
            status_code=response.status_code, body=parsed_body, headers=dict(response.headers)
        )
