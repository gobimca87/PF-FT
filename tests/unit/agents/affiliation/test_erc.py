from pff_fa_ai.agents.affiliation.erc import (
    REQUIRED_SECTIONS,
    build_affiliation_erc,
    build_erc_section,
)
from pff_fa_ai.context.erc.states import ErcAuthority, ErcLifecycleStatus, ErcSectionStatus


def test_build_erc_section_should_mark_the_source_as_authoritative() -> None:
    section = build_erc_section(
        name="club",
        data={"club_id": "club-1"},
        api_id="enterprise.affiliation.get_club",
        endpoint_ref="/api/v1/clubs/{clubId}",
    )

    assert section.status is ErcSectionStatus.COMPLETE
    assert section.provenance is not None
    assert section.provenance.authority is ErcAuthority.AUTHORITATIVE
    assert section.provenance.api == "enterprise.affiliation.get_club"


def test_build_erc_section_should_wrap_a_non_dict_payload() -> None:
    section = build_erc_section(
        name="teams",
        data=[{"team_id": "team-1"}],
        api_id="enterprise.affiliation.get_teams",
        endpoint_ref="/api/v1/clubs/{clubId}/teams",
    )

    assert section.data == {"items": [{"team_id": "team-1"}]}


def test_build_affiliation_erc_should_reach_ready_status() -> None:
    sections = {
        name: build_erc_section(name=name, data={}, api_id="api", endpoint_ref="/x")
        for name in REQUIRED_SECTIONS
    }

    erc = build_affiliation_erc(
        erc_id="erc-1", workflow_instance_id="wf-1", conversation_id="conv-1", sections=sections
    )

    assert erc.status is ErcLifecycleStatus.READY
    assert erc.completeness is not None
    assert erc.completeness.completed_sections == len(REQUIRED_SECTIONS)
    assert erc.completeness.missing_sections == ()


def test_build_affiliation_erc_should_report_missing_sections() -> None:
    sections = {
        "club": build_erc_section(name="club", data={}, api_id="api", endpoint_ref="/x"),
    }

    erc = build_affiliation_erc(
        erc_id="erc-1", workflow_instance_id="wf-1", conversation_id="conv-1", sections=sections
    )

    assert erc.completeness is not None
    assert "teams" in erc.completeness.missing_sections
    assert erc.completeness.completed_sections == 1
