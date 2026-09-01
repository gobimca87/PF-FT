---
id: ADR-D4-06
title: ERC invalidation, patching and event-driven refresh
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
related_adrs: [ADR-D4-02, ADR-D4-03, ADR-D2-16, ADR-D2-18, ADR-D4-12]
source_docs:
  - "MD files/3 Context & Integration/8 PFF-FA-AI-ERC-CONTEXT.md §60, §61, §62, §63, §64, §65, §66"
  - "MD files/1 Foundation/5. PFF-FA-AI-STATE-MODEL.md §67"
build_phases: [4, 5]
impacted_paths:
  - src/pff_fa_ai/erc/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-06 — ERC invalidation, patching and event-driven refresh

## 1. Summary

PFF AI will keep ERC current through **section-level invalidation and patching** and
**event-driven refresh**: when an enterprise event indicates a change (via Azure
Service Bus, ADR-D2-16), only the affected ERC section is invalidated and re-collected
(patched), not the whole ERC (8 PFF-FA-AI-ERC-CONTEXT.md §60–§64). On-demand freshness checks (ADR-D4-03)
trigger the same section refresh. Refresh never fabricates — it re-reads from the
authoritative source.

## 2. Context and Problem Statement

8 PFF-FA-AI-ERC-CONTEXT.md §60–§61 define the ERC update strategy and patch model; §62–§63 define
invalidation and refresh; §64 defines event-driven refresh; §65–§66 tie ERC to
transaction state/uncertainty; 5. PFF-FA-AI-STATE-MODEL.md §67 covers state and enterprise events. Because
ERC is a reference view of enterprise truth (ADR-D2-12), it can go stale as the
enterprise changes. Rebuilding the whole ERC on any change is wasteful and slow;
never refreshing risks stale-as-fresh (ADR-D4-03). This ADR fixes how ERC stays
current efficiently and safely.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Section-level invalidation + patch | 8 PFF-FA-AI-ERC-CONTEXT.md §60–§62 |
| DR-F-02 | Event-driven refresh from Service Bus | 8 PFF-FA-AI-ERC-CONTEXT.md §64; ADR-D2-16 |
| DR-F-03 | On-demand refresh when freshness stale | ADR-D4-03; 8 PFF-FA-AI-ERC-CONTEXT.md §63 |
| DR-C-01 | Refresh re-reads source; never fabricates | 8 PFF-FA-AI-ERC-CONTEXT.md; CLAUDE.md |
| DR-C-02 | Consume events reliably (idempotent) | ADR-D2-18 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Enterprise emits change events for key entities | Fall back to freshness-TTL refresh | Event catalogue review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Freshness/correctness | 28 | Avoid stale ERC | Staleness window |
| EC-02 | Efficiency (avoid full rebuild) | 22 | Cost/latency | Refresh scope |
| EC-03 | Reliability (no missed/duplicate refresh) | 20 | Idempotent consume | Missed/dup rate |
| EC-04 | Timeliness (react to change fast) | 16 | UX/correctness | Event-to-refresh lag |
| EC-05 | Simplicity | 14 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Event-driven section patch + on-demand freshness refresh

**Description.** Subscribe to enterprise change events (ADR-D2-16); map each to the
affected ERC section(s); invalidate + re-collect just those (§61–§62); also refresh a
section on-demand when its freshness policy says stale (ADR-D4-03). Idempotent
consume (ADR-D2-18).
**Strengths.** Fresh, efficient, timely, reliable.
**Weaknesses.** Requires event→section mapping + idempotent consumer.
**Cost / effort.** Medium.

### 5.2 Option B — Full ERC rebuild on any change/expiry

**Description.** Rebuild the whole ERC when anything changes or TTL expires.
**Strengths.** Simple; always consistent.
**Weaknesses.** Wasteful; slow; hammers enterprise APIs.
**Cost / effort.** Low; inefficient.

### 5.3 Option C — TTL-only refresh (no events)

**Description.** Refresh sections purely on TTL expiry.
**Strengths.** Simple; no event plumbing.
**Weaknesses.** Not timely — changes unseen until TTL; stale window; misses the
Service Bus capability the platform already has.
**Cost / effort.** Low; less fresh.

### 5.4 Option D — Poll enterprise APIs for changes

**Description.** Periodically poll for changes.
**Strengths.** No event contract needed.
**Weaknesses.** Load on enterprise APIs; latency; wasteful vs events.
**Cost / effort.** Medium; inefficient.

### 5.5 Option E — Event-driven full invalidation (event triggers whole-ERC refresh)

**Description.** Use events but rebuild the entire ERC on any event.
**Strengths.** Timely; simpler mapping.
**Weaknesses.** Loses the efficiency of section patch; unnecessary reads.
**Cost / effort.** Low-medium; wasteful.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Never refresh (build once) | ADR-D4-03 — stale-as-fresh |
| Patch ERC from event *payload* as truth | DR-C-01 — re-read source, don't trust event body as full truth |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 8 PFF-FA-AI-ERC-CONTEXT.md §60–§66, ADR-D2-16/18 and
the freshness model (ADR-D4-03).

