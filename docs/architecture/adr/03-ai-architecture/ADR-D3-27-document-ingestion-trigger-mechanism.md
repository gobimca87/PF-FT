---
id: ADR-D3-27
title: Document ingestion trigger mechanism — what starts a (re-)ingest
domain: 3 AI
ws_ref: [WS-17]
status: Accepted
version: 1.0.0
date: 2026-08-23
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Integration Engineer, Release Manager]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-21, ADR-D2-16, ADR-D2-17, ADR-D3-11, ADR-D5-06, ADR-D6-15]
source_docs:
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §11, §12, §13, §14, §15, §16, §17, §100"
build_phases: [8]
impacted_paths:
  - src/pf_ft_ai/rag/ingestion/
classification: Internal
review_due: 2027-08-23
---

# ADR-D3-27 — Document ingestion trigger mechanism — what starts a (re-)ingest

## 1. Summary

PFF AI will trigger document ingestion through **two complementary paths, matched to
where a document actually lives**: (1) **enterprise-source documents** (policies
tracked in an FA system of record) are re-ingested on a **Service Bus event**
(`document updated` / `policy updated` / `source changed` — doc 13 §100); (2)
**platform-authored knowledge content** (FAQ/how-to material maintained as part of
this repository) is ingested via **CI on merge**, the same governed pipeline that
promotes prompts and config (ADR-D3-11, ADR-D5-06). No path polls or crawls — this
closes a gap left open by [ADR-D3-21](ADR-D3-21-document-ingestion-and-chunking-strategy.md),
which fixed *how* a document is chunked but not *what starts* the ingest.

## 2. Context and Problem Statement

Doc 13 §11 shows the sequence `Source → discovered → registered → identity assigned →
ingestion` but never states what causes "discovered"; §12–§14 define document
identity/version/change-detection (content hash + source-modified timestamp) but
change detection presumes something already triggered a check. §100 is the one
concrete signal in the spec: Service Bus can carry `document updated` / `policy
updated` / `source changed` events leading to re-ingestion/re-indexing. ADR-D3-21
established the corpus profile (5–20 documents/year, ~4k–20k chunks, 2–10% annual
churn) that drove chunking/embedding/vector-store choices, but never decided the
trigger itself — leaving open whether ingestion is polled, pushed, or manual. Given
how rarely this corpus changes, getting the trigger wrong either means expensive
infrastructure for a trickle of updates, or a silent gap where a policy change never
reaches the index.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Enterprise-source document changes must reach RAG | doc 13 §100 |
| DR-F-02 | Platform-authored content ingested via a governed pipeline | ADR-D3-11, D5-06 |
| DR-C-01 | No fabricated freshness — a stale index must be detectable | doc 13 §14; ADR-D4-03-style provenance |
| DR-N-01 | Infrastructure proportionate to 5–20 changes/year | ADR-D3-21 corpus profile |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise source systems can emit change events via Service Bus | Fall back to a low-frequency scheduled scan for that source | Integration review with the source system owner |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Freshness (change reaches the index promptly) | 28 | A stale policy is a real-world risk | Event-to-publish lag |
| EC-02 | Infrastructure proportionality | 22 | 5–20 changes/year (ADR-D3-21) | Idle-infra cost |
| EC-03 | Coverage (handles both source types) | 20 | Enterprise-tracked *and* repo-authored docs exist | Path coverage |
| EC-04 | Auditability / governance fit | 16 | Who approved this content change | Governance gate |
| EC-05 | Operational simplicity | 14 | Small team | # moving parts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Service Bus event-driven (enterprise-source) + CI-on-merge (repo-authored), no polling

