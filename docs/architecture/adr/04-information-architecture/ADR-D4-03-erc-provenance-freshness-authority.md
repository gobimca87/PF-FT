---
id: ADR-D4-03
title: ERC provenance, freshness policy and authority levels
domain: 4 Information
ws_ref: [WS-19]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Backend Lead, Integration Engineer, Security Architect]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D4-02, ADR-D2-12, ADR-D1-03, ADR-D4-06, ADR-D4-12]
source_docs:
  - "MD files/3 Context & Integration/8 PFF-FA-AI-ERC-CONTEXT.md §15, §16, §17, §18, §19, §65, §66"
  - "MD files/1 Foundation/5. PFF-FA-AI-STATE-MODEL.md §26, §28"
build_phases: [4]
impacted_paths:
  - src/pff_fa_ai/erc/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-03 — ERC provenance, freshness policy and authority levels

## 1. Summary

Every ERC section will carry **provenance** (which enterprise source produced it, and
when), a **freshness** assessment against a per-section policy, and an explicit
**authority level** — so the platform can reason about how much to trust each section
and where it sits in the precedence chain (8 PFF-FA-AI-ERC-CONTEXT.md §15–§19, §65–§66). Stale or
lower-authority context is treated accordingly; the enterprise API/event remains the
top authority, and ERC never presents inferred or aged data as if freshly
authoritative.

## 2. Context and Problem Statement

8 PFF-FA-AI-ERC-CONTEXT.md §15–§16 make provenance a principle; §17–§18 define freshness and its policy;
§19 defines authority levels; §65–§66 tie ERC to transaction state and uncertainty.
The precedence chain (ADR-D1-03) requires the platform to know *how authoritative* a
given datum is. Without provenance/freshness/authority on each section, the platform
cannot tell fresh authoritative data from an aged cache-derived value, and could
present stale context as current truth — a correctness and trust failure. This ADR
fixes the metadata and policy that make trust computable.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Provenance on every section (source + timestamp) | 8 PFF-FA-AI-ERC-CONTEXT.md §15–§16 |
| DR-F-02 | Freshness assessed vs per-section policy | 8 PFF-FA-AI-ERC-CONTEXT.md §17–§18 |
| DR-F-03 | Explicit authority level per section | 8 PFF-FA-AI-ERC-CONTEXT.md §19; ADR-D1-03 |
| DR-C-01 | Enterprise API/event is top authority | CLAUDE.md |
| DR-F-04 | Transaction-uncertainty reflected in ERC | 8 PFF-FA-AI-ERC-CONTEXT.md §65–§66 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Sources expose usable timestamps/etags | Derive freshness from fetch time only | Integration review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Trust computability (provenance+authority) | 30 | Enables precedence reasoning | Metadata completeness |
| EC-02 | Freshness accuracy | 22 | Avoid stale-as-fresh | Freshness correctness |
| EC-03 | Precedence alignment | 20 | Golden Rule | Authority mapping |
| EC-04 | Overhead/cost | 14 | Metadata cost | Size/latency |
| EC-05 | Simplicity | 14 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Per-section provenance + freshness policy + authority level

**Description.** Each section stamped with source id, fetch/source timestamp, an
authority level enum, and evaluated against a per-section freshness TTL/policy;
transaction-uncertain sections flagged (§66).
**Strengths.** Full trust computability; precedence-aligned; granular.
**Weaknesses.** Metadata overhead per section.
**Cost / effort.** Low-medium.

### 5.2 Option B — ERC-level provenance/freshness only (not per section)

**Description.** One provenance/freshness for the whole ERC.
**Strengths.** Less metadata.
**Weaknesses.** Sections have different sources/volatility; coarse freshness
mislabels fresh sections as stale and vice versa.
**Cost / effort.** Low; inaccurate.

### 5.3 Option C — Timestamps only, no authority levels

**Description.** Record when fetched; no authority classification.
**Strengths.** Simple.
**Weaknesses.** Can't reason about precedence between sources; §19 unmet.
**Cost / effort.** Low; insufficient.

### 5.4 Option D — Freshness by TTL only (no source-timestamp reasoning)

**Description.** Treat any section older than TTL as stale regardless of source
change signals.
**Strengths.** Trivial.
**Weaknesses.** Ignores etags/change events; over-refreshes fresh data / misses early
changes; less accurate than policy that uses source signals.
**Cost / effort.** Low; blunt.

### 5.5 Option E — Confidence-scored provenance (probabilistic trust)

**Description.** Attach a numeric confidence to each section.
**Strengths.** Nuanced.
**Weaknesses.** Enterprise authority is categorical, not probabilistic; a made-up
confidence on authoritative data is misleading; better to use discrete authority
levels + freshness. Confidence belongs to RAG/memory (9 PFF-FA-AI-MEMORY-CACHE.md §28), not ERC.
**Cost / effort.** Medium; conceptually wrong for ERC.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| No provenance | 8 PFF-FA-AI-ERC-CONTEXT.md §16 — provenance is a principle |
| Infer freshness from SLM | Precedence — SLM is lowest authority |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 8 PFF-FA-AI-ERC-CONTEXT.md §15–§19/§65–§66 and the
precedence chain.

