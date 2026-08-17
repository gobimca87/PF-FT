from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.common.validation import format_validation_error
from pf_ft_ai.configuration.hashing import compute_configuration_hash
from pf_ft_ai.configuration.models import (
    ALLOWED_ENVIRONMENTS,
    AgenticRagSettings,
    BatchingConfiguration,
    BatchingSettings,
    CacheConfiguration,
    CacheSettings,
    ChunkingSettings,
    CircuitBreakerSettings,
    ConcurrencySettings,
    ConfigurationMetadata,
    ContextBudgetConfiguration,
    ContextBudgetSettings,
    ConversationConfiguration,
    ConversationSecuritySettings,
    ConversationSettings,
    EmbeddingConfiguration,
    EmbeddingSettings,
    Environment,
    EnvironmentIdentity,
    ErcConfiguration,
    ErcSettings,
    HarnessConfiguration,
    HarnessLimits,
    IntegrationConfiguration,
    MemoryConfiguration,
    MemorySettings,
    PlatformConfiguration,
    RagConfiguration,
    RedisConfiguration,
    RedisConnectionSettings,
    RerankingSettings,
    RetrievalSettings,
    RetrySettings,
    RuntimeConfig,
    SessionSettings,
    SlmConfiguration,
    SlmSettings,
    TimeoutSettings,
    WorkflowSettings,
)
from pf_ft_ai.configuration.secrets import EnvVarSecretResolver, SecretResolver

