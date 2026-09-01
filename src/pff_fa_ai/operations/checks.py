from __future__ import annotations

import httpx

from pff_fa_ai.engineering_agents.agents.architecture_compliance_agent import (
    ArchitectureComplianceAgent,
)
from pff_fa_ai.engineering_agents.agents.configuration_agent import ConfigurationValidationAgent
from pff_fa_ai.engineering_agents.agents.dependency_agent import DependencyVulnerabilityAgent
from pff_fa_ai.engineering_agents.models import EngineeringAgentResult, Finding
from pff_fa_ai.engineering_agents.states import AgentResultStatus, FindingSeverity

_AGENT_VERSION = "1.0.0"
_PLATFORM_HEALTH_CHECK_ID = "platform-health"


async def configuration_check() -> EngineeringAgentResult:
    """doc 28 §135 daily checklist "Platform health" — real config/ validity, the same
    check Phase 18's `ConfigurationValidationAgent` runs on every PR, run again on a
    schedule so config that only degrades over time (e.g. a secret reference silently
    stops resolving) is still caught between deployments."""
    return await ConfigurationValidationAgent().run()


async def architecture_check() -> EngineeringAgentResult:
    """doc 28 §137 monthly checklist "Runbook review" / architecture-drift detection
    (doc 23 §97-98) — the domain-layering boundary re-checked on a schedule."""
    return await ArchitectureComplianceAgent().run()


async def dependency_check(*, pip_audit_json_output: str) -> EngineeringAgentResult:
    """doc 28 §136 weekly checklist "Vulnerability status" — a new CVE can appear for
    an already-approved dependency at any time, independent of any PR."""
    return await DependencyVulnerabilityAgent(pip_audit_json_output=pip_audit_json_output).run()


async def platform_health_check(
    *, base_url: str | None, transport: httpx.AsyncBaseTransport | None = None
) -> EngineeringAgentResult:
    """doc 28 §135 daily checklist "Platform health" / doc 28 §30 "Platform Health
    Checklist" — a real HTTP call against the deployed `/api/v1/health` endpoint when a
    URL is configured. No environment is deployed by this phase (Phase 19's IaC/
    manifest decision is still deferred), so `base_url=None` reports SKIPPED rather
    than a fabricated PASS — an honest "not applicable yet", not a fake result.
    `transport` is test-only dependency injection (e.g. `httpx.MockTransport`); real
    callers never set it, leaving httpx to make an actual network call."""
    if base_url is None:
        return EngineeringAgentResult(
            agent_id=_PLATFORM_HEALTH_CHECK_ID,
            agent_version=_AGENT_VERSION,
            status=AgentResultStatus.SKIPPED,
        )

    try:
        async with httpx.AsyncClient(
            base_url=base_url, timeout=10.0, transport=transport
        ) as client:
            response = await client.get("/api/v1/health")
    except httpx.HTTPError as exc:
        return EngineeringAgentResult(
            agent_id=_PLATFORM_HEALTH_CHECK_ID,
            agent_version=_AGENT_VERSION,
            status=AgentResultStatus.ERROR,
            findings=(
                Finding(
                    finding_id="platform-health-unreachable",
                    agent_id=_PLATFORM_HEALTH_CHECK_ID,
                    severity=FindingSeverity.CRITICAL,
                    description=f"Health endpoint unreachable: {exc}",
                ),
            ),
        )

    if response.status_code != 200:
        return EngineeringAgentResult(
            agent_id=_PLATFORM_HEALTH_CHECK_ID,
            agent_version=_AGENT_VERSION,
            status=AgentResultStatus.FAIL,
            findings=(
                Finding(
                    finding_id="platform-health-non-200",
                    agent_id=_PLATFORM_HEALTH_CHECK_ID,
                    severity=FindingSeverity.CRITICAL,
                    description=f"Health endpoint returned HTTP {response.status_code}",
                ),
            ),
        )

    return EngineeringAgentResult(
        agent_id=_PLATFORM_HEALTH_CHECK_ID,
        agent_version=_AGENT_VERSION,
        status=AgentResultStatus.PASS,
    )
