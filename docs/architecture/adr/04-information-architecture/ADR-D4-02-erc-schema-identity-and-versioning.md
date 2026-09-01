---
id: ADR-D4-02
title: ERC schema, identity and section-level versioning
domain: 4 Information
ws_ref: [WS-19]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Integration Engineer]
reviewers: [Principal Architect, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D2-12, ADR-D4-03, ADR-D4-04, ADR-D4-05, ADR-D4-06, ADR-D2-07]
source_docs:
  - "MD files/3 Context & Integration/8 PF-FT-AI-ERC-CONTEXT.md §8, §11, §12, §13, §14, §20, §21, §59, §67, §68, §69, §70, §71"
  - "MD files/1 Foundation/5. PF-FT-AI-STATE-MODEL.md §23, §25, §59"
build_phases: [4]
impacted_paths:
  - src/pf_ft_ai/erc/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-02 — ERC schema, identity and section-level versioning

## 1. Summary

PFF AI will model the Enterprise Runtime Context (ERC) as a **strongly-typed,
sectioned Pydantic structure** with a stable ERC identity, an overall ERC version and
**independent section-level versions**, plus a schema version — so that individual
context sections (club, teams, officials, insurance…) can be refreshed and validated
independently without rebuilding the whole ERC (8 PF-FT-AI-ERC-CONTEXT.md §11–§14, §20–§21, §59).
Validation is schema + cross-section + referential integrity (§67–§71).

## 2. Context and Problem Statement

8 PF-FT-AI-ERC-CONTEXT.md §11–§14 define ERC identity, version, schema version and metadata; §20–§21
define its high-level and dynamic-section structure; §59 defines section-level
versioning; §67–§71 define validation. ERC is the AI's structured, provenance-bearing
view of enterprise truth (ADR-D2-12) — but it is not the enterprise DB (§4), not
memory (§5), not cache (§6), not RAG (§7). Without a fixed schema/identity/versioning
model, sections cannot be refreshed independently (§60–§64), provenance/freshness
(ADR-D4-03) cannot attach cleanly, and validation is ad hoc. This ADR fixes the shape.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Sectioned structure with per-section identity/version | 8 PF-FT-AI-ERC-CONTEXT.md §20–§21, §59 |
| DR-F-02 | Stable ERC identity + version + schema version | 8 PF-FT-AI-ERC-CONTEXT.md §11–§13 |
| DR-F-03 | Schema, cross-section and referential validation | 8 PF-FT-AI-ERC-CONTEXT.md §67–§71 |
| DR-C-01 | ERC is typed at the boundary (Pydantic) | CLAUDE.md; ADR-D2-07 |
| DR-C-02 | ERC references enterprise truth; is not the DB | 8 PF-FT-AI-ERC-CONTEXT.md §4 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Section boundaries are stable enough to version independently | Coarser sections | Schema review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Independent section refresh/version | 26 | Efficiency + freshness | Section refresh possible? |
| EC-02 | Type safety & validation | 22 | Correctness at boundary | Validation coverage |
| EC-03 | Provenance/freshness attach-ability | 18 | Feeds ADR-D4-03 | Per-section metadata |
| EC-04 | Evolvability (schema versioning) | 16 | Change over time | Compat handling |
| EC-05 | Simplicity | 10 | Maintainability | Concepts |
| EC-06 | Performance (partial build) | 8 | Avoid full rebuilds | Rebuild scope |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Typed sectioned Pydantic ERC with section-level + schema versioning

**Description.** ERC = root model with typed sections; each section carries id,
version, provenance, freshness; root carries ERC id, ERC version, schema version;
validation at schema, cross-section and referential levels.
**Strengths.** Independent refresh; strong validation; provenance-ready; evolvable.
**Weaknesses.** More model surface.
**Cost / effort.** Medium.

### 5.2 Option B — Single flat typed ERC (no sections)

**Description.** One typed model, versioned as a whole.
**Strengths.** Simple.
**Weaknesses.** No independent section refresh; any change rebuilds/rerevalidates all;
provenance/freshness coarse.
**Cost / effort.** Low; inefficient.

### 5.3 Option C — Untyped dict/JSON ERC

**Description.** Loose dict of context.
**Strengths.** Flexible, fast to start.
**Weaknesses.** No boundary type safety (violates CLAUDE.md); ad-hoc validation;
error-prone.
**Cost / effort.** Low; unsafe.

### 5.4 Option D — Document-store-native ERC (mirror enterprise objects)

**Description.** Store ERC as enterprise-shaped documents.
**Strengths.** Close to source shape.
**Weaknesses.** Couples ERC to enterprise schemas; blurs "ERC is not the DB" (§4);
harder to attach AI-specific provenance/authority.
**Cost / effort.** Medium; coupling.

### 5.5 Option E — GraphQL-style composable context graph

**Description.** Model ERC as a queryable graph of context nodes.
**Strengths.** Flexible composition; fetch-what-you-need.
**Weaknesses.** Heavy; adds a query layer; over-engineered for a bounded set of
sections; versioning per node complex.
**Cost / effort.** High.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Reuse enterprise DTOs directly as ERC | 8 PF-FT-AI-ERC-CONTEXT.md §4/§33 — ERC needs normalization + AI metadata |
| No schema version | 8 PF-FT-AI-ERC-CONTEXT.md §13 — evolution unmanageable |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 8 PF-FT-AI-ERC-CONTEXT.md §11–§21/§59/§67–§71.

