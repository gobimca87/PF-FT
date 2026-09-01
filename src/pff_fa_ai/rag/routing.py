from __future__ import annotations

from pff_fa_ai.rag.states import InformationRequirement, RetrievalRoute

# Doc 13 §5: CURRENT_* → Enterprise API (never RAG); reference/policy/documentary/
# historical/procedural knowledge → RAG. Mixed questions are the caller's responsibility
# to decompose (doc 13 §59) — this only classifies a single, already-decomposed requirement.
_ROUTE_MAP: dict[InformationRequirement, RetrievalRoute] = {
    InformationRequirement.CURRENT_TRANSACTIONAL: RetrievalRoute.ENTERPRISE_API,
    InformationRequirement.CURRENT_AUTHORITATIVE: RetrievalRoute.ENTERPRISE_API,
    InformationRequirement.REFERENCE_KNOWLEDGE: RetrievalRoute.RAG,
    InformationRequirement.POLICY: RetrievalRoute.RAG,
    InformationRequirement.DOCUMENTARY: RetrievalRoute.RAG,
    InformationRequirement.HISTORICAL: RetrievalRoute.RAG,
    InformationRequirement.PROCEDURAL: RetrievalRoute.RAG,
}


def route_information_requirement(requirement: InformationRequirement) -> RetrievalRoute:
    return _ROUTE_MAP[requirement]
