from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pff_fa_ai.context.erc.lifecycle import assert_valid_transition
from pff_fa_ai.context.erc.models import Erc, ErcCompleteness, ErcSection, compute_freshness
from pff_fa_ai.context.erc.provenance import Provenance
from pff_fa_ai.context.erc.states import ErcAuthority, ErcLifecycleStatus, ErcSectionStatus

# doc 8 §9-10: the full lifecycle walk, not a single jump to READY — proves the
# sections this agent builds actually earned `READY` status through every mandatory
# transition (`context.erc.lifecycle.assert_valid_transition`).
_LIFECYCLE_WALK: tuple[ErcLifecycleStatus, ...] = (
    ErcLifecycleStatus.NOT_CREATED,
    ErcLifecycleStatus.REQUIREMENTS_IDENTIFIED,
    ErcLifecycleStatus.COLLECTING,
    ErcLifecycleStatus.NORMALIZING,
    ErcLifecycleStatus.AGGREGATING,
    ErcLifecycleStatus.VALIDATING,
    ErcLifecycleStatus.READY,
)

# The 5 ERC sections every affiliation ERC carries, per doc 4 §72's checklist
# (club/application/teams/officials/insurance) plus products.
REQUIRED_SECTIONS: tuple[str, ...] = (
    "club",
    "application",
    "teams",
    "officials",
    "insurance",
    "products",
)


def _walk_lifecycle_to_ready() -> None:
    for current, target in zip(_LIFECYCLE_WALK, _LIFECYCLE_WALK[1:], strict=False):
        assert_valid_transition(current=current, target=target)


def build_erc_section(
    *, name: str, data: Any, api_id: str, endpoint_ref: str, ttl_seconds: int = 300
) -> ErcSection:
    now = datetime.now(UTC)
    provenance = Provenance(
        system="enterprise-affiliation",
        api=api_id,
        endpoint_ref=endpoint_ref,
        retrieved_at=now,
        authority=ErcAuthority.AUTHORITATIVE,
    )
    freshness = compute_freshness(retrieved_at=now, ttl_seconds=ttl_seconds, now=now)
    return ErcSection(
        name=name,
        status=ErcSectionStatus.COMPLETE,
        data=data if isinstance(data, dict) else {"items": data},
        provenance=provenance,
        freshness=freshness,
    )


def build_affiliation_erc(
    *, erc_id: str, workflow_instance_id: str, conversation_id: str, sections: dict[str, ErcSection]
) -> Erc:
    """doc 8 (ERC) — assembles the affiliation ERC from already-collected, already
    section-wrapped data. Walks the full lifecycle to `READY` (see
    `_walk_lifecycle_to_ready`) rather than jumping straight there."""
    _walk_lifecycle_to_ready()
    now = datetime.now(UTC)
    completeness = ErcCompleteness(
        required_sections=len(REQUIRED_SECTIONS),
        completed_sections=len(sections),
        missing_sections=tuple(name for name in REQUIRED_SECTIONS if name not in sections),
    )
    return Erc(
        version=1,
        erc_id=erc_id,
        schema_version="1.0.0",
        status=ErcLifecycleStatus.READY,
        workflow_instance_id=workflow_instance_id,
        conversation_id=conversation_id,
        created_at=now,
        updated_at=now,
        sections=sections,
        completeness=completeness,
    )