| Criterion | Weight | A: Typed sectioned | B: Flat typed | C: Untyped | D: Doc-native | E: Graph |
|---|---|---|---|---|---|---|
| EC-01 Section refresh | 26 | 5 | 2 | 2 | 4 | 5 |
| EC-02 Type safety/validation | 22 | 5 | 5 | 1 | 3 | 4 |
| EC-03 Provenance attach | 18 | 5 | 3 | 2 | 3 | 4 |
| EC-04 Evolvability | 16 | 5 | 3 | 2 | 3 | 4 |
| EC-05 Simplicity | 10 | 4 | 5 | 4 | 3 | 2 |
| EC-06 Partial-build perf | 8 | 5 | 2 | 3 | 4 | 5 |
| **Weighted total** | **100** | **492** | **342** | **196** | **334** | **414** |

Totals (×20): **A = 492**, **E = 414**, **B = 342**, **D = 334**, **C = 196**.

**Sensitivity.** A leads E by 78. E (graph) is the only near contender and could be
reconsidered if context composition needs grow far more dynamic (RT-01), but is
over-engineered for a bounded, well-known set of ERC sections.

## 7. Decision

**PFF AI will model ERC as a typed, sectioned Pydantic structure with ERC identity,
ERC version, schema version and independent section-level versions, validated at
schema, cross-section and referential levels (Option A).** Each section carries the
provenance/freshness/authority metadata that ADR-D4-03 requires, enabling independent
refresh (ADR-D4-06). Untyped (C) violates boundary typing; flat (B) blocks
independent refresh; doc-native (D) couples to enterprise schemas; graph (E) is
over-engineered.

**Status rationale.** `Accepted` — 8 PF-FT-AI-ERC-CONTEXT.md §11–§21 govern this.

## 8. Architecture Detail

- `src/pf_ft_ai/erc/`: `EnterpriseRuntimeContext` root (id, erc_version,
  schema_version, metadata) containing typed sections (e.g. `ClubSection`,
  `TeamsSection`, `OfficialsSection`), each with `section_version`, `provenance`,
  `freshness`, `authority_level` (ADR-D4-03).
- **Validation** (8 PF-FT-AI-ERC-CONTEXT.md §67–§71): Pydantic schema validation, cross-section rules
  (§69), referential integrity (§70), producing an ERC validation result with
  warnings/errors (§71–§73).
- **Construction** feeds from ADR-D4-04 (collection/batching) and ADR-D2-12; sections
  refresh via ADR-D4-06 patches without full rebuild (§60–§61).

## 9. Consequences

### 9.1 Positive
- Independent, validated, provenance-bearing sections; efficient refresh.
### 9.2 Negative
- More models to define and evolve.
### 9.3 Neutral
- Anchors ERC provenance/collection/failure/refresh ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Flat-model simplicity | Section independence + validation | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | ERC references enterprise truth; is not the DB (§4) |
| Precedence chain | ERC authority levels feed precedence (ADR-D4-03) |
| Four-state separation | ERC is the enterprise-reference view, distinct from memory/cache (§5–§6) |
| Versioned artefacts | ERC + section + schema versions |
| Adam persona governs *how*, not *what* | ERC carries the *what*; persona narrates it |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Schema drift breaks consumers | Med | Med | M | Schema version + compat tests | Backend Lead | Low |
| RSK-02 | Section boundaries wrong | Low | Med | M | Review vs enterprise domains (ADR-D4-07) | AI Arch Lead | Low |
| RSK-03 | Referential integrity gaps | Low | Med | M | Cross-section validation (§69–§70) | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | ERC validation pass rate | ≥ 99% | < 97% | ERC validator | Continuous |
| QM-02 | Section-level refresh (no full rebuild) | supported | regression | Tests | Per release |
| QM-03 | Schema version present on every ERC | 100% | < 100% | Runtime check | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Typed validation reduces malformed-data risk |
| Data classification touched | ERC sections may be Confidential/Personal |
| Personal data / PII | Minimised to needed sections (ADR-D6-07) |
| Children's data and safeguarding | Safeguarding sections classified + access-controlled |
| UK GDPR lawful basis and rights impact | Section granularity aids minimisation |
| Audit and evidential requirements | Section versions + provenance auditable |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 |
| Repository paths | `src/pf_ft_ai/erc/` |
| Configuration | Section schema definitions |
| Contracts / schemas | ERC + section Pydantic models |
| Migration | Schema version migration |
| Dependencies on other ADRs | ADR-D2-12, ADR-D4-03, ADR-D4-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | ERC is typed and sectioned | Model review |
| AC-02 | Sections refreshable independently | Unit test |
| AC-03 | Schema + cross-section + referential validation runs | Tests (§67–§71) |
| AC-04 | Schema version enforced | Runtime check |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Validation results; section refresh metrics |
| Alerting | Validation failure spikes |
| Runbook | `docs/runbooks/erc.md` |
| Failure mode and degradation | Invalid section → warning/error handling (ADR-D4-05) |
| Rollback | Schema version revert |
| Support model impact | Backend + integration |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| ERC models + validation | M | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Context composition needs highly dynamic | Design review | Evaluate graph model (Option E) |
| RT-02 | Frequent schema-compat breaks | QM-01 | Revisit section boundaries/versioning |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 |
| Specification sections | 8 PF-FT-AI-ERC-CONTEXT.md §8, §11–§14, §20–§21, §59, §67–§71; 5. PF-FT-AI-STATE-MODEL.md §23, §25, §59 |
| Requirement IDs | ERC-SCHEMA-* |
| Build phases | 4 |
| Code paths | `src/pf_ft_ai/erc/` |
| Configuration | section schemas |
| Tests | ERC validation suite |
| Upstream ADRs | ADR-D2-12 |
| Downstream ADRs | ADR-D4-03, ADR-D4-04, ADR-D4-05, ADR-D4-06 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
