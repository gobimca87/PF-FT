from pff_fa_ai.agents.affiliation.dependencies import build_affiliation_dependencies
from pff_fa_ai.infrastructure.persistence import InMemoryWorkflowRepository


async def test_build_affiliation_dependencies_should_construct_against_the_real_config() -> None:
    deps = build_affiliation_dependencies(
        environment="dev", workflow_repository=InMemoryWorkflowRepository()
    )

    try:
        assert deps.settings.enterprise_base_url
        assert deps.settings.team_official_batch_size == 20
        assert deps.tool_executor is not None
        assert deps.portal_resolver is not None
    finally:
        await deps.http_client.aclose()
