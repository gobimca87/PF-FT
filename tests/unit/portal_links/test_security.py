from pff_fa_ai.portal_links.security import assert_safe_url

_ALLOWED = frozenset({"portal.example.com"})


def test_should_accept_a_safe_https_url() -> None:
    assert assert_safe_url("https://portal.example.com/clubs/123", allowed_domains=_ALLOWED) is None


def test_should_reject_a_non_https_scheme() -> None:
    assert (
        assert_safe_url("http://portal.example.com/clubs/123", allowed_domains=_ALLOWED)
        == "UNSAFE_SCHEME"
    )


def test_should_reject_javascript_scheme() -> None:
    assert assert_safe_url("javascript:alert(1)", allowed_domains=_ALLOWED) == "UNSAFE_SCHEME"


def test_should_reject_a_url_with_embedded_credentials() -> None:
    assert (
        assert_safe_url("https://user:pass@portal.example.com/clubs/123", allowed_domains=_ALLOWED)
        == "CREDENTIALS_IN_URL"
    )


def test_should_reject_an_unallowlisted_domain() -> None:
    assert (
        assert_safe_url("https://evil.example.com/clubs/123", allowed_domains=_ALLOWED)
        == "DOMAIN_NOT_ALLOWLISTED"
    )
