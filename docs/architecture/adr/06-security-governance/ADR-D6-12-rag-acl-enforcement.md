---
id: ADR-D6-12
title: RAG ACL enforcement and retrieval-time authorization
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Architecture Lead, Backend Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D3-22, ADR-D3-24, ADR-D6-03, ADR-D3-20, ADR-D6-09]
source_docs:
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §39, §40, §41, §44, §45"
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §33, §34, §35, §36, §37, §38, §39"
  - "MD files/4 AI/14.PF-FT-AI-EMBEDDING-VECTOR.md §49, §50, §51"
build_phases: [8]
impacted_paths:
  - src/pf_ft_ai/rag/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-12 — RAG ACL enforcement and retrieval-time authorization

## 1. Summary

RAG retrieval will enforce **access control at retrieval time**: the caller's authz
context (ADR-D6-03) is translated into **metadata filters applied before/within the
vector search**, so a user only ever retrieves knowledge chunks they are authorized to
see — ACL is a filter on the query, **never a prompt instruction** the model may ignore
(19.PF-FT-AI-SECURITY.md §39–§41, §44–§45; 13.FP-FT-AI-RAG.md §33–§39; 14.PF-FT-AI-EMBEDDING-VECTOR.md §49–§51). Filter construction is
injection-safe.

## 2. Context and Problem Statement

19.PF-FT-AI-SECURITY.md §39–§41 RAG security/ACL enforcement/content trust, §44–§45 vector-store/metadata
security; 13.FP-FT-AI-RAG.md §33–§39 ACL-aware retrieval (§35 "ACL is not a prompt"), tenant/org/role
filtering, classification; 14.PF-FT-AI-EMBEDDING-VECTOR.md §49–§51 ACL filtering, metadata-filter construction,
filter-injection protection. If ACL were a prompt ("only show allowed docs"), the model
could be jailbroken into leaking restricted knowledge. This ADR fixes retrieval-time,
filter-based ACL.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-C-01 | ACL is a filter, not a prompt | 13.FP-FT-AI-RAG.md §35 |
| DR-F-01 | Filter by tenant/org/role/classification | 13.FP-FT-AI-RAG.md §36–§39 |
| DR-F-02 | Filter applied before/within search | 13.FP-FT-AI-RAG.md §62; 14.PF-FT-AI-EMBEDDING-VECTOR.md §49 |
| DR-C-02 | Injection-safe filter construction | 14.PF-FT-AI-EMBEDDING-VECTOR.md §51 |
| DR-F-03 | Authz context drives the filter | ADR-D6-03 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Chunks carry security metadata | Enforce at ingestion (ADR-D3-21) | Metadata audit |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Access-control correctness (no leak) | 34 | Confidentiality | ACL tests |
| EC-02 | Non-bypassability (not a prompt) | 24 | Jailbreak-proof | Structural filter |
| EC-03 | Injection-safe filter construction | 16 | Filter injection | Bound filters |
| EC-04 | Performance (filter+search) | 14 | Latency | p95 |
| EC-05 | Granularity (tenant/org/role/class) | 12 | Real ACL model | Dimensions |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Retrieval-time metadata-filter ACL from authz context, injection-safe, pre/within search

**Description.** Translate authz context into a bound metadata filter (tenant/org/role/
classification) applied before/within the vector search (13.FP-FT-AI-RAG.md §62; 14.PF-FT-AI-EMBEDDING-VECTOR.md §49–§50);
filters parameterised to prevent injection (§51); chunks carry security metadata from
ingestion.
**Strengths.** Structural, non-bypassable, granular, injection-safe.
**Weaknesses.** Requires security metadata on every chunk.
**Cost / effort.** Medium.

### 5.2 Option B — Prompt-based ACL ("only use authorized docs")

**Description.** Tell the model to respect access rules.
**Strengths.** Trivial.
**Weaknesses.** Model can be jailbroken into leaking; violates 13.FP-FT-AI-RAG.md §35.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Post-retrieval filtering (retrieve all, then drop unauthorized)

**Description.** Search unfiltered, remove unauthorized results after.
**Strengths.** Simple search.
**Weaknesses.** Unauthorized content is retrieved (in memory/logs); leakage risk; wastes
budget; timing side-channels.
**Cost / effort.** Low; leak risk.

### 5.4 Option D — Separate index per tenant/role

**Description.** Physically isolated indexes.
**Strengths.** Strong isolation.
**Weaknesses.** Index sprawl; role combinations explode; costly at this corpus scale.
Useful for hard tenant isolation only.
**Cost / effort.** High.

### 5.5 Option E — Filter ACL + document-level classification gate + audit

**Description.** Option A plus a classification gate (block restricted classes for
unauthorized roles even if metadata mislabelled) and access audit.
**Strengths.** Defence-in-depth for ACL; auditable.
**Weaknesses.** Slightly more config.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No ACL (all knowledge to all) | 19.PF-FT-AI-SECURITY.md §40 |
| User-supplied ACL context | ADR-D6-03 — server-owned only |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 19.PF-FT-AI-SECURITY.md §39–§45, 13.FP-FT-AI-RAG.md §33–§39, 14.PF-FT-AI-EMBEDDING-VECTOR.md §49–§51.

