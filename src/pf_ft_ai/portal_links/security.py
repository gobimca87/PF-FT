from __future__ import annotations

from urllib.parse import urlparse

_ALLOWED_SCHEME = "https"


def assert_safe_url(url: str, *, allowed_domains: frozenset[str]) -> str | None:
    """doc 12 §30-33/§110: HTTPS-only, allowlisted host, no credentials embedded.
    Returns a reason code on failure, `None` if the URL passes."""
    parsed = urlparse(url)
    if parsed.scheme != _ALLOWED_SCHEME:
        return "UNSAFE_SCHEME"
    if parsed.username or parsed.password:
        return "CREDENTIALS_IN_URL"
    if parsed.hostname not in allowed_domains:
        return "DOMAIN_NOT_ALLOWLISTED"
    return None
