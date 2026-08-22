---
id: ADR-D3-20
title: RAG scope — knowledge and FAQ only, never business truth
domain: 3 AI
ws_ref: [WS-17]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: AI Architecture Lead
contributors: [Principal Architect, Security Architect, Domain SME]
reviewers: [Principal Architect, Data Protection Officer]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D1-03, ADR-D3-21, ADR-D3-22, ADR-D3-24, ADR-D2-12, ADR-D6-12]
source_docs:
  - "MD files/4 AI/13.FP-FT-AI-RAG.md §2, §4, §5, §100, §101, §102, §103, §116, §117, §118, §119"
build_phases: [8]
impacted_paths:
  - src/pf_ft_ai/rag/
classification: Internal
review_due: 2027-08-22
---

# ADR-D3-20 — RAG scope — knowledge and FAQ only, never business truth

## 1. Summary

PFF AI's RAG subsystem will serve **only knowledge and FAQ content** — policies,
guidance, how-to, rules explanations — and will **never** be a source of
authoritative business state (a club's affiliation status, a payment result, an
official's record). Those come exclusively from enterprise APIs/events via ERC, per
the precedence chain. RAG sits at the bottom-but-one tier of authority and its output
is always grounded, cited, and subordinate to enterprise truth (doc 13 §2, §4, §5).

## 2. Context and Problem Statement

Doc 13 §4 states "RAG is not the enterprise API layer" and §5 defines the RAG
decision boundary; §100–§103 fix how RAG relates to Service Bus, memory, ERC and
enterprise APIs; §116–§119 govern hallucination control and answerability. The
Golden Rule and precedence chain (ADR-D1-03) place RAG below ERC/enterprise. The
central risk is scope creep: an engineer, seeing RAG can "answer questions", points
it at business records, and the platform starts stating stale or unauthorised
"facts" that only the enterprise system may assert. This ADR draws the boundary
explicitly and makes it enforceable.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | RAG answers knowledge/FAQ questions with citations | doc 13 §2, §81 |
| DR-C-01 | RAG must never assert business truth | doc 13 §4, §5; ADR-D1-03 |
| DR-C-02 | Precedence: Enterprise API/Event > ERC > Cache > RAG > SLM | CLAUDE.md; doc 13 §102–§103 |
| DR-C-03 | Grounded-response + answerability rules apply | doc 13 §116–§119 |
| DR-N-01 | ACL-aware retrieval (some knowledge is restricted) | doc 13 §33–§39; ADR-D6-12 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Business questions can be routed to enterprise APIs, not RAG | Redesign routing | Intent routing tests (ADR-D3-05) |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Authority correctness (no business truth from RAG) | 34 | The whole point; safety | Boundary tests |
| EC-02 | Usefulness for knowledge questions | 22 | Must add value | Answered-with-citation rate |
| EC-03 | Enforceability | 18 | Boundary must hold in code | Guard exists |
| EC-04 | Hallucination control | 14 | Grounded/answerable | Ungrounded-answer rate |
| EC-05 | Simplicity of mental model | 12 | Team clarity | Ambiguity of scope |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Knowledge/FAQ only; business questions routed to enterprise APIs

**Description.** RAG indexes only knowledge sources; any question needing business
state is routed to enterprise APIs via ERC; RAG answers are grounded and cited.
**Strengths.** Honours precedence; safe; clear mental model; enforceable.
**Weaknesses.** Requires disciplined routing to separate knowledge vs business
questions.
**Cost / effort.** Low-medium.

### 5.2 Option B — RAG over knowledge + a read-only snapshot of business data

**Description.** Also index periodic snapshots of business records for "faster" answers.
**Strengths.** Fewer live API calls.
**Weaknesses.** Stale business "truth"; violates precedence (RAG asserting business
state); ACL/freshness nightmare; the exact failure this ADR exists to prevent.
**Cost / effort.** High risk.

### 5.3 Option C — RAG as a general Q&A layer over everything

**Description.** One retrieval layer over knowledge and enterprise data.
**Strengths.** Simple single interface.
**Weaknesses.** Conflates authority tiers; unsafe; unauditable business claims.
**Cost / effort.** Low build, unacceptable risk.

### 5.4 Option D — No RAG; enterprise APIs + static FAQ pages only

**Description.** Drop retrieval; link users to static FAQs.
**Strengths.** Zero hallucination risk; simplest.
**Weaknesses.** Loses conversational knowledge answering; poor UX for policy
questions; underuses the platform's value.
**Cost / effort.** Low; low value.

### 5.5 Option E — Knowledge/FAQ RAG + explicit "consult enterprise" hand-off for business questions

**Description.** Option A plus a first-class behaviour where, on a business-state
question, RAG declines and the agent fetches from enterprise APIs (or tells the user
what it will do), never guessing.
**Strengths.** A's safety + best UX; the decline/hand-off is explicit and testable.
**Weaknesses.** Slightly more routing/behaviour to build.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| RAG writes back to enterprise | DR-C-01 — RAG is read-only knowledge |
| RAG overrides ERC when "more detailed" | DR-C-02 — precedence is absolute |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 13 §2–§5, §100–§103,
§116–§119 and the precedence chain (ADR-D1-03).

| Criterion | Weight | A: Knowledge-only | B: +snapshot | C: General Q&A | D: No RAG | E: Knowledge + handoff |
|---|---|---|---|---|---|---|
| EC-01 Authority correctness | 34 | 5 | 2 | 1 | 5 | 5 |
| EC-02 Usefulness | 22 | 4 | 4 | 5 | 2 | 5 |
| EC-03 Enforceability | 18 | 4 | 2 | 1 | 5 | 5 |
| EC-04 Hallucination control | 14 | 4 | 3 | 2 | 5 | 5 |
| EC-05 Simplicity | 12 | 4 | 2 | 3 | 5 | 4 |
| **Weighted total** | **100** | **432** | **266** | **220** | **428** | **488** |

Totals (×20): **E = 488**, **A = 432**, **D = 428**, **B = 266**, **C = 220**.

**Sensitivity.** E beats A by making the business-question hand-off an explicit,
testable behaviour rather than relying on routing alone. D is safe but low-value; the
gap to E is entirely EC-02. B and C fail the authority criterion decisively.

## 7. Decision

**PFF AI's RAG will serve knowledge and FAQ content only, and on any business-state
question will decline to answer from RAG and hand off to enterprise APIs via ERC
(Option E).** RAG output is always grounded and cited (ADR-D3-22), ACL-filtered
(ADR-D6-12), and ranks below ERC/enterprise in the precedence chain — it can never
assert or override business truth. Indexing business-record snapshots (B) or a
general Q&A layer (C) is forbidden. Dropping RAG entirely (D) is rejected as
low-value.

**Status rationale.** `Accepted` — doc 13 §4–§5 and the Golden Rule fix this
boundary; the ADR records the enforceable design.

## 8. Architecture Detail

- **Source registry** (doc 13 §8–§10): only knowledge/FAQ/policy sources may be
  registered; source authority classification tags every source; business systems
  are not registrable RAG sources.
- **Decision boundary** (doc 13 §5): a check before retrieval classifies the question;
  business-state intents bypass RAG and go to enterprise APIs (ADR-D2-12/D3-05).
- **Grounding + answerability** (doc 13 §116–§119): answers must be supported by
  retrieved, cited content; unanswerable/low-confidence → say so, don't fabricate.
- **Precedence enforcement** (doc 13 §102–§103): where RAG and ERC/enterprise both
  have content, enterprise wins; RAG never contradicts authoritative state.
- **ACL** (doc 13 §33–§39; ADR-D6-12): retrieval-time filtering on the caller's
  authorisation.

## 9. Consequences

### 9.1 Positive
- The platform can never state stale/unauthorised business "facts" from RAG.
- Clear, testable boundary and hand-off behaviour.
### 9.2 Negative
- Requires disciplined question classification and a hand-off path.
### 9.3 Neutral
- Defines the subject for ADR-D3-21/22/23/24.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| "Fast" cached business answers from RAG | Authority correctness & auditability | Principal Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | RAG informs; it never decides or asserts business state |
| Precedence chain | RAG explicitly ranked below ERC/enterprise; never overrides (doc 13 §102–§103) |
| Four-state separation | Knowledge plane distinct from enterprise business state |
| Versioned artefacts | RAG pipeline/index versioned (doc 13 §138–§143) |
| Adam persona governs *how*, not *what* | Persona narrates cited knowledge; never invents business truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Business source registered into RAG | Low | High | M | Source-registry policy + review | Security Architect | Low |
| RSK-02 | RAG answers a business question | Med | High | H | Decision boundary + hand-off + tests | AI Arch Lead | Low |
| RSK-03 | RAG contradicts ERC | Low | High | M | Precedence enforcement + eval | Principal Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Business questions answered by RAG | 0 | > 0 | Boundary tests / traces | Continuous |
| QM-02 | Knowledge answers with valid citation | 100% | < 98% | Eval (doc 13 §135) | Per release |
| QM-03 | Ungrounded answer rate | ≈ 0 | rising | Eval (§117) | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Restricts RAG to knowledge; no business-data exposure via retrieval |
| Data classification touched | Internal knowledge; ACL-restricted subsets |
| Personal data / PII | Business/personal records are not in RAG |
| Children's data and safeguarding | Safeguarding knowledge yes; safeguarding records never |
| UK GDPR lawful basis and rights impact | Minimises personal data in the index |
| Audit and evidential requirements | Citations + provenance (doc 13 §176–§178) |
| Standards touched | ISO/IEC 42001, 27001, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 8 |
| Repository paths | `src/pf_ft_ai/rag/` |
| Configuration | Source registry policy; decision-boundary config |
| Contracts / schemas | RAG tool contract (doc 13 §106) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D1-03, ADR-D2-12, ADR-D3-05, ADR-D6-12 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only knowledge sources registrable | Source-registry test |
| AC-02 | Business-state question → hand-off, not RAG answer | Boundary test |
| AC-03 | RAG answer never contradicts ERC | Precedence eval |
| AC-04 | Every knowledge answer cited or declined | Citation eval (ADR-D3-22) |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Boundary decisions; citation rate; grounding metrics |
| Alerting | Any business-question-answered-by-RAG detection |
| Runbook | `docs/runbooks/rag.md` |
| Failure mode and degradation | Retrieval failure → say so / hand off (doc 13 §182–§183) |
| Rollback | Disable RAG source; fall back to enterprise-only answers |
| Support model impact | AI platform + content owners |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Boundary + hand-off logic | M | negligible | Build |
| (Index/embedding costs) | see ADR-D3-21/23/24 | | |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Pressure to index business data for speed | Design review | Reaffirm boundary; solve with caching of enterprise reads (ADR-D4-12), not RAG |
| RT-02 | RAG-answered business question incident | Incident | CAR; tighten boundary |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-17 |
| Specification sections | doc 13 §2, §4, §5, §100–§103, §116–§119 |
| Requirement IDs | RAG-SCOPE-* |
| Build phases | 8 |
| Code paths | `src/pf_ft_ai/rag/` |
| Configuration | source registry policy |
| Tests | boundary + citation + precedence suites |
| Upstream ADRs | ADR-D1-03, ADR-D2-12 |
| Downstream ADRs | ADR-D3-21, ADR-D3-22, ADR-D3-24, ADR-D6-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | AI Architecture Lead | Initial decision recorded. |
