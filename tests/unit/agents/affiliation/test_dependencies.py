from pff_fa_ai.agents.affiliation.dependencies import build_affiliation_dependencies
from pff_fa_ai.configuration.loader import load_memory_configuration
from pff_fa_ai.infrastructure.persistence import InMemoryMemoryStore, InMemoryWorkflowRepository
from pff_fa_ai.memory import MemoryService


async def test_build_affiliation_dependencies_should_construct_against_the_real_config() -> None:
    deps = build_affiliation_dependencies(
        environment="dev",
        workflow_repository=InMemoryWorkflowRepository(),
        memory_service=MemoryService(
            InMemoryMemoryStore(), load_memory_configuration("dev").memory
        ),
    )

    try:
        assert deps.settings.enterprise_base_url
        assert deps.settings.team_official_batch_size == 20
        assert deps.tool_executor is not None
        assert deps.portal_resolver is not None
    finally:
        await deps.http_client.aclose()
