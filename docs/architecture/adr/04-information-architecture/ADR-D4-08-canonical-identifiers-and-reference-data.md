---
id: ADR-D4-08
title: Canonical identifier and reference-data strategy (WGS alignment)
domain: 4 Information
ws_ref: [WS-20]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [Integration Engineer, Domain SME, AI Architecture Lead]
reviewers: [AI Architecture Lead, Data Protection Officer]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-02, ADR-D4-03, ADR-D2-13, ADR-D2-15, ADR-D3-22]
source_docs:
  - "MD files/0 Workflow/pff_affiliation_e2e_flow.md — Phase 8 (Scenarios 13, 15, 16, 17)"
  - "MD files/3 Context & Integration/10 PF-FT-AI-ENTERPRISE-INTEGRATION.md §16, §21, §84"
  - "MD files/3 Context & Integration/8 PF-FT-AI-ERC-CONTEXT.md §11, §55, §70"
build_phases: [4, 10]
impacted_paths:
  - src/pf_ft_ai/erc/
  - src/pf_ft_ai/integration/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-08 — Canonical identifier and reference-data strategy (WGS alignment)

## 1. Summary

PFF AI will treat entity identifiers (club, team, official, affiliation number,
league, season) as **enterprise-owned canonical identifiers referenced by the AI,
never minted or reconciled by the AI itself**. Where PFF and WGS (the FA's national
database) hold parallel identities or diverge — notably the **PFF/WGS season-rollover
gap** (PFF rolls June 1st, WGS July 1st) — the AI surfaces the enterprise-provided
mapping and status faithfully, and never invents an affiliation number, guesses a
cross-system mapping, or asserts a season state the enterprise has not confirmed
(affiliation flow Phase 8; doc 10 §16, §21).

## 2. Context and Problem Statement

The affiliation flow's Phase 8 shows identifiers and reference data are enterprise
concerns: WGS *generates* the affiliation number (Scenario 15), attaches teams to an
existing WGS membership (Scenario 16), and there is a deliberate **1-month
PFF/WGS season mismatch** during which "PFF = new season, WGS = old season"
(Scenario 13), with last season shown as a static snapshot for 30 days. Doc 10 §21
maps enterprise responses to context; doc 8 §55/§70 cover duplicate detection and
referential integrity. If the AI platform mints IDs, caches a stale season as
current, or reconciles PFF↔WGS itself, it would be asserting business truth it does
not own — a direct Golden-Rule violation with real-world consequences (wrong
affiliation number, wrong season eligibility). This ADR fixes identifier and
reference-data handling.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Reference enterprise canonical IDs; never mint | affiliation Phase 8; doc 10 §21 |
| DR-F-02 | Represent PFF↔WGS mapping as provided, not inferred | affiliation Scenario 15–16 |
| DR-F-03 | Handle season-rollover mismatch faithfully | affiliation Scenario 13 |
| DR-C-01 | AI never asserts unconfirmed season/eligibility | CLAUDE.md; doc 8 §66 |
| DR-F-04 | Referential integrity across ERC sections | doc 8 §70 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise exposes canonical IDs + PFF/WGS mapping | Represent as unknown; ask enterprise | Integration review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Authority correctness (no minted/guessed IDs) | 34 | Golden Rule; real-world impact | Boundary tests |
| EC-02 | Season/mapping fidelity | 22 | Rollover mismatch correctness | Season-state tests |
| EC-03 | Referential integrity | 18 | Consistent cross-section refs | Integrity checks |
| EC-04 | Traceability of identifiers | 14 | Audit | ID provenance |
| EC-05 | Simplicity | 12 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Enterprise-canonical IDs referenced with provenance; enterprise-provided PFF↔WGS mapping; season state read from enterprise

**Description.** The AI stores enterprise IDs as opaque canonical references (with
provenance, ADR-D4-03); any PFF↔WGS mapping and current season come from enterprise
reads/events; during the rollover gap the AI reports whatever each system asserts, not
a reconciled view.
**Strengths.** Authority-correct; faithful to the mismatch; auditable.
**Weaknesses.** AI can't "helpfully" pre-resolve mappings — by design.
**Cost / effort.** Low-medium.

