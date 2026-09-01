from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from pff_fa_ai.context.erc.models import Erc, ErcSection, compute_freshness
from pff_fa_ai.context.erc.provenance import Provenance
from pff_fa_ai.context.erc.states import ErcSectionStatus
from pff_fa_ai.domain.versioning import assert_expected_version


class ErcRefreshOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    erc: Erc
    previous_version: int
    new_version: int
    refreshed_sections: tuple[str, ...]


class ErcRefreshService:
    """doc 11 §50-54/§69: partial refresh only — touches the one affected section, never
    rebuilds the whole ERC (doc 11 §51-52)."""

    def refresh(
        self,
        *,
        erc: Erc,
        section_name: str,
        section_data: dict[str, Any],
        provenance: Provenance,
        ttl_seconds: int,
        now: datetime,
        expected_version: int,
    ) -> ErcRefreshOutcome:
        assert_expected_version(current_version=erc.version, expected_version=expected_version)

        existing_section = erc.sections.get(section_name)
        next_section_version = (existing_section.section_version + 1) if existing_section else 1
        freshness = compute_freshness(retrieved_at=now, ttl_seconds=ttl_seconds, now=now)

        updated_section = ErcSection(
            name=section_name,
            status=ErcSectionStatus.COMPLETE,
            section_version=next_section_version,
            data=section_data,
            provenance=provenance,
            freshness=freshness,
        )
        updated_sections = dict(erc.sections)
        updated_sections[section_name] = updated_section

        updated_erc = erc.model_copy(
            update={
                "sections": updated_sections,
                "version": erc.version + 1,
                "updated_at": now,
            }
        )
        return ErcRefreshOutcome(
            erc=updated_erc,
            previous_version=erc.version,
            new_version=updated_erc.version,
            refreshed_sections=(section_name,),
        )
