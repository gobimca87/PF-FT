import pytest

from pff_fa_ai.common.exceptions import GuardrailError
from pff_fa_ai.guardrails.token_vault import InMemoryTokenVault, is_vault_token


async def test_should_tokenise_and_detokenise_round_trip() -> None:
    vault = InMemoryTokenVault()

    token = await vault.tokenize("john@example.com", classification="CONFIDENTIAL")

    assert is_vault_token(token)
    assert await vault.detokenize(token) == "john@example.com"


async def test_should_reuse_a_token_for_the_same_value() -> None:
    vault = InMemoryTokenVault()

    first = await vault.tokenize("CLB-1", classification="CONFIDENTIAL")
    second = await vault.tokenize("CLB-1", classification="CONFIDENTIAL")

    assert first == second


async def test_should_raise_for_an_unknown_token() -> None:
    with pytest.raises(GuardrailError, match="cannot be re-identified"):
        await InMemoryTokenVault().detokenize("PFFTKN-CONFIDENTIAL-v-deadbeef")
