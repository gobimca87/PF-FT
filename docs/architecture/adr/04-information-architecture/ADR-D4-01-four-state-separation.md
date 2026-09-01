---
id: ADR-D4-01
title: Four-state separation — conversation / session / workflow / enterprise
domain: 4 Information
ws_ref: [WS-19]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Principal Architect
contributors: [AI Architecture Lead, Backend Lead]
reviewers: [AI Architecture Lead, Security Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D2-07, ADR-D2-12, ADR-D4-10, ADR-D4-11, ADR-D4-12, ADR-D1-03]
source_docs:
  - "MD files/1 Foundation/5. PF-FT-AI-STATE-MODEL.md §2, §3, §4, §5, §49, §50, §53, §54"
  - "MD files/2 Agent Runtime/6 PF-FT-AI-CONVERSATION-SESSION.md §6, §54"
  - "MD files/3 Context & Integration/9 PF-FT-AI-MEMORY-CACHE.md §3, §4"
build_phases: [3, 7]
impacted_paths:
  - src/pf_ft_ai/state/
classification: Internal
review_due: 2027-08-22
---

# ADR-D4-01 — Four-state separation — conversation / session / workflow / enterprise

## 1. Summary

PFF AI will keep four state concepts **strictly separate in code, storage and
lifecycle**: Conversation State, Session State, Workflow/Agent State and Enterprise
Business State — never conflating them, never letting one masquerade as another.
Enterprise Business State is owned entirely by PFF and is only *referenced* (via ERC),
never copied as truth. This is the information-architecture backbone that makes the
Golden Rule and precedence chain enforceable (5. PF-FT-AI-STATE-MODEL.md §2–§5; CLAUDE.md).

## 2. Context and Problem Statement

5. PF-FT-AI-STATE-MODEL.md §2–§5 define the state hierarchy and ownership boundary; §49–§54 define the
composite runtime state, consistency rules and state-store separation; 9 PF-FT-AI-MEMORY-CACHE.md §3–§4
draw the memory/cache/ERC boundary; CLAUDE.md mandates the four states "never be
conflated in code." The failure this prevents: a developer stashes an enterprise fact
(e.g. affiliation status) in conversation memory or session state, and the platform
starts treating a stale copy as truth — violating precedence and creating
correctness, security and audit hazards. Without an explicit, enforced separation,
the boundary erodes silently.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Four states distinguishable by type, store and lifecycle | 5. PF-FT-AI-STATE-MODEL.md §4, §54 |
| DR-C-01 | Enterprise state owned by PFF; only referenced, never copied as truth | 5. PF-FT-AI-STATE-MODEL.md §5; 9 PF-FT-AI-MEMORY-CACHE.md §17; ADR-D1-03 |
| DR-C-02 | Each state has its own ownership, TTL, classification | 5. PF-FT-AI-STATE-MODEL.md §55–§56 |
| DR-N-01 | Boundary enforced, not merely documented | CLAUDE.md |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Distinct stores per state class is feasible | Logical namespaces on shared store | ADR-D4-10 |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Enforceability of separation | 30 | The whole point | Type/store/CI checks |
| EC-02 | Precedence & correctness protection | 24 | Prevents stale-truth | Boundary tests |
| EC-03 | Clarity of mental model | 16 | Team follows it | Ambiguity |
| EC-04 | Independent lifecycle/TTL/classification | 16 | Security & retention | Per-state config |
| EC-05 | Simplicity/cost | 14 | Avoid over-engineering | # stores/abstractions |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Four distinct typed state models + separated stores/namespaces + CI enforcement

**Description.** Distinct TypedDict/Pydantic models per state class (ADR-D2-07),
stored in separated stores or namespaces (ADR-D4-10), with import/lint/architecture
tests forbidding cross-contamination and forbidding enterprise truth in
conversation/session/workflow state.
**Strengths.** Enforceable; precedence-safe; clear; per-state lifecycle.
**Weaknesses.** More models/config than a blob.
**Cost / effort.** Medium.

### 5.2 Option B — Single unified state object

