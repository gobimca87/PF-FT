# Golden Evaluation Dataset

Empty by design. `src/pf_ft_ai/evaluation/dataset.py`'s `load_golden_dataset()` loads
every `*.yaml` file in this directory into a `GoldenDatasetRegistry` — the loader,
registry, deterministic-assertion runner, and retrieval metrics are fully built and
tested (see `tests/unit/evaluation/`), but populating it with real cases across the 16
categories doc 21 §13 requires a real workflow to write golden cases *against*, which
doesn't exist until `AffiliationAgent` (`DEVELOPMENT-GUIDE.md` Phase 23).

Each file holds one `GoldenCase` entry or a YAML list of entries (doc 21 §10-11):

```yaml
case_id: AFF-001
workflow: club-affiliation
category: HAPPY_PATH
input:
  query: "Start affiliation for club ABC"
expected:
  workflow: affiliation
  required_context: [club, officials, course]
  expected_tools: [club-details, official-details, course-details]
```
