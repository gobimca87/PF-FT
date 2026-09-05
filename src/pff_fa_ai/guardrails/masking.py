from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field

from pff_fa_ai.guardrails.pii import _PII_PATTERNS, detect_pii
from pff_fa_ai.guardrails.secrets import detect_secrets
from pff_fa_ai.guardrails.states import DataClassification
from pff_fa_ai.guardrails.token_vault import TokenVault, is_vault_token

# ADR-D6-19 §8: the mask/tokenise categories the platform can recognise deterministically
# today. Names/free-text special-category and children's data still need the NLP model
# doc 18 §61 flags as absent — a caller that already knows a value is sensitive passes it
# via `known_values`, and anything the matrix does not classify fails closed (hard-block).
_PII_CLASSIFICATION = DataClassification.CONFIDENTIAL
_SECRET_CLASSIFICATION = DataClassification.SECRET

# ADR-D6-19 §8: matches any vault token embedded in a model's output, so unmask can find
# and re-identify it inside the boundary before use. Token bodies are alphabetic only (see
# token_vault) — the pattern deliberately excludes digits.
_TOKEN_IN_TEXT = re.compile(r"PFFTKN-[A-Za-z]+-[a-z]+")


class EgressRule(BaseModel):
    """ADR-D6-19 §8 per-classification egress rule from the data-handling matrix."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    can_send_external: bool
    mask_required: bool
    hard_block: bool


class MaskingResult(BaseModel):
    """ADR-D6-19 §14 boundary contract. `blocked` is fail-closed: the external call MUST
    NOT proceed and is routed to the self-hosted SLM instead."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    masked_text: str
    blocked: bool = False
    block_reasons: tuple[str, ...] = Field(default_factory=tuple)
    token_count: int = 0


class KnownSensitiveValue(BaseModel):
    """A value the caller already knows is sensitive — typically an enterprise-record
    value (ADR-D6-07 §10) that no pattern detector can recognise on its own."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    value: str
    classification: DataClassification


EgressMatrix = Mapping[DataClassification, EgressRule]


class SlmInputMasker:
    """ADR-D6-19 §7-8 — the external-SLM boundary transform. For any payload bound for an
    external / hosted model it hard-blocks the classes that must never leave (ADR-D6-16),
    tokenises every remaining personal and enterprise value through the token vault, and
    verifies no raw PII or secret survives before egress. It is a boundary transform, not
    a business decision (DR-C-03)."""

    def __init__(self, vault: TokenVault, *, egress_matrix: EgressMatrix) -> None:
        self._vault = vault
        self._matrix = egress_matrix

    def _rule_for(self, classification: DataClassification) -> EgressRule:
        # Fail-closed default: an unclassified value is treated as hard-blocked, never
        # silently sent (ADR-D6-19 DR-F-04).
        return self._matrix.get(
            classification,
            EgressRule(can_send_external=False, mask_required=True, hard_block=True),
        )

    async def mask_for_external(
        self,
        text: str,
        *,
        known_values: Sequence[KnownSensitiveValue] = (),
    ) -> MaskingResult:
        block_reasons: list[str] = []
        working = text

        # 1. Hard-block the always-forbidden classes first (ADR-D6-16, DR-C-01) — these
        #    are never sent, even masked.
        for secret_category in sorted(detect_secrets(working)):
            if self._rule_for(_SECRET_CLASSIFICATION).hard_block:
                block_reasons.append(f"HARD_BLOCK-SECRET-{secret_category}")
        for known in known_values:
            if self._rule_for(known.classification).hard_block:
                block_reasons.append(f"HARD_BLOCK-{known.classification.value}")
        if block_reasons:
            return MaskingResult(masked_text="", blocked=True, block_reasons=tuple(block_reasons))

        # 2. Tokenise known enterprise/sensitive values the detectors cannot see.
        token_count = 0
        for known in known_values:
            rule = self._rule_for(known.classification)
            if rule.mask_required and known.value in working:
                token = await self._vault.tokenize(
                    known.value, classification=known.classification.value
                )
                working = working.replace(known.value, token)
                token_count += 1

        # 3. Tokenise pattern-detectable PII.
        if self._rule_for(_PII_CLASSIFICATION).mask_required:
            working, pii_tokens = await self._mask_detected_pii(working)
            token_count += pii_tokens

        # 4. Verify fail-closed: nothing raw may remain (ADR-D6-19 AC-02).
        residual_pii = detect_pii(working)
        residual_secrets = detect_secrets(working)
        if residual_pii or residual_secrets:
            reasons = tuple(f"VERIFY_FAIL-{c}" for c in sorted(residual_pii | residual_secrets))
            return MaskingResult(masked_text="", blocked=True, block_reasons=reasons)

        return MaskingResult(masked_text=working, token_count=token_count)

    async def _mask_detected_pii(self, text: str) -> tuple[str, int]:
        masked = text
        count = 0
        for pattern in _PII_PATTERNS.values():
            matches = {match.group(0) for match in pattern.finditer(masked)}
            for raw in matches:
                if is_vault_token(raw):
                    continue
                token = await self._vault.tokenize(raw, classification=_PII_CLASSIFICATION.value)
                masked = masked.replace(raw, token)
                count += 1
        return masked, count

    async def unmask(self, text: str) -> str:
        """ADR-D6-19 §8 — re-identify a masked external output inside the boundary before
        use. Every vault token found in the output is mapped back to its original value."""
        result = text
        for token in set(_TOKEN_IN_TEXT.findall(text)):
            result = result.replace(token, await self._vault.detokenize(token))
        return result
