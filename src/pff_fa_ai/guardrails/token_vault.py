from __future__ import annotations

import uuid
from typing import Protocol

from pff_fa_ai.common.exceptions import GuardrailError

# ADR-D6-19 §8: token format is deterministic and syntactically distinct so a masked
# payload can be verified to contain no raw value and a model can round-trip the token
# through free text without corrupting it. The random body is ALPHABETIC ONLY — a token
# must never itself contain a digit run that a numeric PII detector (e.g. a phone number)
# would match, or the boundary verify step would false-positive on its own output.
_TOKEN_PREFIX = "PFFTKN"  # noqa: S105 -- opaque placeholder prefix, not a credential
_DIGIT_TO_ALPHA = str.maketrans("0123456789", "klmnopqrst")


def _alpha_id() -> str:
    return uuid.uuid4().hex.translate(_DIGIT_TO_ALPHA)


def is_vault_token(candidate: str) -> bool:
    return candidate.startswith(f"{_TOKEN_PREFIX}-")


class TokenVault(Protocol):
    """ADR-D6-19 §8 / ADR-D6-06 §8 — a Confidential, tenancy-internal mapping of opaque
    tokens to original values. Contents never egress (DR-N-02); reverse access is
    controlled and audited by the caller. Scoped to the turn/session via TTL by the
    backing store."""

    async def tokenize(self, value: str, *, classification: str) -> str: ...

    async def detokenize(self, token: str) -> str: ...


class InMemoryTokenVault:
    """Reference/tests implementation — the same "mock until the real store is wired"
    posture as `MockSLMProvider`. A production vault is Redis/Key-Vault-backed
    (ADR-D4-10 / ADR-D6-05) with a short TTL; the mapping semantics are identical."""

    def __init__(self) -> None:
        self._forward: dict[str, str] = {}
        self._reverse: dict[str, str] = {}

    async def tokenize(self, value: str, *, classification: str) -> str:
        # Reuse a token for an identical value so referential utility is preserved
        # within a turn (ADR-D6-06 §5.5) — the same club id masks to the same token.
        existing = self._reverse.get(value)
        if existing is not None:
            return existing
        token = f"{_TOKEN_PREFIX}-{classification}-{_alpha_id()}"
        self._forward[token] = value
        self._reverse[value] = token
        return token

    async def detokenize(self, token: str) -> str:
        value = self._forward.get(token)
        if value is None:
            raise GuardrailError(
                "Token not found in the vault; masked SLM output cannot be re-identified",
                details={"token": token},
            )
        return value