**Description.** One big state blob holding everything.
**Strengths.** Simple to pass around.
**Weaknesses.** Conflation by construction; no per-state TTL/classification; stale
enterprise copies inevitable; violates CLAUDE.md.
**Cost / effort.** Low, unsafe.

### 5.3 Option C — Two-way split (AI runtime state vs enterprise state)

**Description.** Separate enterprise from everything AI, but merge conversation/
session/workflow.
**Strengths.** Protects enterprise truth boundary.
**Weaknesses.** Conflates conversation/session/workflow — different lifecycles/TTLs/
owners; 5. PF-FT-AI-STATE-MODEL.md requires four.
**Cost / effort.** Low-medium; insufficient.

### 5.4 Option D — Separation by convention only (docs, no enforcement)

**Description.** Four states in guidelines; no code guards.
**Strengths.** No tooling.
**Weaknesses.** Erodes silently; the exact failure mode. CLAUDE.md wants enforcement.
**Cost / effort.** Low; ineffective.

### 5.5 Option E — Event-sourced single log with projections per state

**Description.** One event log; derive four state projections.
**Strengths.** Strong audit; single write path.
**Weaknesses.** Heavy for this platform; still needs the four projections separated;
enterprise truth must not be event-sourced here (it's PFF's). Over-engineered now.
**Cost / effort.** High.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Copy enterprise state into memory for speed | DR-C-01 — stale truth (use cache with TTL instead, ADR-D4-12) |
| Merge session into conversation | Different lifetimes (6 PF-FT-AI-CONVERSATION-SESSION.md §16) |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 5. PF-FT-AI-STATE-MODEL.md §2–§5/§49–§56 and 9 PF-FT-AI-MEMORY-CACHE.md
§3–§4.

| Criterion | Weight | A: 4 typed + enforced | B: Unified blob | C: Two-way | D: Convention | E: Event-sourced |
|---|---|---|---|---|---|---|
| EC-01 Enforceability | 30 | 5 | 1 | 3 | 2 | 4 |
| EC-02 Precedence protection | 24 | 5 | 1 | 4 | 3 | 4 |
| EC-03 Clarity | 16 | 5 | 3 | 3 | 3 | 3 |
| EC-04 Lifecycle/TTL | 16 | 5 | 1 | 3 | 3 | 4 |
| EC-05 Simplicity/cost | 14 | 4 | 5 | 4 | 5 | 2 |
| **Weighted total** | **100** | **488** | **192** | **342** | **306** | **370** |

Totals (×20): **A = 488**, **E = 370**, **C = 342**, **D = 306**, **B = 192**.

**Sensitivity.** A leads by > 100. E (event-sourcing) is the only other high scorer
and could be revisited if audit requirements grow (RT-01), but is over-engineered for
current needs. No re-weighting favours the conflating options.

## 7. Decision

**PFF AI will maintain four strictly-separated state classes — Conversation,
Session, Workflow/Agent, Enterprise Business — with distinct typed models, separated
stores/namespaces and CI-enforced boundaries (Option A).** Enterprise Business State
is owned by PFF and only referenced via ERC (ADR-D2-12), never copied as truth into
the other three. Cross-contamination and enterprise-truth-in-AI-state are blocked by
architecture-fitness tests. Options B/C/D fail enforcement or completeness; E is
deferred as over-engineered.

**Status rationale.** `Accepted` — mandated by 5. PF-FT-AI-STATE-MODEL.md and CLAUDE.md; ADR records
enforcement design.

## 8. Architecture Detail

- **Models** (ADR-D2-07): TypedDict for LangGraph-internal workflow/agent state;
  Pydantic at boundaries; distinct types per state class in `src/pf_ft_ai/state/`.
- **Stores** (5. PF-FT-AI-STATE-MODEL.md §53–§54; ADR-D4-10): conversation/session/memory/cache on the
  Redis-namespaced store; workflow instance state persisted for suspend/resume
  (ADR-D2-10); enterprise state never persisted as truth (only ERC references +
  cache with TTL, ADR-D4-12).
- **Consistency rules** (5. PF-FT-AI-STATE-MODEL.md §50): the seven state-consistency rules are encoded as
  invariants/tests.
