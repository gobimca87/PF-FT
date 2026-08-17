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


class GuardrailSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    approved_model_ids: tuple[str, ...] = Field(default_factory=tuple)
    fail_open_boundaries: tuple[str, ...] = Field(default_factory=tuple)


class GuardrailConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    guardrail: GuardrailSettings
    configuration_hash: str


class ServiceBusConnectionSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    connection_string: str = Field(repr=False)


class TopicSettings(BaseModel):
    """doc 11 §28-31, §128 — one topic per environment, filtered to a dedicated AI
    subscription so the platform never consumes unrelated enterprise events."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    description: str
    subscription_name: str
    subscription_description: str
    event_type_filters: tuple[str, ...] = Field(default_factory=tuple)


class ServiceBusConsumerSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_concurrent_messages: int = Field(gt=0)
    processing_timeout_seconds: int = Field(gt=0)


class EventRetrySettings(BaseModel):
    """doc 11 §75 — note the seconds-based fields, distinct from integration's
    millisecond-based `RetrySettings`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_attempts: int = Field(gt=0)
    initial_seconds: int = Field(gt=0)
    max_seconds: int = Field(gt=0)
    jitter: bool


class ServiceBusConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    connection: ServiceBusConnectionSettings
    topic: TopicSettings
    consumer: ServiceBusConsumerSettings
    retry: EventRetrySettings
    configuration_hash: str


class PortalLinkPolicySettings(BaseModel):
    """doc 12 §32/§128 — `allowed_domains` starts empty: no real portal hostname is
    approved yet, so every link resolution fails closed until one is configured."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_links_per_response: int = Field(gt=0)
    allowed_domains: tuple[str, ...] = Field(default_factory=tuple)


class PortalLinkConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    link_policy: PortalLinkPolicySettings
    configuration_hash: str


class LangfuseSettings(BaseModel):
    """doc 24 §44-45: host/public_key/secret_key always come from `*_secret_ref` —
    never inlined. All three are optional because `enabled: false` (the default until a
    real Langfuse project exists) never needs them (doc 24 §48)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = False
    host: str | None = Field(default=None)
    public_key: str | None = Field(default=None)
    secret_key: str | None = Field(default=None, repr=False)


class ObservabilityConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    langfuse: LangfuseSettings
    circuit_breaker: CircuitBreakerSettings
    configuration_hash: str
