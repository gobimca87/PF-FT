from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.rag.states import DocumentLifecycleStatus, RagStatus, SourceAuthorityLevel


class SourceRegistration(BaseModel):
    """Doc 13 §8 — every RAG source must be registered before ingestion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    name: str
    source_type: str
    owner: str
    authority_level: SourceAuthorityLevel


class DocumentRecord(BaseModel):
    """Doc 13 §12-13 — stable document identity + version for change detection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    source_id: str
    title: str
    document_version: int = Field(ge=1)
    content_hash: str
    status: DocumentLifecycleStatus


class Chunk(BaseModel):
    """Doc 13 §30 chunk metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str
    document_id: str
    document_version: int = Field(ge=1)
    source_id: str
    chunk_index: int = Field(ge=0)
    content: str
    content_hash: str
    title: str
    tenant_id: str
    organization_id: str | None = None
    page: int | None = None
    section: str | None = None


class Citation(BaseModel):
    """Doc 13 §81 citation architecture — built only from actually-retrieved chunk fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    document_version: int = Field(ge=1)
    title: str
    chunk_id: str
    page: int | None = None
    section: str | None = None


class RetrievedChunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk: Chunk
    score: float


class RagQuery(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    query_text: str
    tenant_id: str
    organization_ids: tuple[str, ...] = Field(default_factory=tuple)
    domain: str | None = None


class RagResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: RagStatus
    chunks: tuple[RetrievedChunk, ...] = Field(default_factory=tuple)
    citations: tuple[Citation, ...] = Field(default_factory=tuple)
