from pff_fa_ai.guardrails.masking import (
    EgressRule,
    KnownSensitiveValue,
    SlmInputMasker,
)
from pff_fa_ai.guardrails.states import DataClassification
from pff_fa_ai.guardrails.token_vault import InMemoryTokenVault, is_vault_token

_FAKE_AWS_KEY = "AKIAABCDEFGHIJKLMNOP"  # pragma: allowlist secret -- fake key for tests

# ADR-D6-19 §8 base egress matrix: personal → mask, secret/restricted → hard-block.
_MATRIX = {
    DataClassification.PUBLIC: EgressRule(
        can_send_external=True, mask_required=False, hard_block=False
    ),
    DataClassification.INTERNAL: EgressRule(
        can_send_external=True, mask_required=False, hard_block=False
    ),
    DataClassification.CONFIDENTIAL: EgressRule(
        can_send_external=True, mask_required=True, hard_block=False
    ),
    DataClassification.RESTRICTED: EgressRule(
        can_send_external=False, mask_required=True, hard_block=True
    ),
    DataClassification.SECRET: EgressRule(
        can_send_external=False, mask_required=True, hard_block=True
    ),
}


def _masker() -> SlmInputMasker:
    return SlmInputMasker(InMemoryTokenVault(), egress_matrix=_MATRIX)


async def test_should_tokenise_detected_pii_so_no_raw_value_egresses() -> None:
    result = await _masker().mask_for_external("Contact the secretary at john.doe@example.com")

    assert not result.blocked
    assert "john.doe@example.com" not in result.masked_text
    assert result.token_count == 1
    assert "PFFTKN" in result.masked_text


async def test_should_hard_block_a_secret_and_send_nothing() -> None:
    result = await _masker().mask_for_external(f"token {_FAKE_AWS_KEY} grants access")

    assert result.blocked
    assert result.masked_text == ""
    assert any(reason.startswith("HARD_BLOCK-SECRET") for reason in result.block_reasons)


async def test_should_hard_block_restricted_known_values_even_when_maskable() -> None:
    known = [
        KnownSensitiveValue(value="child-record-123", classification=DataClassification.RESTRICTED)
    ]

    result = await _masker().mask_for_external(
        "safeguarding note child-record-123", known_values=known
    )

    assert result.blocked
    assert any(reason.startswith("HARD_BLOCK-RESTRICTED") for reason in result.block_reasons)


async def test_should_tokenise_a_known_confidential_enterprise_value() -> None:
    known = [KnownSensitiveValue(value="CLB-99887", classification=DataClassification.CONFIDENTIAL)]

    result = await _masker().mask_for_external("affiliation for club CLB-99887", known_values=known)

    assert not result.blocked
    assert "CLB-99887" not in result.masked_text
    assert result.token_count == 1


async def test_should_fail_closed_when_a_classification_is_absent_from_the_matrix() -> None:
    masker = SlmInputMasker(InMemoryTokenVault(), egress_matrix={})
    known = [KnownSensitiveValue(value="x", classification=DataClassification.CONFIDENTIAL)]

    result = await masker.mask_for_external("value x here", known_values=known)

    assert result.blocked  # unclassified ⇒ hard-block (default-safe)


async def test_should_round_trip_a_masked_output_back_to_the_original_value() -> None:
    masker = _masker()
    result = await masker.mask_for_external("email jane@example.org please")
    token = result.masked_text.split("email ")[1].split(" please")[0]
    assert is_vault_token(token)

    model_output = f"I have contacted {token} about the affiliation."
    unmasked = await masker.unmask(model_output)

    assert "jane@example.org" in unmasked
    assert "PFFTKN" not in unmasked


async def test_should_reuse_the_same_token_for_the_same_value() -> None:
    result = await _masker().mask_for_external("a@b.com and again a@b.com")

    tokens = {part for part in result.masked_text.split() if is_vault_token(part)}
    assert len(tokens) == 1  # one token reused for the identical address


async def test_should_leave_clean_text_untouched() -> None:
    result = await _masker().mask_for_external("The affiliation workflow is match ready.")

    assert not result.blocked
    assert result.masked_text == "The affiliation workflow is match ready."
    assert result.token_count == 0
