from __future__ import annotations

from dataclasses import dataclass

import httpx

from pff_fa_ai.agents.affiliation.resume_context import AffiliationResumeContextStore
from pff_fa_ai.configuration.loader import (
    CONFIG_ROOT,
    load_agents_configuration,
    load_integration_configuration,
    load_portal_link_configuration,
)
from pff_fa_ai.configuration.models import AffiliationAgentSettings, Environment
from pff_fa_ai.configuration.secrets import SecretResolver, secret_resolver_for_environment
from pff_fa_ai.domain.workflow.repository import WorkflowRepository
from pff_fa_ai.guardrails.pipeline import GuardrailPipeline
from pff_fa_ai.integration.api.catalog import load_api_catalog
from pff_fa_ai.integration.api.client import HttpxEnterpriseHttpClient
from pff_fa_ai.integration.execution.concurrency import ConcurrencyLimiter
from pff_fa_ai.integration.tools.executor import ToolExecutor
from pff_fa_ai.integration.tools.registry import load_tool_registry
from pff_fa_ai.portal_links.catalog import load_portal_catalog
from pff_fa_ai.portal_links.resolver import PortalLinkResolver


@dataclass
class AffiliationDependencies:
    """Everything `AffiliationAgent` needs, constructed once per app lifetime
    (`build_affiliation_dependencies`) and reused across requests — mirrors
    `api.dependencies.AppState`'s "build once, inject everywhere" pattern."""

    tool_executor: ToolExecutor
    workflow_repository: WorkflowRepository
    portal_resolver: PortalLinkResolver
    guardrails: GuardrailPipeline
    settings: AffiliationAgentSettings
    http_client: httpx.AsyncClient
    resume_context_store: AffiliationResumeContextStore


def build_affiliation_dependencies(
    *,
    environment: Environment,
    workflow_repository: WorkflowRepository,
    guardrails: GuardrailPipeline | None = None,
    secret_resolver: SecretResolver | None = None,
) -> AffiliationDependencies:
    # ADR-D5-07 / ADR-D5-20: a deployed runtime resolves every `*_secret_ref` from Key Vault
    # via the SPN; local dev may use the process environment. Built once and threaded into
    # every config load so secrets come from a single, policy-selected source.
    resolver = secret_resolver or secret_resolver_for_environment(environment)

    agents_config = load_agents_configuration(environment, secret_resolver=resolver)
    integration_config = load_integration_configuration(environment, secret_resolver=resolver)
    portal_link_config = load_portal_link_configuration(environment, secret_resolver=resolver)

    api_catalog = load_api_catalog(
        CONFIG_ROOT / "enterprise" / "api-catalog", secret_resolver=resolver
    )
    tool_registry = load_tool_registry(
        CONFIG_ROOT / "enterprise" / "tool-registry",
        catalog=api_catalog,
        secret_resolver=resolver,
    )
    portal_registry = load_portal_catalog()

    http_client = httpx.AsyncClient(base_url=agents_config.affiliation.enterprise_base_url)
    tool_executor = ToolExecutor(
        tool_registry=tool_registry,
        api_catalog=api_catalog,
        http_client=HttpxEnterpriseHttpClient(http_client),
        retry_settings=integration_config.retry,
        circuit_breaker_settings=integration_config.circuit_breaker,
        concurrency_limiter=ConcurrencyLimiter(integration_config.concurrency),
    )
    portal_resolver = PortalLinkResolver(
        portal_registry,
        environment=environment,
        allowed_domains=frozenset(portal_link_config.link_policy.allowed_domains),
    )

    return AffiliationDependencies(
        tool_executor=tool_executor,
        workflow_repository=workflow_repository,
        portal_resolver=portal_resolver,
        guardrails=guardrails or GuardrailPipeline(),
        settings=agents_config.affiliation,
        http_client=http_client,
        resume_context_store=AffiliationResumeContextStore(),
    )