| Criterion | Weight | A: Filter ACL | B: Prompt ACL | C: Post-filter | D: Per-tenant index | E: Filter+class gate |
|---|---|---|---|---|---|---|
| EC-01 Correctness | 34 | 5 | 1 | 3 | 5 | 5 |
| EC-02 Non-bypassable | 24 | 5 | 1 | 4 | 5 | 5 |
| EC-03 Injection-safe | 16 | 5 | 2 | 4 | 5 | 5 |
| EC-04 Performance | 14 | 4 | 5 | 2 | 4 | 4 |
| EC-05 Granularity | 12 | 5 | 3 | 4 | 3 | 5 |
| **Weighted total** | **100** | **482** | **176** | **338** | **462** | **492** |

Totals (×20): **E = 492**, **A = 482**, **D = 462**, **C = 338**, **B = 176**.

**Sensitivity.** E (filter + classification gate + audit) edges A with a defence-in-depth
backstop against metadata mislabelling — worthwhile for FA safeguarding-sensitive
knowledge. Per-tenant indexes (D) remain the tool for hard tenant isolation where
required. Prompt-based ACL (B) is decisively rejected.

## 7. Decision

**PFF AI will enforce RAG ACL at retrieval time via injection-safe metadata filters
derived from the server-owned authz context, applied before/within the vector search,
plus a document-classification gate and access audit as defence-in-depth (Option E);
per-tenant/role index isolation (D) is used where hard isolation is required.** ACL is
never a prompt instruction (B); post-retrieval filtering (C) is rejected for leakage.

## 8. Architecture Detail

- Chunks carry security metadata (tenant/org/role/classification) from ingestion
  (ADR-D3-21; 13.FP-FT-AI-RAG.md §32); retrieval (ADR-D3-22) builds a bound OData/metadata filter
  from the authz context (ADR-D6-03), applied in the vector store (ADR-D3-24; 14.PF-FT-AI-EMBEDDING-VECTOR.md
  §49–§50); filter values parameterised (§51) to prevent filter injection.
- Classification gate blocks restricted classes for unauthorized roles even on metadata
  error; every retrieval's ACL decision is audited (ADR-D6-17).
- ACL failures fail closed (no results rather than over-return); ties to the guardrail
  pipeline (ADR-D6-09).

## 9. Consequences

### 9.1 Positive
- Structural, non-bypassable, granular, injection-safe RAG access control.
### 9.2 Negative
- Requires security metadata on all chunks + gate config.
### 9.3 Neutral
- Works with vector store (D3-24) and retrieval (D3-22).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of prompt ACL | Non-bypassable confidentiality | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Access authority from validated claims, not the model |
| Precedence chain | ACL uses authoritative authz context |
| Four-state separation | Security metadata separate from content |
| Versioned artefacts | ACL/filter policy versioned |
| Adam persona governs *how*, not *what* | Persona can't reveal unauthorized knowledge |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Unauthorized knowledge retrieved | Low | High | H | Filter + classification gate + tests | Security Architect | Low |
| RSK-02 | Filter injection bypasses ACL | Low | High | M | Bound/parameterised filters (§51) | Backend Lead | Low |
| RSK-03 | Chunk mislabelled in metadata | Med | High | H | Classification gate backstop + ingestion checks | AI Arch Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Cross-ACL retrieval leaks | 0 | > 0 | ACL tests | Continuous |
| QM-02 | Chunks with security metadata | 100% | < 100% | Ingestion audit | Per index build |
| QM-03 | Filter-injection bypasses | 0 | > 0 | Security tests | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Structural ACL closes knowledge-leak vector |
| Data classification touched | Restricted knowledge classes |
| Personal data / PII | Knowledge only (ADR-D3-20); still ACL-gated |
| Children's data and safeguarding | Safeguarding knowledge restricted by role |
| UK GDPR lawful basis and rights impact | Access control on knowledge |
| Audit and evidential requirements | ACL decisions audited |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 8 |
| Repository paths | `src/pf_ft_ai/rag/` |
| Configuration | ACL/filter policy; classification gate |
| Contracts / schemas | Security metadata schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-22, D3-24, D6-03, D3-20 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Filter applied before/within search from authz context | Integration test |
| AC-02 | No cross-ACL retrieval | ACL eval dataset (13.FP-FT-AI-RAG.md §131) |
| AC-03 | Filters injection-safe | Security test (§51) |
| AC-04 | Classification gate blocks mislabel leaks | Test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | ACL decisions; denied retrievals |
| Alerting | Any cross-ACL leak (sev-1) |
| Runbook | `docs/runbooks/rag-acl.md` |
| Failure mode and degradation | ACL uncertain → fail closed (no results) |
| Rollback | Policy revert |
| Support model impact | Security + AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| ACL filter + gate + audit | M | small | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Hard tenant isolation required | Compliance | Per-tenant index (Option D) |
| RT-02 | ACL-leak incident | Incident | CAR; tighten filters/gate |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 19.PF-FT-AI-SECURITY.md §39–§45; 13.FP-FT-AI-RAG.md §33–§39; 14.PF-FT-AI-EMBEDDING-VECTOR.md §49–§51 |
| Requirement IDs | SEC-RAG-ACL-* |
| Build phases | 8 |
| Code paths | `src/pf_ft_ai/rag/` |
| Configuration | ACL/filter/gate |
| Tests | ACL eval + injection suites |
| Upstream ADRs | ADR-D3-22, D3-24, D6-03 |
| Downstream ADRs | ADR-D3-20 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
