import pytest

from pff_fa_ai.rag.routing import route_information_requirement
from pff_fa_ai.rag.states import InformationRequirement, RetrievalRoute


@pytest.mark.parametrize(
    "requirement",
    [InformationRequirement.CURRENT_TRANSACTIONAL, InformationRequirement.CURRENT_AUTHORITATIVE],
)
def test_should_route_current_state_questions_to_enterprise_api(
    requirement: InformationRequirement,
) -> None:
    assert route_information_requirement(requirement) is RetrievalRoute.ENTERPRISE_API


@pytest.mark.parametrize(
    "requirement",
    [
        InformationRequirement.REFERENCE_KNOWLEDGE,
        InformationRequirement.POLICY,
        InformationRequirement.DOCUMENTARY,
        InformationRequirement.HISTORICAL,
        InformationRequirement.PROCEDURAL,
    ],
)
def test_should_route_knowledge_questions_to_rag(requirement: InformationRequirement) -> None:
    assert route_information_requirement(requirement) is RetrievalRoute.RAG