### 5.2 Option B — AI maintains its own ID mapping/reconciliation table

**Description.** The AI builds a PFF↔WGS crosswalk and resolves IDs itself.
**Strengths.** Fast cross-system answers.
**Weaknesses.** AI asserting a mapping it doesn't own; drifts from enterprise; the
rollover gap makes reconciliation ambiguous — high risk of wrong eligibility.
**Cost / effort.** High risk.

### 5.3 Option C — AI mints provisional identifiers (e.g. affiliation numbers) pending enterprise confirmation

**Description.** Generate provisional IDs for UX continuity.
**Strengths.** Immediate feedback.
**Weaknesses.** Directly violates "enterprise executes"; a provisional affiliation
number could be shown as real — unacceptable (Scenario 15: WGS generates it).
**Cost / effort.** Low; unacceptable.

### 5.4 Option D — Cache enterprise IDs/season as truth with long TTL

**Description.** Cache identity/season data aggressively.
**Strengths.** Fewer reads.
**Weaknesses.** Stale season during the 1-month gap → wrong state; violates freshness/
precedence.
**Cost / effort.** Low; unsafe for volatile reference data.

### 5.5 Option E — Enterprise-canonical + a read-only reference-data cache with volatility-aware TTL and event invalidation

**Description.** Option A plus caching of *stable* reference data (e.g. league lists)
with short/volatility-aware TTL (ADR-D4-12) and event-driven invalidation
(ADR-D4-06); volatile identity/season data always read live near decisions.
**Strengths.** A's correctness + performance for stable reference data.
**Weaknesses.** Must classify reference data by volatility.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| AI-generated surrogate keys used as business IDs | DR-C-01 — enterprise owns identity |
| Ignore PFF/WGS gap (treat as one season) | Scenario 13 — factual mismatch exists |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by affiliation Phase 8 (Scenarios
13, 15–17), doc 10 §21 and doc 8 §55/§70.

| Criterion | Weight | A: Canonical ref | B: AI reconciles | C: AI mints | D: Cache-as-truth | E: Canonical + vol-aware cache |
|---|---|---|---|---|---|---|
| EC-01 Authority correctness | 34 | 5 | 2 | 1 | 2 | 5 |
| EC-02 Season/mapping fidelity | 22 | 5 | 3 | 2 | 1 | 5 |
| EC-03 Referential integrity | 18 | 4 | 3 | 2 | 3 | 5 |
| EC-04 Traceability | 14 | 5 | 3 | 2 | 3 | 5 |
| EC-05 Simplicity | 12 | 5 | 2 | 4 | 4 | 4 |
| **Weighted total** | **100** | **482** | **256** | **196** | **228** | **492** |

Totals (×20): **E = 492**, **A = 482**, **B = 256**, **D = 228**, **C = 196**.

**Sensitivity.** E edges A by adding volatility-aware caching of *stable* reference
data without touching the authority correctness that dominates the score. B/C/D fail
the authority criterion decisively — they are exactly the failure modes Phase 8
guards against.

## 7. Decision

**PFF AI will reference enterprise-owned canonical identifiers with provenance and
never mint or reconcile them; PFF↔WGS mappings and current-season state come from
enterprise reads/events; stable reference data (e.g. league catalogues) may be cached
with volatility-aware TTL and event invalidation, while volatile identity/season data
is read live near decisions (Option E).** During the PFF/WGS rollover gap the AI
reports each system's asserted state faithfully and never presents a reconciled or
assumed season/eligibility. Minting (C), self-reconciliation (B) and cache-as-truth
(D) are rejected.

**Status rationale.** `Accepted` — affiliation Phase 8 and the Golden Rule govern this.

## 8. Architecture Detail

- Identifiers stored as opaque `CanonicalRef{system: PFF|WGS, entity_type, id,
  provenance}` inside ERC sections (ADR-D4-02); referential integrity checked across
  sections (doc 8 §70) using these refs.
