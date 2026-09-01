from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.embedding_vector.states import EmbeddingModelStatus


class EmbeddingModelDescriptor(BaseModel):
    """Doc 14 §8, §15 — the controlled embedding model registry entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str
    provider: str
    version: str
    dimension: int = Field(gt=0)
    max_input_tokens: int = Field(gt=0)
    status: EmbeddingModelStatus


class VectorMetadata(BaseModel):
    """Doc 14 §26 required vector metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document_id: str
    document_version: int = Field(ge=1)
    source_id: str
    chunk_index: int = Field(ge=0)
    tenant_id: str
    organization_id: str | None = None
    domain: str | None = None


class VectorRecord(BaseModel):
    """Doc 14 §22 vector record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    vector_id: str
    chunk_id: str
    embedding: tuple[float, ...]
    embedding_model: str
    embedding_version: str
    dimension: int = Field(gt=0)
    metadata: VectorMetadata


class VectorSearchFilter(BaseModel):
    """Doc 14 §49-50 — filters constructed from validated claims, never from model output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    organization_ids: tuple[str, ...] = Field(default_factory=tuple)
    domain: str | None = None


class VectorSearchResult(BaseModel):
    """Doc 14 §53 search response entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    vector_id: str
    chunk_id: str
    score: float
    metadata: VectorMetadata
