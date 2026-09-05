from __future__ import annotations

from collections.abc import AsyncIterator

from pff_fa_ai.common.exceptions import ModelError
from pff_fa_ai.guardrails.masking import SlmInputMasker
from pff_fa_ai.slm.models import SlmMessage, SlmRequest, SlmResponse
from pff_fa_ai.slm.providers import SLMProvider
from pff_fa_ai.slm.states import ProviderHealthStatus


class MaskedExternalSLMProvider:
    """ADR-D6-19 §7-8 — the mandatory masking boundary for an external / hosted SLM.

    Every payload is masked/tokenised before it leaves the tenancy; the model's tokenised
    output is re-identified inside the boundary via the token vault before use. The
    boundary fails closed: if any part of the payload cannot be masked and verified (a
    hard-blocked class, or residual raw PII), the external call is never made — it is
    routed to the self-hosted SLM when one is configured, otherwise blocked (ADR-D6-19
    DR-F-04). Injection/output guardrails still run around this decorator; masking is only
    the data-egress transform.
    """

    def __init__(
        self,
        external: SLMProvider,
        masker: SlmInputMasker,
        *,
        self_hosted_fallback: SLMProvider | None = None,
    ) -> None:
        self._external = external
        self._masker = masker
        self._self_hosted_fallback = self_hosted_fallback

    async def generate(self, request: SlmRequest) -> SlmResponse:
        masked_messages: list[SlmMessage] = []
        for message in request.messages:
            result = await self._masker.mask_for_external(message.content)
            if result.blocked:
                return await self._route_to_self_host_or_block(request, result.block_reasons)
            masked_messages.append(SlmMessage(role=message.role, content=result.masked_text))

        masked_request = request.model_copy(update={"messages": tuple(masked_messages)})
        response = await self._external.generate(masked_request)
        unmasked_output = await self._masker.unmask(response.output)
        return response.model_copy(update={"output": unmasked_output})

    async def stream(self, request: SlmRequest) -> AsyncIterator[str]:
        # Masked streaming would emit tokenised fragments that cannot be safely unmasked
        # mid-stream, so the boundary generates fully, unmasks, then re-streams.
        response = await self.generate(request)
        for word in response.output.split():
            yield word + " "

    async def health(self) -> ProviderHealthStatus:
        return await self._external.health()

    async def _route_to_self_host_or_block(
        self, request: SlmRequest, block_reasons: tuple[str, ...]
    ) -> SlmResponse:
        if self._self_hosted_fallback is None:
            raise ModelError(
                "External SLM payload could not be masked and no self-hosted SLM is "
                "configured to route to; blocking (fail-closed, ADR-D6-19)",
                details={"block_reasons": list(block_reasons)},
            )
        return await self._self_hosted_fallback.generate(request)
