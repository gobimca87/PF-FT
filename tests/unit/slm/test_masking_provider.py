from collections.abc import AsyncIterator

import pytest

from pff_fa_ai.common.exceptions import ModelError
from pff_fa_ai.guardrails.masking import EgressRule, SlmInputMasker
from pff_fa_ai.guardrails.states import DataClassification
from pff_fa_ai.guardrails.token_vault import InMemoryTokenVault
from pff_fa_ai.slm.masking_provider import MaskedExternalSLMProvider
from pff_fa_ai.slm.models import SlmMessage, SlmRequest, SlmResponse, SlmUsage
from pff_fa_ai.slm.providers import MockSLMProvider
from pff_fa_ai.slm.states import ProviderHealthStatus

_FAKE_AWS_KEY = "AKIAABCDEFGHIJKLMNOP"  # pragma: allowlist secret -- fake key for tests

_MATRIX = {
    DataClassification.PUBLIC: EgressRule(
        can_send_external=True, mask_required=False, hard_block=False
    ),
    DataClassification.CONFIDENTIAL: EgressRule(
        can_send_external=True, mask_required=True, hard_block=False
    ),
    DataClassification.SECRET: EgressRule(
        can_send_external=False, mask_required=True, hard_block=True
    ),
}


class _CapturingProvider:
    """Records the request it was asked to serve so the test can assert what egressed."""

    def __init__(self) -> None:
        self.seen: SlmRequest | None = None

    async def generate(self, request: SlmRequest) -> SlmResponse:
        self.seen = request
        last_user = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
        return SlmResponse(
            request_id="req-1",
            model_id=request.model_id,
            model_version="1.0.0",
            output=f"Handled {last_user}",
            usage=SlmUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            finish_reason="stop",
        )

    async def stream(self, request: SlmRequest) -> AsyncIterator[str]:  # pragma: no cover
        yield "x"

    async def health(self) -> ProviderHealthStatus:  # pragma: no cover - not exercised
        raise NotImplementedError


def _masker() -> SlmInputMasker:
    return SlmInputMasker(InMemoryTokenVault(), egress_matrix=_MATRIX)


def _request(content: str) -> SlmRequest:
    return SlmRequest(
        model_id="mock-slm-v1",
        messages=(SlmMessage(role="user", content=content),),
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=64,
    )


async def test_should_mask_the_payload_before_it_reaches_the_external_model() -> None:
    external = _CapturingProvider()
    provider = MaskedExternalSLMProvider(external, _masker())

    await provider.generate(_request("email me at agent@example.com"))

    assert external.seen is not None
    egressed = external.seen.messages[0].content
    assert "agent@example.com" not in egressed
    assert "PFFTKN" in egressed


async def test_should_unmask_the_model_output_before_returning_it() -> None:
    provider = MaskedExternalSLMProvider(_CapturingProvider(), _masker())

    response = await provider.generate(_request("email me at agent@example.com"))

    assert "agent@example.com" in response.output
    assert "PFFTKN" not in response.output


async def test_should_route_to_self_host_when_masking_hard_blocks() -> None:
    provider = MaskedExternalSLMProvider(
        _CapturingProvider(), _masker(), self_hosted_fallback=MockSLMProvider()
    )

    response = await provider.generate(_request(f"secret {_FAKE_AWS_KEY}"))

    # MockSLMProvider (self-host) sees the raw text — it is in-tenancy, masking optional.
    assert _FAKE_AWS_KEY in response.output


async def test_should_fail_closed_when_no_self_host_is_configured() -> None:
    provider = MaskedExternalSLMProvider(_CapturingProvider(), _masker())

    with pytest.raises(ModelError, match="fail-closed"):
        await provider.generate(_request(f"secret {_FAKE_AWS_KEY}"))
