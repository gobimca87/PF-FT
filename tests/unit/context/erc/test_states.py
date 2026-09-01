import pytest

from pff_fa_ai.context.erc.states import (
    ErcAuthority,
    ErcValidationStatus,
    FreshnessStatus,
    higher_erc_authority,
)


def test_erc_validation_status_should_match_doc8_section71() -> None:
    assert [status.value for status in ErcValidationStatus] == [
        "VALID",
        "VALID_WITH_WARNINGS",
        "INVALID",
        "INCOMPLETE",
        "STALE",
    ]


def test_freshness_status_should_match_doc8_section17() -> None:
    assert [status.value for status in FreshnessStatus] == ["FRESH", "STALE", "UNKNOWN", "EXPIRED"]


def test_erc_authority_should_match_doc8_section19_order() -> None:
    assert [authority.value for authority in ErcAuthority] == [
        "AUTHORITATIVE",
        "DERIVED",
        "AI_INTERPRETED",
        "RAG_CONTEXT",
        "USER_PROVIDED",
    ]


@pytest.mark.parametrize(
    "first,second,expected",
    [
        (ErcAuthority.AUTHORITATIVE, ErcAuthority.USER_PROVIDED, ErcAuthority.AUTHORITATIVE),
        (ErcAuthority.USER_PROVIDED, ErcAuthority.AUTHORITATIVE, ErcAuthority.AUTHORITATIVE),
        (ErcAuthority.DERIVED, ErcAuthority.AI_INTERPRETED, ErcAuthority.DERIVED),
        (ErcAuthority.RAG_CONTEXT, ErcAuthority.RAG_CONTEXT, ErcAuthority.RAG_CONTEXT),
    ],
)
def test_should_resolve_higher_erc_authority(
    first: ErcAuthority, second: ErcAuthority, expected: ErcAuthority
) -> None:
    assert higher_erc_authority(first, second) == expected
