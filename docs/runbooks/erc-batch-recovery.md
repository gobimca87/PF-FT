# ERC Batch Recovery Runbook

**Owner:** AI Platform / Enterprise Integration (doc 28 §4) · **Severity:** P2/P3
depending on how much of the ERC is affected (doc 28 §10-11).

## Symptoms (doc 28 §72)

Missing team, missing official, failed batch, duplicate data, aggregation failure,
context overflow, API failure mid-batch.

## Diagnostic steps

1. Identify the batch shape — `split_into_batches()` (`src/pf_ft_ai/context/collection/batching.py`)
   uses `config/base/batching.yaml`'s `batching.batch_size` (agreed default: 20).
   `tests/erc/test_batch_scale_points.py` documents the exact scale points this has
   been verified at (1, 20, 21, 40, 100, 100+).
2. Check aggregation — `aggregate_records()` (`context/collection/aggregator.py`)
   returns `AggregationResult.is_complete`, `.received_count`, `.duplicate_count`.
   **`is_complete=False` must never be reported to the user as success** (doc 28 §75,
   doc 22 §53).
3. Determine failure type per entity: missing (never returned by the API), duplicate
   (returned more than once — `deduplicate_records()` handles this deterministically),
   or aggregation mismatch (`received_count != expected_count`).

## Recovery (doc 28 §74)

```text
Identify failed batch
 → Identify failure type (transient vs. permanent)
 → Retry if transient (respect the enterprise API's own retry/circuit-breaker state —
   see enterprise-api.md)
 → Re-fetch authoritative data if required
 → Re-validate and re-aggregate
 → Continue the workflow only once complete
```

Never fabricate a missing team/official record to make the batch appear complete
(doc 28 §17 "Never fabricate missing workflow or ERC data").

## Context overflow

If the aggregated ERC is too large for the SLM context budget: check
`context/projection/budget.py`'s `compute_available_context_tokens()` — a negative or
near-zero result means controlled batching/compression is required, never silent
truncation (doc 26 §36, doc 22 §129).

## Escalation

AI Platform team; escalate to Enterprise Integration if the root cause is the
enterprise API returning incomplete data rather than the batching/aggregation logic
itself.
