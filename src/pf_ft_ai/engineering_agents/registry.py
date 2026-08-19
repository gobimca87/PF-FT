from __future__ import annotations

from pf_ft_ai.common.exceptions import ConfigurationError
from pf_ft_ai.engineering_agents.models import EngineeringAgentDefinition
from pf_ft_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    EngineeringAgentRisk,
    ExecutionMode,
    PermissionLevel,
)


class EngineeringAgentRegistry:
    """doc 23 §82. Duplicate `agent_id` registration is rejected — silently overwriting
    a governed agent's definition would break the auditability doc 23 §95 requires."""

    def __init__(self) -> None:
        self._definitions: dict[str, EngineeringAgentDefinition] = {}

    def register(self, definition: EngineeringAgentDefinition) -> None:
        if definition.agent_id in self._definitions:
            raise ConfigurationError(
                f"Duplicate engineering agent registered: {definition.agent_id}"
            )
        self._definitions[definition.agent_id] = definition

    def get(self, agent_id: str) -> EngineeringAgentDefinition | None:
        return self._definitions.get(agent_id)

    def active(self) -> tuple[EngineeringAgentDefinition, ...]:
        return tuple(
            definition
            for definition in self._definitions.values()
            if definition.lifecycle_status is AgentLifecycleStatus.ACTIVE
        )

    def all_definitions(self) -> tuple[EngineeringAgentDefinition, ...]:
        return tuple(self._definitions.values())


# doc 23 §5/§111: the five agents this phase gives a real, deterministic implementation
# to (no model required — see each agent module's docstring). The remaining catalog
# entries doc 23 lists require semantic judgment an approved LLM would provide, and no
# engineering-agent model has been evaluation-selected yet (same "mock provider until
# approved" posture as the SLM/embedding/judge model defaults elsewhere in this
# platform) — they're registered as PROPOSED so the catalog is complete and auditable,
# but the supervisor never selects a non-ACTIVE agent to run.
_REAL_AGENTS: tuple[tuple[str, str], ...] = (
    ("configuration", "Validate config/ YAML syntax and scan for hardcoded secrets"),
    ("architecture-compliance", "Enforce CLAUDE.md's domain-layer import boundary"),
    ("security-scan", "Parse ruff --select S findings into the standard result contract"),
    ("dependency", "Parse pip-audit findings into the standard result contract"),
    ("unit-test", "Report pytest pass/fail/coverage results (does not generate tests)"),
)

_PROPOSED_AGENTS: tuple[tuple[str, str], ...] = (
    ("code-review", "Semantic code quality/architecture/security review"),
    ("prompt-review", "Prompt structure, injection-resistance, and instruction-hierarchy review"),
    ("ai-evaluation", "Orchestrate golden-dataset evaluation for a change"),
    ("test-generation", "Generate missing unit/integration/security tests"),
    ("documentation", "Update generated documentation for a change"),
    ("api-contract", "Diff enterprise/API contracts for breaking changes"),
    ("rag-validation", "Validate RAG source/chunking/ACL/retrieval behavior"),
    ("embedding-vector-validation", "Validate embedding/vector-store compatibility"),
    ("model-validation", "Validate SLM registry/version/compatibility"),
    ("guardrail-validation", "Run guardrail regression against known safe/attack cases"),
    ("observability-validation", "Validate telemetry does not leak sensitive values"),
    ("regression", "Run AI/prompt/guardrail regression suites for a change"),
)


def build_default_registry() -> EngineeringAgentRegistry:
    registry = EngineeringAgentRegistry()
    for agent_id, purpose in _REAL_AGENTS:
        registry.register(
            EngineeringAgentDefinition(
                agent_id=agent_id,
                version="1.0.0",
                purpose=purpose,
                owner="platform-engineering",
                risk=EngineeringAgentRisk.LOW,
                permission_level=PermissionLevel.LEVEL_1_REPORT,
                execution_mode=ExecutionMode.VALIDATE,
                lifecycle_status=AgentLifecycleStatus.ACTIVE,
            )
        )
    for agent_id, purpose in _PROPOSED_AGENTS:
        registry.register(
            EngineeringAgentDefinition(
                agent_id=agent_id,
                version="0.0.0",
                purpose=purpose,
                owner="platform-engineering",
                risk=EngineeringAgentRisk.MEDIUM,
                permission_level=PermissionLevel.LEVEL_0_READ_ONLY,
                execution_mode=ExecutionMode.READ_ONLY,
                lifecycle_status=AgentLifecycleStatus.PROPOSED,
            )
        )
    return registry
