from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MessageRole = Literal["system", "user", "assistant", "tool"]
FinishReason = Literal["stop", "length", "content_filter", "tool_call", "error"]


class SlmMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: MessageRole
    content: str


class SlmUsage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class SlmRequest(BaseModel):
    """Doc 15 / DEVELOPMENT-GUIDE Phase 9 request contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    messages: tuple[SlmMessage, ...]
    temperature: float = Field(ge=0, le=2)
    top_p: float = Field(gt=0, le=1)
    max_output_tokens: int = Field(gt=0)
    stream: bool = False
    response_format: str | None = None


class SlmResponse(BaseModel):
    """Doc 15 / DEVELOPMENT-GUIDE Phase 9 response contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: str
    model_id: str
    model_version: str
    output: str
    usage: SlmUsage
    finish_reason: FinishReason