| Criterion | Weight | A: Per-section full | B: ERC-level | C: Timestamps only | D: TTL only | E: Confidence-scored |
|---|---|---|---|---|---|---|
| EC-01 Trust computability | 30 | 5 | 3 | 2 | 2 | 4 |
| EC-02 Freshness accuracy | 22 | 5 | 2 | 3 | 3 | 3 |
| EC-03 Precedence alignment | 20 | 5 | 3 | 2 | 2 | 3 |
| EC-04 Overhead | 14 | 3 | 5 | 5 | 5 | 3 |
| EC-05 Simplicity | 14 | 4 | 5 | 4 | 4 | 2 |
| **Weighted total** | **100** | **458** | **336** | **300** | **300** | **316** |

Totals (×20): **A = 458**, **B = 336**, **E = 316**, **C = 300**, **D = 300**.

**Sensitivity.** A leads by > 120. Its only weakness is overhead (EC-04), which is
minor per section; no re-weighting overturns the trust/precedence advantage.

## 7. Decision

**PFF AI will stamp every ERC section with provenance (source id + source/fetch
timestamp), an explicit authority level, and a freshness assessment against a
per-section policy that uses source change-signals where available (Option A);
transaction-uncertain sections are flagged per 8 PFF-FA-AI-ERC-CONTEXT.md §66.** Authority levels map into
the precedence chain (enterprise API/event highest). ERC-level-only (B), timestamps-
only (C), TTL-only (D) are insufficient; probabilistic confidence (E) is conceptually
wrong for authoritative context.

**Status rationale.** `Accepted` — 8 PFF-FA-AI-ERC-CONTEXT.md §15–§19 govern this.

## 8. Architecture Detail

- Section metadata: `provenance{source_id, source_ts, fetch_ts}`, `authority_level`
  (enum ordered per precedence), `freshness{policy_id, assessed_at, state:
  FRESH|AGING|STALE}`, `transaction_uncertain: bool` (8 PFF-FA-AI-ERC-CONTEXT.md §66).
- Freshness policies per section (8 PFF-FA-AI-ERC-CONTEXT.md §18) keyed to data volatility; where the source
  exposes etag/last-modified/change events, freshness uses them; else fetch-age vs TTL.
- On use, the context assembler (ADR-D3-25) and consumers respect authority + freshness;
  stale/uncertain sections trigger refresh (ADR-D4-06) or explicit handling.

## 9. Consequences

### 9.1 Positive
- Trust and precedence become computable per section; stale data can't pose as fresh.
### 9.2 Negative
- Per-section metadata overhead.
### 9.3 Neutral
- Feeds refresh (D4-06) and cache TTL (D4-12) decisions.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Metadata leanness | Computable trust & freshness | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Authority levels keep enterprise on top |
| Precedence chain | Authority level is the section's place in the chain |
| Four-state separation | Provenance marks enterprise-reference nature of ERC |
| Versioned artefacts | Freshness policies versioned |
| Adam persona governs *how*, not *what* | Persona must not present stale as fresh |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Stale section used as fresh | Med | High | H | Freshness state + assembler respects it | AI Arch Lead | Low |
| RSK-02 | Source lacks change signals | Med | Med | M | Fall back to TTL-based freshness | Integration Eng | Low |
| RSK-03 | Authority misclassification | Low | High | M | Authority mapping review + tests | Principal Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Sections with complete provenance | 100% | < 100% | ERC validator | Continuous |
| QM-02 | Stale-served-as-fresh incidents | 0 | > 0 | Traces/audit | Continuous |
| QM-03 | Freshness assessment coverage | 100% | < 100% | Runtime | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | None new |
| Data classification touched | Metadata Internal; data as per section |
| Personal data / PII | Provenance aids lawful-basis/audit |
| Children's data and safeguarding | Freshness matters for safeguarding-sensitive context |
| UK GDPR lawful basis and rights impact | Provenance supports accountability |
| Audit and evidential requirements | Provenance is evidential |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 |
| Repository paths | `src/pff_fa_ai/erc/` |
| Configuration | Per-section freshness policies |
| Contracts / schemas | Section metadata schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-02, ADR-D2-12, ADR-D4-06 |
| Effort estimate | S–M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Every section has provenance + authority + freshness | Validator test |
| AC-02 | Assembler respects freshness/authority | Integration test |
| AC-03 | Transaction-uncertain flagged | Test (§66) |
| AC-04 | Authority maps to precedence order | Unit test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Freshness distribution; stale-section rate |
| Alerting | High stale rate; provenance gaps |
| Runbook | `docs/runbooks/erc.md` |
| Failure mode and degradation | Stale/uncertain → refresh or explicit handling |
| Rollback | Freshness policy revert |
| Support model impact | Integration + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Metadata + freshness engine | S | negligible | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Stale-as-fresh incident | Incident | CAR; tighten freshness policy |
| RT-02 | Sources add change events | Integration | Switch section to event-driven freshness (ADR-D4-06) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 |
| Specification sections | 8 PFF-FA-AI-ERC-CONTEXT.md §15–§19, §65–§66; 5. PFF-FA-AI-STATE-MODEL.md §26, §28 |
| Requirement IDs | ERC-PROV-* |
| Build phases | 4 |
| Code paths | `src/pff_fa_ai/erc/` |
| Configuration | freshness policies |
| Tests | provenance/freshness suites |
| Upstream ADRs | ADR-D4-02, ADR-D1-03 |
| Downstream ADRs | ADR-D4-06, ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