| Criterion | Weight | A: Event patch + on-demand | B: Full rebuild | C: TTL-only | D: Poll | E: Event full-rebuild |
|---|---|---|---|---|---|---|
| EC-01 Freshness | 28 | 5 | 4 | 3 | 4 | 5 |
| EC-02 Efficiency | 22 | 5 | 1 | 4 | 2 | 2 |
| EC-03 Reliability | 20 | 4 | 4 | 4 | 3 | 4 |
| EC-04 Timeliness | 16 | 5 | 2 | 2 | 3 | 5 |
| EC-05 Simplicity | 14 | 3 | 5 | 5 | 3 | 4 |
| **Weighted total** | **100** | **452** | **312** | **356** | **300** | **384** |

Totals (×20): **A = 452**, **E = 384**, **C = 356**, **B = 312**, **D = 300**.

**Sensitivity.** A leads E by 68 on efficiency (section patch vs full rebuild). Where
an entity has no change event (DR-A-01 false), that section falls back to C (TTL) —
A subsumes C as a fallback per section.

## 7. Decision

**PFF AI will refresh ERC by event-driven section-level patching plus on-demand
freshness refresh (Option A).** Enterprise change events from Azure Service Bus
(ADR-D2-16) are mapped to affected ERC sections and only those sections are
invalidated and re-collected (re-reading the authoritative source, never trusting the
event body as full truth); sections lacking change events fall back to TTL-based
freshness refresh (ADR-D4-03). Consumption is idempotent (ADR-D2-18). Full-rebuild
(B/E) is wasteful; TTL-only (C) and polling (D) are less timely/efficient.

**Status rationale.** `Accepted` — 8 PFF-FA-AI-ERC-CONTEXT.md §60–§64 govern this.

## 8. Architecture Detail

- Event→section mapping registry; a refresh handler invalidates the section (§62),
  re-collects it via the planner (ADR-D4-04), re-validates (ADR-D4-02) and bumps the
  section version + freshness (ADR-D4-03).
- Idempotent consume (ADR-D2-18): dedup by event id; at-least-once tolerated.
- Transaction-uncertainty (§65–§66): an event indicating an in-flight/uncertain
  transaction marks the section `transaction_uncertain` until a confirming read.
- Cache coherence: refreshing a section invalidates related cache entries (ADR-D4-12).

## 9. Consequences

### 9.1 Positive
- Fresh, timely ERC with minimal enterprise-read cost.
### 9.2 Negative
- Event mapping + idempotent consumer to build/maintain.
### 9.3 Neutral
- Ties ERC to the eventing platform (D2-16/18) and cache (D4-12).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of TTL-only | Timeliness + efficiency | AI Arch Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Refresh re-reads authoritative source; event body is a signal, not truth |
| Precedence chain | Keeps ERC aligned with enterprise state |
| Four-state separation | Refresh operates on the ERC plane only |
| Versioned artefacts | Section versions bumped on refresh |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Missed event → stale section | Low | High | M | Idempotent consume + TTL fallback | Integration Eng | Low |
| RSK-02 | Event body trusted as full truth | Low | High | M | Always re-read source on refresh | AI Arch Lead | Low |
| RSK-03 | Refresh storm on event burst | Low | Med | M | Debounce/coalesce per section | SRE | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Event-to-refresh lag p95 | ≤ target | breach | App Insights | Continuous |
| QM-02 | Stale-section rate | ≈ 0 | rising | Freshness metrics | Continuous |
| QM-03 | Duplicate-refresh suppression | 100% | < 100% | Consumer metrics | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Event consumer (validated envelope, ADR-D2-17) |
| Data classification touched | As per refreshed sections |
| Personal data / PII | Re-read minimised to affected section |
| Children's data and safeguarding | Safeguarding sections refreshed under authorization |
| UK GDPR lawful basis and rights impact | Accuracy upheld by timely refresh |
| Audit and evidential requirements | Refresh events audited |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 4 (ERC), 5 (eventing) |
| Repository paths | `src/pff_fa_ai/erc/` |
| Configuration | Event→section map; debounce; TTL fallback |
| Contracts / schemas | Event envelope (ADR-D2-17) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D4-02, ADR-D4-03, ADR-D2-16, ADR-D2-18 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Event refreshes only affected section | Integration test |
| AC-02 | Refresh re-reads source (not event body) | Test |
| AC-03 | Idempotent under duplicate events | Test (ADR-D2-18) |
| AC-04 | No-event entities fall back to TTL refresh | Test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Event lag, refresh counts, stale rate |
| Alerting | Lag breach; stale spike |
| Runbook | `docs/runbooks/erc.md` |
| Failure mode and degradation | Consumer down → TTL fallback keeps bounded freshness |
| Rollback | Disable event refresh; TTL-only |
| Support model impact | Integration + SRE |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Refresh handler + mapping | M | small | Build + event processing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Enterprise lacks needed change events | Integration | Extend event catalogue or accept TTL fallback |
| RT-02 | Refresh storms | QM/metrics | Tune debounce/coalescing |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 |
| Specification sections | 8 PFF-FA-AI-ERC-CONTEXT.md §60–§66; 5. PFF-FA-AI-STATE-MODEL.md §67 |
| Requirement IDs | ERC-REFRESH-* |
| Build phases | 4, 5 |
| Code paths | `src/pff_fa_ai/erc/` |
| Configuration | event→section map, TTL fallback |
| Tests | refresh + idempotency suites |
| Upstream ADRs | ADR-D4-02, ADR-D2-16 |
| Downstream ADRs | ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
