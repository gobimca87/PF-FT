# API Catalog

Empty by design. `src/pf_ft_ai/integration/api/catalog.py`'s `load_api_catalog()` loads every
`*.yaml` file in this directory into an `ApiCatalog` — the loader and validation are fully
built and tested (see `tests/unit/integration/api/`), but populating it with real entries
(`clubs.yaml`, `affiliations.yaml`, `teams.yaml`, `officials.yaml`, `courses.yaml`,
`compliance.yaml` per doc 10 §7) requires real PFF enterprise API contracts, which aren't
available yet. `DEVELOPMENT-GUIDE.md` Phase 23 (`AffiliationAgent`) is where those get
registered against real or documented PFF endpoints.

Each file holds one entry or a YAML list of entries, validated against `ApiCatalogEntry`
(doc 10 §10, §125).
