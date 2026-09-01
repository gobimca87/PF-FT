"""Shared test helpers for the affiliation agent test suite — not collected as tests
itself (no `test_` prefix), matching `tests/mocks/enterprise_api.py`'s pattern."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from pff_fa_ai.agents.affiliation.dependencies import AffiliationDependencies
from pff_fa_ai.agents.affiliation.resume_context import AffiliationResumeContextStore
from pff_fa_ai.agents.context import AgentExecutionContext
from pff_fa_ai.common.claims import ClaimsContext
from pff_fa_ai.common.correlation import CorrelationContext, new_id
from pff_fa_ai.configuration.loader import (
    CONFIG_ROOT,
    load_agents_configuration,
    load_integration_configuration,
    load_portal_link_configuration,
)
from pff_fa_ai.configuration.models import Environment
from pff_fa_ai.domain.workflow.repository import WorkflowRepository
from pff_fa_ai.guardrails.pipeline import GuardrailPipeline
from pff_fa_ai.infrastructure.persistence import InMemoryWorkflowRepository
from pff_fa_ai.integration.api.catalog import load_api_catalog
from pff_fa_ai.integration.api.client import HttpxEnterpriseHttpClient
from pff_fa_ai.integration.execution.concurrency import ConcurrencyLimiter
from pff_fa_ai.integration.tools.executor import ToolExecutor
from pff_fa_ai.integration.tools.registry import load_tool_registry
from pff_fa_ai.portal_links.catalog import load_portal_catalog
from pff_fa_ai.portal_links.resolver import PortalLinkResolver

RequestHandler = Callable[[httpx.Request], httpx.Response]

CLUB_ID = "club-1"
APPLICATION_ID = "app-1"


def build_test_dependencies(
    handler: RequestHandler,
    *,
    environment: Environment = "dev",
    workflow_repository: WorkflowRepository | None = None,
) -> AffiliationDependencies:
    """Builds real `AffiliationDependencies` against the real repo config (same
    "real config repository" pattern used throughout this project's config-loader
    tests), with the enterprise HTTP client backed by an `httpx.MockTransport`."""
    agents_config = load_agents_configuration(environment)
    integration_config = load_integration_configuration(environment)
    portal_link_config = load_portal_link_configuration(environment)
    api_catalog = load_api_catalog(CONFIG_ROOT / "enterprise" / "api-catalog")
    tool_registry = load_tool_registry(
        CONFIG_ROOT / "enterprise" / "tool-registry", catalog=api_catalog
    )
    portal_registry = load_portal_catalog()

    http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://enterprise.example"
    )
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
        workflow_repository=workflow_repository or InMemoryWorkflowRepository(),
        portal_resolver=portal_resolver,
        guardrails=GuardrailPipeline(),
        settings=agents_config.affiliation,
        http_client=http_client,
        resume_context_store=AffiliationResumeContextStore(),
    )


def make_context(
    *,
    workflow_instance_id: str | None = None,
    club_id: str = CLUB_ID,
    user_message: str = "What's my affiliation status?",
    subject: str = "user-1",
) -> AgentExecutionContext:
    return AgentExecutionContext(
        conversation_id="conv-1",
        session_id="sess-1",
        workflow_instance_id=workflow_instance_id or new_id("wf"),
        agent_run_id=new_id("run"),
        claims=ClaimsContext(
            subject=subject, organization=club_id, permissions=("affiliation.read",)
        ),
        user_message=user_message,
        correlation=CorrelationContext(request_id=new_id("req"), correlation_id=new_id("corr")),
    )


def enterprise_response_handler(
    *,
    application_status: str = "COMPLETE",
    total_fee: float = 150.0,
    invoice_number: str | None = None,
    payment_status: str = "AWAITING_PAYMENT",
    rejection_reason: str | None = None,
    cancellation_reason: str | None = None,
    team_count: int = 2,
    official_count: int = 1,
    not_found_paths: frozenset[str] = frozenset(),
) -> RequestHandler:
    """Builds a deterministic `httpx.MockTransport` handler covering all 7 affiliation
    tools, parameterized by application status so each test scenario just changes a
    keyword argument rather than rewriting the whole handler."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path in not_found_paths:
            return httpx.Response(404, json={"error": "not found"})
        if path.endswith(f"/clubs/{CLUB_ID}"):
            return httpx.Response(
                200,
                json={
                    "club_id": CLUB_ID,
                    "name": "Testville FC",
                    "county": "Testshire",
                    "status": "ACTIVE",
                },
            )
        if path.endswith("/affiliation-application"):
            body: dict[str, Any] = {
                "application_id": APPLICATION_ID,
                "club_id": CLUB_ID,
                "season": "2026-27",
                "status": application_status,
                "total_fee": total_fee,
                "currency": "GBP",
                "invoice_number": invoice_number,
                "rejection_reason": rejection_reason,
                "cancellation_reason": cancellation_reason,
            }
            return httpx.Response(200, json=body)
        if path.endswith("/teams"):
            items = [
                {
                    "team_id": f"team-{i}",
                    "name": f"Team {i}",
                    "age_group": "U10",
                    "affiliated": application_status == "COMPLETE",
                }
                for i in range(1, team_count + 1)
            ]
            return httpx.Response(200, json={"total": team_count, "items": items})
        if path.endswith("/officials"):
            items = [
                {
                    "official_id": f"off-{i}",
                    "name": f"Official {i}",
                    "role": "Welfare Officer",
                    "safeguarding_status": "VALID",
                    "suspended": False,
                }
                for i in range(1, official_count + 1)
            ]
            return httpx.Response(200, json={"total": official_count, "items": items})
        if path.endswith("/insurance"):
            return httpx.Response(
                200,
                json={
                    "club_id": CLUB_ID,
                    "public_liability_status": "ACTIVE",
                    "personal_accident_status": "ACTIVE",
                },
            )
        if path.endswith("/products"):
            return httpx.Response(200, json={"total": 0, "items": []})
        if "/payment-status" in path:
            return httpx.Response(
                200,
                json={
                    "application_id": APPLICATION_ID,
                    "invoice_number": invoice_number,
                    "status": payment_status,
                    "amount": total_fee,
                },
            )
        return httpx.Response(404, json={"error": "not found"})

    return handler
