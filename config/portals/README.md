# Portal Catalog

`src/pf_ft_ai/portal_links/catalog.py`'s `load_portal_catalog()` loads every `*.yaml` file
in this directory into a `PortalRegistry`.

`affiliation.yaml` (Phase 23) registers the Club Portal with the two routes
`AffiliationAgent` resolves: viewing the application status, and paying an outstanding
invoice. `urls` are placeholder hostnames — TODO(enterprise-integration): replace with the
real Club Portal hostname per environment once confirmed.
`config/base/portal-links.yaml`'s `link_policy.allowed_domains` lists the same placeholder
hostnames so resolution actually succeeds against them; every other portal/domain still
fails closed until it's likewise approved.

Each file holds one `Portal` entry (doc 12 §14/§125), validated against
`Portal`/`PortalRoute`.