- **Enforcement**: import-linter + a fitness test asserting no enterprise-authoritative
  field is written into conversation/session/workflow stores.

## 9. Consequences

### 9.1 Positive
- Precedence and Golden Rule become structurally enforceable.
- Independent TTL/classification/retention per state class.
### 9.2 Negative
- More models and store config than a single blob.
### 9.3 Neutral
- Frames ADR-D4-02..12 (ERC, memory, cache, store).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Single-blob simplicity | Enforceable separation & correctness | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Enterprise state owned by PFF; AI holds only references |
| Precedence chain | Separation prevents low-authority state posing as enterprise truth |
| Four-state separation | This ADR *is* that principle, made enforceable |
| Versioned artefacts | State schemas versioned (5. PF-FT-AI-STATE-MODEL.md §51–§52) |
| Adam persona governs *how*, not *what* | Persona holds no state |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Enterprise fact cached as truth in memory | Med | High | H | CI fitness test; use ERC-ref memory (9 PF-FT-AI-MEMORY-CACHE.md §16) | AI Arch Lead | Low |
| RSK-02 | State schemas drift/incompatible | Low | Med | M | State versioning + migration (5. PF-FT-AI-STATE-MODEL.md §51–§52) | Backend Lead | Low |
| RSK-03 | Cross-tenant/user state leakage | Low | High | M | Namespace isolation + tests (9 PF-FT-AI-MEMORY-CACHE.md §77–§79) | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Enterprise-truth-in-AI-state violations | 0 | > 0 | CI fitness test | Per build |
| QM-02 | Cross-state contamination test pass | 100% | < 100% | CI | Per build |
| QM-03 | State schema version present | 100% | < 100% | Runtime check | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Isolation reduces cross-contamination/leak surface |
| Data classification touched | Each state class classified independently (5. PF-FT-AI-STATE-MODEL.md §56) |
| Personal data / PII | Retention/TTL set per state class |
| Children's data and safeguarding | Enterprise safeguarding data stays in PFF; not copied |
| UK GDPR lawful basis and rights impact | Per-state retention enables rights handling |
| Audit and evidential requirements | State-transition audit (5. PF-FT-AI-STATE-MODEL.md §60) |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 3 (state model), 7 (stores) |
| Repository paths | `src/pf_ft_ai/state/` |
| Configuration | Per-state TTL/classification |
| Contracts / schemas | Four state models + versions |
| Migration | State migration policy (5. PF-FT-AI-STATE-MODEL.md §52) |
| Dependencies on other ADRs | ADR-D2-07, ADR-D2-12, ADR-D4-10 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Four distinct state types exist; none merged | Type/architecture review |
| AC-02 | No enterprise-authoritative write to AI state | CI fitness test |
| AC-03 | Each state has own TTL/classification | Config review |
| AC-04 | Cross-tenant isolation holds | Security test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | State store metrics per class; violation counts |
| Alerting | Any separation violation |
| Runbook | `docs/runbooks/state.md` |
| Failure mode and degradation | Store failure isolated per class |
| Rollback | Schema version revert |
| Support model impact | Backend + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| State models + enforcement tests | M | negligible | Build |
| Store namespaces | — | shared | ADR-D4-10 |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Audit needs full state history | Governance | Consider event-sourcing (Option E) for AI state |
| RT-02 | Separation violations recur | QM-01 | Strengthen enforcement / training |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-19 Information/State |
| Specification sections | 5. PF-FT-AI-STATE-MODEL.md §2–§5, §49–§56, §60; 6 PF-FT-AI-CONVERSATION-SESSION.md §6, §54; 9 PF-FT-AI-MEMORY-CACHE.md §3–§4 |
| Requirement IDs | STATE-* |
| Build phases | 3, 7 |
| Code paths | `src/pf_ft_ai/state/` |
| Configuration | per-state TTL/classification |
| Tests | separation fitness suite |
| Upstream ADRs | ADR-D1-03, ADR-D2-07 |
| Downstream ADRs | ADR-D4-02, ADR-D4-10, ADR-D4-11, ADR-D4-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Principal Architect | Initial decision recorded. |
