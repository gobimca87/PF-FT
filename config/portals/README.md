# Portal Catalog

Empty by design. `src/pf_ft_ai/portal_links/catalog.py`'s `load_portal_catalog()` loads
every `*.yaml` file in this directory into a `PortalRegistry` — the loader, resolver, and
security validation are fully built and tested (see `tests/unit/portal_links/`), but
populating it with real portals (`club-portal.yaml`, `affiliation-portal.yaml`, ...)
requires real PFF enterprise portal base URLs and route paths, which aren't available
yet. `DEVELOPMENT-GUIDE.md` Phase 23 (`AffiliationAgent`) is where those get registered
against real or documented PFF portal endpoints.

Each file holds one `Portal` entry (doc 12 §64/§124), validated against
`Portal`/`PortalRoute` (doc 12 §14/§125). `config/base/portal-links.yaml`'s
`link_policy.allowed_domains` must also be populated with the real portal hostname(s)
before any link resolution can succeed — it starts empty.
