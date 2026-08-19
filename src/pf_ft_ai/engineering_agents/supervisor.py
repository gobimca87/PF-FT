from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Mapping

from pf_ft_ai.common.correlation import new_id
from pf_ft_ai.engineering_agents.models import EngineeringAgentResult, EngineeringRun
from pf_ft_ai.engineering_agents.registry import EngineeringAgentRegistry
from pf_ft_ai.engineering_agents.states import (
    AgentLifecycleStatus,
    AgentResultStatus,
    ChangedComponent,
)

AgentRunner = Callable[[], Awaitable[EngineeringAgentResult]]

# doc 23 §9's worked examples, extended with the direct 1:1 mappings doc 23 §5's
# category list implies. Anything not listed here still gets the baseline
# security/unit-test pair, since those two are relevant to any code change.
_IMPACT_AGENT_MAP: dict[ChangedComponent, tuple[str, ...]] = {
    ChangedComponent.PROMPTS: (
        "prompt-review",
        "ai-evaluation",
        "regression",
        "guardrail-validation",
    ),
    ChangedComponent.RAG: (
        "rag-validation",
        "embedding-vector-validation",
        "ai-evaluation",
        "regression",
    ),
    ChangedComponent.EMBEDDINGS: ("embedding-vector-validation", "ai-evaluation", "regression"),
    ChangedComponent.VECTOR: ("embedding-vector-validation", "ai-evaluation", "regression"),
    ChangedComponent.TOOLS: ("api-contract", "security-scan", "unit-test", "ai-evaluation"),
    ChangedComponent.MCP: ("api-contract", "security-scan", "unit-test"),
    ChangedComponent.MODELS: ("model-validation", "ai-evaluation", "regression"),
    ChangedComponent.SLM_CONFIGURATION: ("model-validation", "ai-evaluation", "regression"),
    ChangedComponent.GUARDRAILS: ("guardrail-validation", "security-scan", "ai-evaluation"),
    ChangedComponent.CONFIGURATION: ("configuration", "security-scan"),
    ChangedComponent.INFRASTRUCTURE: ("configuration", "security-scan"),
    ChangedComponent.AGENTS: ("code-review", "unit-test", "ai-evaluation", "regression"),
    ChangedComponent.LANGGRAPH: ("code-review", "unit-test", "architecture-compliance"),
    ChangedComponent.FASTAPI: ("code-review", "unit-test", "api-contract"),
    ChangedComponent.SERVICE_BUS: ("unit-test", "security-scan"),
    ChangedComponent.ERC: ("unit-test", "architecture-compliance"),
    ChangedComponent.MEMORY: ("unit-test", "security-scan"),
    ChangedComponent.CACHE: ("unit-test", "security-scan"),
    ChangedComponent.TESTS: ("unit-test",),
    ChangedComponent.DOCUMENTATION: ("documentation",),
    ChangedComponent.PYTHON_CODE: ("code-review", "unit-test", "architecture-compliance"),
}

_BASELINE_AGENTS: tuple[str, ...] = ("security-scan", "unit-test")


def select_agents_for_changes(changed_components: Iterable[ChangedComponent]) -> tuple[str, ...]:
    """doc 23 §8-9 impact-based agent selection. Order is preserved (first-seen wins)
    so callers get deterministic, reviewable agent-run ordering."""
    selected: list[str] = []
    for component in changed_components:
        for agent_id in _IMPACT_AGENT_MAP.get(component, _BASELINE_AGENTS):
            if agent_id not in selected:
                selected.append(agent_id)
    return tuple(selected)


class EngineeringAgentSupervisor:
    """doc 23 §6-7. Independent agents run in parallel (doc 23 §53) via
    `asyncio.gather`; the fuller dependency-graph sequencing doc 23 §54/§112-114
    describes (e.g. Test Generation → Unit Tests → Coverage) is not built — no
    generation agent exists yet to produce that first stage (see README.md's
    Engineering Agents section)."""

    def __init__(self, registry: EngineeringAgentRegistry) -> None:
        self._registry = registry

    def select_agents(self, changed_components: Iterable[ChangedComponent]) -> tuple[str, ...]:
        candidates = select_agents_for_changes(changed_components)
        return tuple(
            agent_id
            for agent_id in candidates
            if (definition := self._registry.get(agent_id)) is not None
            and definition.lifecycle_status is AgentLifecycleStatus.ACTIVE
        )

    async def run(
        self,
        *,
        repository: str,
        commit: str,
        pull_request: str | None = None,
        changed_components: Iterable[ChangedComponent],
        agent_runners: Mapping[str, AgentRunner],
    ) -> EngineeringRun:
        changed = tuple(changed_components)
        selected = self.select_agents(changed)

        async def run_one(agent_id: str) -> EngineeringAgentResult:
            runner = agent_runners.get(agent_id)
            if runner is None:
                definition = self._registry.get(agent_id)
                return EngineeringAgentResult(
                    agent_id=agent_id,
                    agent_version=definition.version if definition else "unknown",
                    status=AgentResultStatus.SKIPPED,
                )
            return await runner()

        results = tuple(await asyncio.gather(*(run_one(agent_id) for agent_id in selected)))
        return EngineeringRun(
            run_id=new_id("eng-run"),
            repository=repository,
            commit=commit,
            pull_request=pull_request,
            changed_components=changed,
            agent_ids=selected,
            results=results,
        )
