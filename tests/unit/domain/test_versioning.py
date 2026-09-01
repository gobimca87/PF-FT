import pytest

from pff_fa_ai.common.exceptions import WorkflowError
from pff_fa_ai.domain.versioning import Versioned, assert_expected_version


def test_should_default_new_entity_to_version_one() -> None:
    assert Versioned().version == 1


def test_should_accept_update_when_expected_version_matches() -> None:
    assert_expected_version(current_version=10, expected_version=10)


def test_should_reject_update_when_expected_version_is_stale() -> None:
    with pytest.raises(WorkflowError, match="Concurrency conflict"):
        assert_expected_version(current_version=11, expected_version=10)
