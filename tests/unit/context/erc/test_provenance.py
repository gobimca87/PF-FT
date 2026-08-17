from datetime import UTC, datetime

from pf_ft_ai.context.erc.provenance import Provenance
from pf_ft_ai.context.erc.states import ErcAuthority


def test_should_build_provenance_with_authoritative_source() -> None:
    provenance = Provenance(
        system="enterprise-club-service",
        api="get-club",
        endpoint_ref="enterprise.club.get",
        retrieved_at=datetime.now(UTC),
        authority=ErcAuthority.AUTHORITATIVE,
    )

    assert provenance.authority is ErcAuthority.AUTHORITATIVE
    assert provenance.system == "enterprise-club-service"