- Season/eligibility read live from enterprise near any decision; the rollover gap
  (Scenario 13) surfaces both PFF and WGS states with explicit labels, never merged.
- Affiliation number and WGS membership are read from enterprise responses (Scenario
  15–16), never generated; a pending affiliation is shown as *pending*, not numbered,
  until WGS confirms.
- Stable reference data cached per ADR-D4-12 with volatility-aware TTL; invalidated by
  events (ADR-D4-06).

## 9. Consequences

### 9.1 Positive
- No wrong/invented IDs or season states; faithful to the real PFF/WGS gap.
### 9.2 Negative
- Cannot pre-resolve cross-system mappings for the user (by design); live reads for
  volatile data.
### 9.3 Neutral
- Reference-data caching handled by D4-12.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| "Helpful" AI-side reconciliation | Authority correctness | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | IDs/mappings/season owned by PFF/WGS; AI references only |
| Precedence chain | Volatile identity/season read live; cache only stable reference data with TTL |
| Four-state separation | Canonical refs live in ERC, not copied as truth into memory |
| Versioned artefacts | Reference-data cache policy versioned |
| Adam persona governs *how*, not *what* | Persona never states an unconfirmed affiliation number/season |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Stale season shown during rollover gap | Med | High | H | Live season reads; label PFF vs WGS | Integration Eng | Low |
| RSK-02 | AI shows provisional affiliation number as real | Low | High | M | Never mint; show pending until WGS confirms | AI Arch Lead | Low |
| RSK-03 | Reference-data cache stale | Low | Med | M | Volatility-aware TTL + event invalidation | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Minted/guessed IDs surfaced | 0 | > 0 | Tests/audit | Continuous |
| QM-02 | Wrong-season assertions | 0 | > 0 | Season tests | Per release |
| QM-03 | Referential-integrity failures | ≈ 0 | rising | Integrity checks | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None new |
| Data classification touched | Identifiers Internal; linked to Personal records |
| Personal data / PII | IDs reference persons (officials) — minimised |
| Children's data and safeguarding | Player/official IDs handled under ADR-D6-16 |
| UK GDPR lawful basis and rights impact | Accuracy principle upheld |
| Audit and evidential requirements | ID provenance recorded |
| Standards touched | ISO/IEC 27001, 42001, ISO 9001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 (ERC), 10 (WGS integration) |
| Repository paths | `src/pf_ft_ai/erc/`, `src/pf_ft_ai/integration/` |
| Configuration | Reference-data volatility/TTL map |
| Contracts / schemas | `CanonicalRef`; season-state model |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-02, ADR-D4-03, ADR-D2-13, ADR-D4-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No AI-minted business identifiers | Code + test |
| AC-02 | Rollover gap surfaces both states labelled | Scenario test |
| AC-03 | Pending affiliation shown without number until WGS confirms | Test |
| AC-04 | Cross-section referential integrity holds | Integrity test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | ID provenance coverage; season-mismatch handling |
| Alerting | Any minted-ID detection; wrong-season assertion |
| Runbook | `docs/runbooks/wgs-integration.md` |
| Failure mode and degradation | Unknown mapping → represent as unknown, ask enterprise |
| Rollback | Reference-data cache policy revert |
| Support model impact | Integration + domain SME |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Canonical-ref model + season handling | M | small | Build + live reads |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | PFF/WGS rollover rules change | Domain change | Update season handling |
| RT-02 | Wrong-season/ID incident | Incident | CAR; tighten live-read policy |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-20 |
| Specification sections | affiliation Phase 8 (Scenarios 13, 15–17); doc 10 §16, §21, §84; doc 8 §11, §55, §70 |
| Requirement IDs | REF-ID-* |
| Build phases | 4, 10 |
| Code paths | `src/pf_ft_ai/erc/`, `src/pf_ft_ai/integration/` |
| Configuration | reference-data volatility map |
| Tests | identifier + season-rollover suites |
| Upstream ADRs | ADR-D4-02, ADR-D2-13 |
| Downstream ADRs | ADR-D4-12, ADR-D2-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
