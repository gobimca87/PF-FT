from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Environment = Literal["dev", "test", "uat", "staging", "prod"]

ALLOWED_ENVIRONMENTS: tuple[Environment, ...] = ("dev", "test", "uat", "staging", "prod")


class ConfigurationMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    configuration_id: str
    version: str
    owner: str
    effective_date: date


class EnvironmentIdentity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: Environment
    region: str
    platform_version: str


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    request_timeout_seconds: int = Field(gt=0)
    max_retries: int = Field(ge=0)


class PlatformConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    metadata: ConfigurationMetadata
    environment: EnvironmentIdentity
    runtime: RuntimeConfig
    configuration_hash: str


class ReleaseManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    release_id: str
    version: str
    environment: Environment
    application_version: str
    git_commit: str | None = None
    configuration_hash: str | None = None
    components: dict[str, str] = Field(default_factory=dict)


class ConversationSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_history_messages: int = Field(gt=0)
    max_history_tokens: int = Field(gt=0)
    summary_threshold_tokens: int = Field(gt=0)
    max_message_size: int = Field(gt=0)


class SessionSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    idle_timeout_minutes: int = Field(gt=0)
    absolute_timeout_hours: int = Field(gt=0)


class ConversationSecuritySettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    enforce_ownership: bool
    enforce_tenant_isolation: bool


class WorkflowSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    resume_enabled: bool


class ConversationConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    conversation: ConversationSettings
    session: SessionSettings
    security: ConversationSecuritySettings
    workflow: WorkflowSettings
    configuration_hash: str


class HarnessLimits(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_graph_steps: int = Field(gt=0)
    max_agent_loops: int = Field(gt=0)
    max_tool_calls: int = Field(gt=0)
    max_parallel_calls: int = Field(gt=0)
    max_context_tokens: int = Field(gt=0)
    max_output_tokens: int = Field(gt=0)
    max_execution_time_seconds: int = Field(gt=0)
    max_retry_count: int = Field(ge=0)
    max_batch_size: int = Field(gt=0)


class HarnessConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    harness: HarnessLimits
    configuration_hash: str


class ErcFreshnessSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    default_ttl_seconds: int = Field(gt=0)


class ErcValidationSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    enforce_schema: bool
    enforce_completeness: bool
    enforce_referential_integrity: bool


class ErcSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str
    freshness: ErcFreshnessSettings
    validation: ErcValidationSettings


class ErcConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    erc: ErcSettings
    configuration_hash: str


class BatchingSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    batch_size: int = Field(gt=0)
    max_parallel_batches: int = Field(gt=0)
    max_retry_attempts: int = Field(ge=0)


class BatchingConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    batching: BatchingSettings
    configuration_hash: str


class ContextBudgetSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_input_tokens: int = Field(gt=0)
    reserved_output_tokens: int = Field(gt=0)
    safety_margin_tokens: int = Field(ge=0)


class ContextBudgetConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    context_budget: ContextBudgetSettings
    configuration_hash: str


class RetrySettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_attempts: int = Field(gt=0)
    backoff: str
    initial_ms: int = Field(gt=0)
    max_ms: int = Field(gt=0)
    jitter: bool


class CircuitBreakerSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    failure_threshold: int = Field(gt=0)
    cooldown_seconds: int = Field(gt=0)
    half_open_max_calls: int = Field(gt=0)


class ConcurrencyPoolSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_parallel: int = Field(gt=0)


class ConcurrencySettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    global_max: int = Field(gt=0)
    enterprise: ConcurrencyPoolSettings
    mcp: ConcurrencyPoolSettings


class TimeoutSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    connect_ms: int = Field(gt=0)
    read_ms: int = Field(gt=0)
    total_ms: int = Field(gt=0)


class IntegrationConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    retry: RetrySettings
    circuit_breaker: CircuitBreakerSettings
    concurrency: ConcurrencySettings
    timeout: TimeoutSettings
    configuration_hash: str


class RedisConnectionSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    host: str
    port: int = Field(gt=0, le=65535)
    ssl: bool
    db: int = Field(ge=0)
    password: str | None = Field(default=None, repr=False)


class RedisConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    redis: RedisConnectionSettings
    configuration_hash: str


class MemorySettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    default_ttl_seconds: int = Field(gt=0)
    category_ttl_seconds: dict[str, int] = Field(default_factory=dict)


class MemoryConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    memory: MemorySettings
    configuration_hash: str


class CacheSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    default_ttl_seconds: int = Field(gt=0)
    category_ttl_seconds: dict[str, int] = Field(default_factory=dict)


class CacheConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cache: CacheSettings
    configuration_hash: str


class ChunkingSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    target_tokens: int = Field(gt=0)
    overlap_tokens: int = Field(ge=0)


class RetrievalSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    vector_top_k: int = Field(gt=0)
    keyword_top_k: int = Field(gt=0)


class RerankingSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    top_n: int = Field(gt=0)


class AgenticRagSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_iterations: int = Field(gt=0)


class RagConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunking: ChunkingSettings
    retrieval: RetrievalSettings
    reranking: RerankingSettings
    agentic_rag: AgenticRagSettings
    configuration_hash: str


class EmbeddingSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str
    model_id: str
    model_version: str
    dimension: int = Field(gt=0)
    max_input_tokens: int = Field(gt=0)
    batch_size: int = Field(gt=0)


class EmbeddingConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    embedding: EmbeddingSettings
    configuration_hash: str


class SlmSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str
    model_id: str
    model_version: str
    temperature: float = Field(ge=0, le=2)
    top_p: float = Field(gt=0, le=1)
    max_output_tokens: int = Field(gt=0)


class SlmConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    slm: SlmSettings
    retry: RetrySettings
    circuit_breaker: CircuitBreakerSettings
    configuration_hash: str
