from datetime import UTC, datetime

import pytest

from pf_ft_ai.common.exceptions import WorkflowError
from pf_ft_ai.context.erc.models import Erc, ErcSection
from pf_ft_ai.context.erc.provenance import Provenance
from pf_ft_ai.context.erc.states import ErcAuthority, ErcLifecycleStatus, ErcSectionStatus
from pf_ft_ai.messaging.handlers.erc_refresh import ErcRefreshService


def _erc(*, sections: dict[str, ErcSection] | None = None) -> Erc:
    now = datetime.now(UTC)
    return Erc(
        erc_id="erc-1",
        schema_version="1.0.0",
        status=ErcLifecycleStatus.READY,
        workflow_instance_id="wf-1",
        conversation_id="conv-1",
        created_at=now,
        updated_at=now,
        sections=sections or {},
    )


def _provenance() -> Provenance:
    return Provenance(
        system="pff-enterprise",
        api="get-officials",
        endpoint_ref="officials.get",
        retrieved_at=datetime.now(UTC),
        authority=ErcAuthority.AUTHORITATIVE,
    )


def test_should_add_a_new_section_and_bump_the_erc_version() -> None:
    service = ErcRefreshService()
    erc = _erc()

    outcome = service.refresh(
        erc=erc,
        section_name="officials",
        section_data={"officials": []},
        provenance=_provenance(),
        ttl_seconds=300,
        now=datetime.now(UTC),
        expected_version=1,
    )

    assert outcome.previous_version == 1
    assert outcome.new_version == 2
    assert outcome.erc.version == 2
    assert outcome.refreshed_sections == ("officials",)
    assert outcome.erc.sections["officials"].section_version == 1


def test_should_only_touch_the_targeted_section() -> None:
    service = ErcRefreshService()
    existing_team_section = ErcSection(
        name="teams", status=ErcSectionStatus.COMPLETE, section_version=3, data={"teams": []}
    )
    erc = _erc(sections={"teams": existing_team_section})

    outcome = service.refresh(
        erc=erc,
        section_name="officials",
        section_data={"officials": []},
        provenance=_provenance(),
        ttl_seconds=300,
        now=datetime.now(UTC),
        expected_version=1,
    )

    # doc 11 §51-52: partial refresh — the untouched section is byte-for-byte unchanged.
    assert outcome.erc.sections["teams"] == existing_team_section
    assert outcome.erc.sections["teams"].section_version == 3


def test_should_bump_the_section_version_on_repeated_refresh() -> None:
    service = ErcRefreshService()
    existing_section = ErcSection(
        name="officials", status=ErcSectionStatus.COMPLETE, section_version=1, data={}
    )
    erc = _erc(sections={"officials": existing_section})

    outcome = service.refresh(
        erc=erc,
        section_name="officials",
        section_data={"officials": ["official-1"]},
        provenance=_provenance(),
        ttl_seconds=300,
        now=datetime.now(UTC),
        expected_version=1,
    )

    assert outcome.erc.sections["officials"].section_version == 2


def test_should_reject_a_stale_expected_version() -> None:
    service = ErcRefreshService()
    erc = _erc()

    with pytest.raises(WorkflowError, match="Concurrency conflict"):
        service.refresh(
            erc=erc,
            section_name="officials",
            section_data={},
            provenance=_provenance(),
            ttl_seconds=300,
            now=datetime.now(UTC),
            expected_version=999,
        )
