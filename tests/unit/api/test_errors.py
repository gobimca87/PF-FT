import pytest
from fastapi import Request, status

from pf_ft_ai.api.errors import _status_code_for, platform_error_handler
from pf_ft_ai.common.exceptions import PlatformError, ValidationError


def test_should_map_a_known_subclass_to_its_status_code() -> None:
    assert _status_code_for(ValidationError("bad")) == status.HTTP_400_BAD_REQUEST


def test_should_default_an_unmapped_platform_error_to_500() -> None:
    assert _status_code_for(PlatformError("generic")) == status.HTTP_500_INTERNAL_SERVER_ERROR


async def test_should_reraise_a_non_platform_error() -> None:
    request = Request(scope={"type": "http", "headers": []})

    with pytest.raises(ValueError, match="not ours"):
        await platform_error_handler(request, ValueError("not ours"))