CONFIG_ROOT = Path(__file__).resolve().parents[3] / "config"
_SECRET_REF_SUFFIX = "_secret_ref"  # noqa: S105 -- key-name suffix, not a credential


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigurationError(f"Missing required configuration file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        content = yaml.safe_load(handle)
    if content is None:
        return {}
    if not isinstance(content, dict):
        raise ConfigurationError(f"Configuration file must contain a YAML mapping: {path}")
    return content


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        existing = merged.get(key)
        if isinstance(existing, Mapping) and isinstance(value, Mapping):
            merged[key] = _deep_merge(existing, value)
        else:
            merged[key] = value
    return merged


def resolve_secret_refs(value: Any, resolver: SecretResolver) -> Any:
    if isinstance(value, dict):
        resolved: dict[str, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and key.endswith(_SECRET_REF_SUFFIX) and isinstance(item, str):
                target_key = key[: -len(_SECRET_REF_SUFFIX)]
                resolved[target_key] = resolver.resolve(item)
            else:
                resolved[key] = resolve_secret_refs(item, resolver)
        return resolved
    if isinstance(value, list):
        return [resolve_secret_refs(item, resolver) for item in value]
    return value


def _load_merged_config(
    *, filename: str, environment: Environment, config_root: Path | None
) -> dict[str, Any]:
    if environment not in ALLOWED_ENVIRONMENTS:
        raise ConfigurationError(
            f"Unknown environment '{environment}'; expected one of {ALLOWED_ENVIRONMENTS}"
        )

    root = config_root or CONFIG_ROOT
    base = _load_yaml_mapping(root / "base" / filename)
    overrides = _load_yaml_mapping(root / "environments" / environment / filename)
    return _deep_merge(base, overrides)


def load_platform_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> PlatformConfiguration:
    merged = _load_merged_config(
        filename="platform.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        metadata = ConfigurationMetadata.model_validate(resolved["configuration"])
        identity = EnvironmentIdentity.model_validate(resolved["environment"])
        runtime = RuntimeConfig.model_validate(resolved["runtime"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid platform configuration: {format_validation_error(exc)}"
        ) from exc

    if identity.name != environment:
        raise ConfigurationError(
            f"environment.name '{identity.name}' does not match requested environment "
            f"'{environment}'"
        )

    # doc 17 §100: hash the pre-resolution config so secret rotation never looks like drift.
    return PlatformConfiguration(
        metadata=metadata,
        environment=identity,
        runtime=runtime,
        configuration_hash=compute_configuration_hash(merged),
    )


def load_conversation_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> ConversationConfiguration:
    merged = _load_merged_config(
        filename="conversation.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        conversation = ConversationSettings.model_validate(resolved["conversation"])
        session = SessionSettings.model_validate(resolved["session"])
        security = ConversationSecuritySettings.model_validate(resolved["security"])
        workflow = WorkflowSettings.model_validate(resolved["workflow"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid conversation configuration: {format_validation_error(exc)}"
        ) from exc

    return ConversationConfiguration(
        conversation=conversation,
        session=session,
        security=security,
        workflow=workflow,
        configuration_hash=compute_configuration_hash(merged),
    )


def load_harness_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> HarnessConfiguration:
    merged = _load_merged_config(
        filename="harness.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        harness = HarnessLimits.model_validate(resolved["harness"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid harness configuration: {format_validation_error(exc)}"
        ) from exc

    return HarnessConfiguration(
        harness=harness, configuration_hash=compute_configuration_hash(merged)
    )


def load_erc_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> ErcConfiguration:
    merged = _load_merged_config(
        filename="erc.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        erc = ErcSettings.model_validate(resolved["erc"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid erc configuration: {format_validation_error(exc)}"
        ) from exc

    return ErcConfiguration(erc=erc, configuration_hash=compute_configuration_hash(merged))


def load_batching_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> BatchingConfiguration:
    merged = _load_merged_config(
        filename="batching.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        batching = BatchingSettings.model_validate(resolved["batching"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid batching configuration: {format_validation_error(exc)}"
        ) from exc

    return BatchingConfiguration(
        batching=batching, configuration_hash=compute_configuration_hash(merged)
    )


def load_context_budget_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> ContextBudgetConfiguration:
    merged = _load_merged_config(
        filename="context-budget.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        context_budget = ContextBudgetSettings.model_validate(resolved["context_budget"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid context budget configuration: {format_validation_error(exc)}"
        ) from exc

    return ContextBudgetConfiguration(
        context_budget=context_budget, configuration_hash=compute_configuration_hash(merged)
    )


def load_integration_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> IntegrationConfiguration:
    merged = _load_merged_config(
        filename="integration.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        retry = RetrySettings.model_validate(resolved["retry"])
        circuit_breaker = CircuitBreakerSettings.model_validate(resolved["circuit_breaker"])
        concurrency = ConcurrencySettings.model_validate(resolved["concurrency"])
        timeout = TimeoutSettings.model_validate(resolved["timeout"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid integration configuration: {format_validation_error(exc)}"
        ) from exc

    return IntegrationConfiguration(
        retry=retry,
        circuit_breaker=circuit_breaker,
        concurrency=concurrency,
        timeout=timeout,
        configuration_hash=compute_configuration_hash(merged),
    )


def load_redis_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> RedisConfiguration:
    merged = _load_merged_config(
        filename="redis.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        redis_settings = RedisConnectionSettings.model_validate(resolved["redis"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid redis configuration: {format_validation_error(exc)}"
        ) from exc

    return RedisConfiguration(
        redis=redis_settings, configuration_hash=compute_configuration_hash(merged)
    )


def load_memory_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> MemoryConfiguration:
    merged = _load_merged_config(
        filename="memory.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        memory = MemorySettings.model_validate(resolved["memory"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid memory configuration: {format_validation_error(exc)}"
        ) from exc

    return MemoryConfiguration(memory=memory, configuration_hash=compute_configuration_hash(merged))


def load_cache_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> CacheConfiguration:
    merged = _load_merged_config(
        filename="cache.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        cache = CacheSettings.model_validate(resolved["cache"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid cache configuration: {format_validation_error(exc)}"
        ) from exc

    return CacheConfiguration(cache=cache, configuration_hash=compute_configuration_hash(merged))


def load_rag_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> RagConfiguration:
    merged = _load_merged_config(
        filename="rag.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        chunking = ChunkingSettings.model_validate(resolved["chunking"])
        retrieval = RetrievalSettings.model_validate(resolved["retrieval"])
        reranking = RerankingSettings.model_validate(resolved["reranking"])
        agentic_rag = AgenticRagSettings.model_validate(resolved["agentic_rag"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid rag configuration: {format_validation_error(exc)}"
        ) from exc

    return RagConfiguration(
        chunking=chunking,
        retrieval=retrieval,
        reranking=reranking,
        agentic_rag=agentic_rag,
        configuration_hash=compute_configuration_hash(merged),
    )


def load_embedding_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> EmbeddingConfiguration:
    merged = _load_merged_config(
        filename="embedding.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        embedding = EmbeddingSettings.model_validate(resolved["embedding"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid embedding configuration: {format_validation_error(exc)}"
        ) from exc

    return EmbeddingConfiguration(
        embedding=embedding, configuration_hash=compute_configuration_hash(merged)
    )


def load_slm_configuration(
    environment: Environment,
    *,
    config_root: Path | None = None,
    secret_resolver: SecretResolver | None = None,
) -> SlmConfiguration:
    merged = _load_merged_config(
        filename="slm.yaml", environment=environment, config_root=config_root
    )
    resolved = resolve_secret_refs(merged, secret_resolver or EnvVarSecretResolver())

    try:
        slm = SlmSettings.model_validate(resolved["slm"])
        retry = RetrySettings.model_validate(resolved["retry"])
        circuit_breaker = CircuitBreakerSettings.model_validate(resolved["circuit_breaker"])
    except KeyError as exc:
        raise ConfigurationError(f"Missing required configuration section: {exc}") from exc
    except PydanticValidationError as exc:
        raise ConfigurationError(
            f"Invalid slm configuration: {format_validation_error(exc)}"
        ) from exc

    return SlmConfiguration(
        slm=slm,
        retry=retry,
        circuit_breaker=circuit_breaker,
        configuration_hash=compute_configuration_hash(merged),
    )
