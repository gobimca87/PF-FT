import pytest

from pff_fa_ai.api.dependencies import _extract_bearer_token


@pytest.mark.parametrize(
    "authorization,expected",
    [
        (None, None),
        ("Bearer abc123", "abc123"),
        ("abc123", "abc123"),  # no scheme prefix — pass through unchanged
        ("Bearer ", ""),
    ],
)
def test_should_extract_bearer_token(authorization: str | None, expected: str | None) -> None:
    assert _extract_bearer_token(authorization) == expected
