# API Catalog

`src/pff_fa_ai/integration/api/catalog.py`'s `load_api_catalog()` loads every `*.yaml` file
in this directory into an `ApiCatalog`.

`affiliation.yaml` (Phase 23) registers the 7 read-only tools DEVELOPMENT-GUIDE names for
`AffiliationAgent`: get_club, get_application, get_teams, get_officials, get_insurance,
get_products, get_payment_status. Their `endpoint.path` values are placeholder shapes, not
a confirmed PFF contract — TODO(enterprise-integration): replace once the real API spec is
available (Phase 23's own scope allowance: "implement or stub with clear TODOs against real
PFF APIs"). The rest of doc 10 §7's catalog (`teams.yaml`, `officials.yaml`, `courses.yaml`,
`compliance.yaml` beyond what affiliation needs) stays unpopulated until a later workflow
needs it — no other business agent has been built yet.

Each file holds one entry or a YAML list of entries, validated against `ApiCatalogEntry`
(doc 10 §10, §125).
