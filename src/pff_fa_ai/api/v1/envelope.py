from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    error_code: str
    message: str


class ResponseEnvelope(BaseModel, Generic[DataT]):
    model_config = ConfigDict(frozen=True)

    request_id: str
    conversation_id: str | None = None
    status: str
    message: str | None = None
    data: DataT | None = None
    links: list[str] = Field(default_factory=list)
    errors: list[ErrorDetail] = Field(default_factory=list)
