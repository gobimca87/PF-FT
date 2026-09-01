from __future__ import annotations

from pff_fa_ai.common.exceptions import GuardrailError

# Doc 9 §35 "Transaction Cache Rule": never blindly cache mutating HTTP methods.
_UNCACHEABLE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def assert_cacheable_method(http_method: str) -> None:
    method = http_method.upper()
    if method in _UNCACHEABLE_METHODS:
        raise GuardrailError(
            f"Refusing to cache a '{method}' response (doc 9 §35 — enterprise system "
            "remains authoritative for transaction-sensitive operations)",
            details={"http_method": method},
        )