**Description.** Enterprise-source documents (e.g. an FA policy CMS) publish a
`document updated`/`policy updated`/`source changed` event (doc 13 §100) consumed by
an idempotent Service Bus listener (ADR-D2-16/D2-18) that enqueues re-ingestion;
platform-authored knowledge content lives in this repository and is ingested by the
CI/CD pipeline on merge to main, gated the same way prompts and config are (ADR-D3-11,
ADR-D5-06, ADR-D6-15).
**Strengths.** Matches doc 13 §100 exactly for enterprise sources; git-native
governance and audit trail for authored content; zero idle polling infrastructure;
proportionate to a 5–20/year corpus.
**Weaknesses.** Requires the enterprise source system to actually emit the event —
not guaranteed for every source (mitigated by DR-A-01's fallback).
**Cost / effort.** Low — reuses existing Service Bus consumer (D2-16) and CI/CD
(D7-09/10) infrastructure.

### 5.2 Option B — Scheduled polling/scan (e.g. nightly job scans all sources for changes)

**Description.** A timer-triggered job periodically re-checks every source's content
hash/timestamp (doc 13 §14) and re-ingests on diff.
**Strengths.** Works even if a source can't emit events; simple mental model.
**Weaknesses.** Runs hundreds of idle checks a year to catch 5–20 real changes —
disproportionate infrastructure for the corpus profile (ADR-D3-21); freshness bounded
by poll interval, not by the actual change.
**Cost / effort.** Low build, wasteful running cost relative to value.

### 5.3 Option C — Pure manual trigger (an admin clicks "re-ingest" via an API/console)

**Description.** No automation; a human initiates every ingest.
**Strengths.** Simplest; maximum human control.
**Weaknesses.** Relies on someone remembering a source changed — the exact silent-gap
failure mode this ADR exists to close; no freshness guarantee at all.
**Cost / effort.** Lowest to build, highest operational risk.

### 5.4 Option D — Webhook from each source system directly into the platform (bypassing Service Bus)

**Description.** Source systems call a PFF AI HTTP endpoint directly on change.
**Strengths.** Low latency; no intermediary.
**Weaknesses.** Exposes an inbound endpoint per source (attack surface, ADR-D6-04);
duplicates what Service Bus already provides as the platform's eventing standard
(ADR-D2-16); no dedup/DLQ/reconciliation (ADR-D2-18) without rebuilding it.
**Cost / effort.** Medium; reinvents existing infrastructure with weaker guarantees.

### 5.5 Option E — Event-driven + CI-on-merge (as A) + a low-frequency safety-net scan for sources with no event feed

**Description.** Option A, plus a low-frequency (e.g. monthly) scan restricted only to
sources confirmed unable to emit change events, as a safety net rather than the
primary mechanism.
**Strengths.** A's proportionality and governance fit, plus closes the residual gap
where a source genuinely cannot emit events, without paying full-corpus polling cost.
**Weaknesses.** A second, narrower mechanism to maintain.
**Cost / effort.** Low-medium; only applies to non-event-capable sources, which is
expected to be a small or empty set.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Real-time filesystem/CMS crawler | No such live crawl target exists in the platform's integration surface (ADR-D2-13); would be built infrastructure for a 5–20/year corpus |
| Ingest on every conversation turn that references a source | Conflates a runtime RAG concern with a batch ingestion concern; wildly disproportionate |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 13 §11–§17/§100 and the
corpus-churn profile established in ADR-D3-21.

| Criterion | Weight | A: Event+CI | B: Scheduled poll | C: Manual only | D: Direct webhook | E: A + safety-net scan |
|---|---|---|---|---|---|---|
| EC-01 Freshness | 28 | 5 | 3 | 1 | 5 | 5 |
| EC-02 Proportionality | 22 | 5 | 2 | 5 | 3 | 4 |
| EC-03 Coverage | 20 | 4 | 5 | 2 | 4 | 5 |
| EC-04 Governance fit | 16 | 5 | 3 | 2 | 3 | 5 |
| EC-05 Simplicity | 14 | 4 | 4 | 5 | 3 | 3 |
| **Weighted total** | **100** | **458** | **312** | **256** | **384** | **456** |

Totals (×20): **A = 458**, **E = 456**, **D = 384**, **B = 312**, **C = 256**.

**Sensitivity.** A and E are effectively tied (2 points apart). **E is adopted**: it
is A plus a narrow, low-cost safety net that only activates for sources confirmed
unable to emit Service Bus events — closing DR-A-01's failure case without paying
full-corpus polling cost (B) for the common case. Manual-only (C) is rejected outright
as the silent-gap anti-pattern; direct webhooks (D) duplicate existing eventing
infrastructure with weaker guarantees.

## 7. Decision

**PFF AI will trigger ingestion via Service Bus events for enterprise-source
documents and CI-on-merge for platform-authored knowledge content, with a narrow,
low-frequency safety-net scan restricted to sources confirmed unable to emit change
events (Option E).** No source is polled by default. Pure manual triggering (C) is
forbidden as a sole mechanism — it may still be used ad hoc for an out-of-band fix,
but is never relied on for routine freshness. Direct webhooks (D) and full-corpus
scheduled polling (B) are rejected as the primary mechanism.

**Status rationale.** `Accepted` — doc 13 §100 fixes Service Bus as the event
mechanism for enterprise sources; the CI-on-merge path for repo-authored content
follows directly from the platform's established config/prompt promotion pattern
(ADR-D3-11, ADR-D5-06). This ADR records the full alternative set and the safety-net
refinement.

## 8. Architecture Detail

- `src/pf_ft_ai/rag/ingestion/`: an idempotent Service Bus consumer (ADR-D2-16,
  reusing the dedup/DLQ/reconciliation model of ADR-D2-18) subscribes to
  `document.updated` / `policy.updated` / `source.changed` events (envelope per
  ADR-D2-17); each event resolves to a `document_id` (doc 13 §12) and enqueues a
  re-ingest through the pipeline fixed in ADR-D3-21 (§15 discovery→…→published).
- Platform-authored content lives under a versioned path in this repository; CI
  (ADR-D7-09) runs the same ingestion pipeline on merge to main, gated by change
  governance (ADR-D6-15) exactly as prompts (ADR-D3-11) and config (ADR-D5-06) are —
  no separate approval process invented for RAG content.
- Change detection within either path still uses content hash + source-modified
  timestamp (doc 13 §14) to avoid re-embedding unchanged content on a duplicate
  event.
- **Safety-net scan**: a low-frequency (monthly) job runs only against the explicit
  allowlist of sources marked "no event feed available"; this list is expected to be
  small or empty and is reviewed whenever a new source is onboarded.
- Ingestion state model and staged-publish (doc 13 §16–§17 — a failed document never
  partially becomes visible) apply identically regardless of which path triggered it.

## 9. Consequences

### 9.1 Positive
- No silent staleness: every source either pushes its own changes or is explicitly
  tracked on the safety-net list.
- No idle polling infrastructure for a 5–20/year corpus.
- Repo-authored content gets the same governance/audit trail as prompts and config.

### 9.2 Negative
- Depends on enterprise source systems actually emitting events (mitigated by the
  safety net for the sources that can't).

### 9.3 Neutral
- The safety-net allowlist is expected to shrink toward empty as source systems are
  onboarded to event emission.

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| The predictability of a uniform poll-everything schedule | Proportionate infrastructure + real-time freshness where it matters | AI Architecture Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise source systems own their content and its change signal; the AI platform only reacts and re-indexes |
| Precedence chain | Ingestion never asserts a document is current beyond what its provenance (content hash/timestamp) shows |
| Four-state separation | Ingestion writes only to the knowledge/RAG plane, never conversation/session/enterprise state |
| Versioned artefacts | Repo-authored content promoted via the same versioned/immutable pipeline as prompts and config |
| Adam persona governs *how*, not *what* | Not applicable — ingestion is upstream of persona-layer generation |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | A source changes without emitting an event and isn't on the safety-net list | Low | Med | M | Onboarding checklist requires declaring event-capability; default to safety-net list if unconfirmed | Integration Engineer | Low |
| RSK-02 | Duplicate events cause redundant re-ingestion | Med | Low | L | Idempotent consumer + content-hash short-circuit (ADR-D2-18, doc 13 §14) | Backend Lead | Low |
| RSK-03 | CI-on-merge ingest fails silently | Low | Med | M | Staged publish — failure never exposes a partial index (doc 13 §17) | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Event-to-published lag (enterprise sources) | ≤ 1 hour | > 24 hours | Ingestion traces | Continuous |
| QM-02 | Sources on the safety-net (no-event) list | trending to 0 | growing | Source registry | Quarterly |
| QM-03 | Duplicate re-ingests avoided via content-hash short-circuit | tracked | — | Ingestion metrics | Monthly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | No new inbound endpoints (event-driven via existing Service Bus, plus CI); avoids Option D's per-source webhook surface |
| Data classification touched | Internal knowledge content only (per ADR-D3-20 scope) |
| Personal data / PII | None — ingestion sources are knowledge/policy documents |
| Children's data and safeguarding | Safeguarding-related *knowledge* content follows the same governed CI path as any other authored content |
| UK GDPR lawful basis and rights impact | Not applicable |
| Audit and evidential requirements | Every ingest traced to its trigger (event id or CI commit) |
| Standards touched | ISO/IEC 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 8 |
| Repository paths | `src/pf_ft_ai/rag/ingestion/` |
| Configuration | Event subscription topics; safety-net source allowlist |
| Contracts / schemas | Service Bus event envelope (ADR-D2-17) for `document.updated`/`policy.updated`/`source.changed` |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-21, D2-16, D2-17, D2-18, D3-11, D5-06 |
| Effort estimate | S — reuses existing Service Bus consumer and CI infrastructure |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Enterprise-source change event triggers re-ingestion within QM-01 target | Integration test |
| AC-02 | Repo-authored content ingests on CI merge | CI pipeline test |
| AC-03 | Duplicate events do not trigger redundant re-embedding | Idempotency test |
| AC-04 | Safety-net scan covers only the declared no-event-feed sources | Config audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Event consumption lag; ingest success/failure per trigger path |
| Alerting | Event-to-published lag breach; ingest failure |
| Runbook | `docs/runbooks/rag.md` (ingestion trigger section) |
| Failure mode and degradation | Consumer down → events queue in Service Bus (ADR-D2-16), processed on recovery; no data loss |
| Rollback | Re-run ingestion for the affected document(s) |
| Support model impact | AI platform + integration engineering |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Event consumer + CI integration | S | negligible | Reuses ADR-D2-16/D7-09 infrastructure |
| Safety-net scan | — | negligible | Monthly job over a small/empty source list |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | A staleness incident traced to a missed event | Incident (ADR-D7-17) | CAR; add the source to the safety-net list or fix event emission |
| RT-02 | Corpus churn grows materially beyond 5–20/year (ADR-D3-21 RT) | ADR-D3-21 revisit | Re-evaluate trigger proportionality |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-17 RAG & Retrieval |
| Specification sections | doc 13 §11–§17, §100 |
| Requirement IDs | RAG-INGEST-TRIGGER-* |
| Build phases | 8 |
| Code paths | `src/pf_ft_ai/rag/ingestion/` |
| Configuration | event subscriptions, safety-net allowlist |
| Tests | event-trigger + CI-ingest + idempotency suites |
| Upstream ADRs | ADR-D3-21, D2-16, D2-17, D2-18 |
| Downstream ADRs | — |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-23 | AI Architecture Lead | Initial decision recorded — closes the ingestion-trigger gap identified after the initial 136-ADR pass. |
