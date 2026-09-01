import pytest

from pff_fa_ai.cache.policy import assert_cacheable_method
from pff_fa_ai.common.exceptions import GuardrailError


@pytest.mark.parametrize("method", ["GET", "get", "HEAD", "OPTIONS"])
def test_should_allow_safe_read_methods(method: str) -> None:
    assert_cacheable_method(method)


@pytest.mark.parametrize("method", ["POST", "put", "PATCH", "delete"])
def test_should_reject_mutating_methods(method: str) -> None:
    with pytest.raises(GuardrailError, match="Refusing to cache"):
        assert_cacheable_method(method)
