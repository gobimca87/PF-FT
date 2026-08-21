---
id: ADR-Dx-NN
title: <Decision title — a noun phrase naming the decision, not the topic>
domain: <0 Decision Programme | 1 Business | 2 Application | 3 AI | 4 Information | 5 Technology | 6 Security & Governance | 7 Operations | 8 Business Value>
ws_ref: [WS-NN]
status: <Proposed | Accepted | Superseded | Deprecated | Rejected>
version: 1.0.0
date: YYYY-MM-DD
decision_owner: <role accountable for the decision>
contributors: [<roles consulted>]
reviewers: [<roles who reviewed>]
approver: <role that ratifies — see ADR-D0-03>
supersedes: []
superseded_by: []
related_adrs: [ADR-Dx-NN]
source_docs:
  - "MD files/<folder>/<doc>.md §<n>, §<n>"
build_phases: [<phase numbers from DEVELOPMENT-GUIDE.md §4>]
impacted_paths:
  - src/pf_ft_ai/<module>/
classification: <Internal | Confidential>
review_due: YYYY-MM-DD
---

# ADR-Dx-NN — <Decision title>

> **Template note.** This is the canonical ADR template for the PFF AI architecture
> decision library. Its structure is fixed by [ADR-D0-01](00-decision-programme/ADR-D0-01-adopt-adr-driven-architecture-governance.md);
> sections may not be dropped. Where a section genuinely does not apply, write
> "Not applicable — <one-line reason>" rather than deleting the heading, so that a
> reviewer can tell the difference between "considered and irrelevant" and "forgotten".
> Delete this blockquote when instantiating.

## 1. Summary

<Two to three sentences. What was decided, and the single most important reason.
A reader who stops here should be able to repeat the decision correctly.>

## 2. Context and Problem Statement

<The situation forcing a decision. Include:
 - what the specification documents say and where they stop short;
 - which components, workflows or teams are blocked until this is resolved;
 - what concretely goes wrong if the decision is left implicit — an ADR whose
   "do nothing" cost is zero probably should not exist.>

## 3. Decision Drivers

### 3.1 Functional drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | <requirement this decision must satisfy> | <doc §> |

### 3.2 Non-functional drivers

| ID | Driver | Target | Source |
|---|---|---|---|
| DR-N-01 | <latency / availability / accuracy / cost attribute> | <measurable target> | <doc §> |

### 3.3 Constraints

| ID | Constraint | Type | Source |
|---|---|---|---|
| DR-C-01 | <fixed boundary that removes options from the table> | <Platform / Regulatory / Organisational / Contractual> | <doc §> |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | <what is taken as true without proof> | <what breaks> | <how and when it gets checked> |

## 4. Evaluation Criteria and Weights

<CMMI DAR SP 1.1 — criteria established *before* alternatives are scored. Weights sum
to 100. Justify any criterion weighted above 20: a dominant weight predetermines the
outcome and must be defensible.>

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | <criterion> | <n> | <why it matters here> | <how an option is scored against it> |
| | **Total** | **100** | | |

Scoring scale: **1** unacceptable · **2** poor · **3** adequate · **4** good · **5** excellent.

## 5. Alternatives Considered

<CMMI DAR SP 1.2 — at least two genuine alternatives. Where a driver or constraint
truly forces the outcome, record the postures that were rejected and why, rather than
inventing candidates that were never viable. Never present a straw man.>

### 5.1 Option A — <name>

**Description.** <what this option is, concretely>

**Strengths.**
- <point>

**Weaknesses.**
- <point>

**Cost / effort.** <order-of-magnitude implementation and run cost>

### 5.2 Option B — <name>

<same structure>

### 5.3 Option C — <name>

<same structure, as many as were genuinely on the table>

## 6. Evaluation Method and Decision Matrix

<CMMI DAR SP 1.3–1.4 — state the method (structured weighted scoring, prototype,
benchmark, expert review, or a combination) and what evidence backed the scores.>

**Method.** <e.g. weighted scoring against §4 criteria, informed by the constraints in
§3.3 and by <benchmark / prototype / vendor documentation / spec doc §>.>

| Criterion | Weight | A: <name> | B: <name> | C: <name> |
|---|---|---|---|---|
| EC-01 <short> | <n> | <s> | <s> | <s> |
| **Weighted total** | **100** | **<t>** | **<t>** | **<t>** |

**Sensitivity.** <Which weight would have to move, and by how much, to change the
winner. If the result is fragile, say so — a decision that flips on a ±5 weight swing
needs a stated tie-breaker.>

## 7. Decision

<CMMI DAR SP 1.5. State the selected option unambiguously, in the imperative:
"PFF AI will …". Then give the rationale that follows from §6 — including why the
runner-up lost on the criteria that mattered, not merely that it scored lower.>

**Status rationale.** <Why this ADR carries its `status`. A `Proposed` ADR must say
exactly what sign-off it is waiting for and from whom.>

## 8. Architecture Detail

<How the decision is actually realised. This is the section that makes the ADR usable
by an implementer: components and their responsibilities, interfaces and contracts,
configuration keys and their file locations, sequence of operations, failure paths.
Include a Mermaid diagram only where it shows a mechanism that prose cannot.>

## 9. Consequences

### 9.1 Positive

- <consequence>

### 9.2 Negative

- <consequence — be honest; an ADR with no negative consequences was not a decision>

### 9.3 Neutral

- <consequence>

### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| <what the platform loses> | <what it gains> | <role> |

## 10. Golden-Rule and Precedence Conformance

<Mandatory in every ADR. Show how the decision honours the project's binding
constraints, or state plainly that it does not touch them.>

| Constraint | Conformance |
|---|---|
| Enterprise systems decide and execute; the AI platform interprets, orchestrates, contextualises, explains, communicates | <how> |
| Authoritative-truth precedence: Enterprise API/Event > ERC > Cache > RAG > SLM output | <how, or "not applicable — <reason>"> |
| Four-state separation: Conversation / Session / Workflow-Agent / Enterprise Business State | <how, or "not applicable — <reason>"> |
| Versioned artefacts, never mutated in place in production | <how, or "not applicable — <reason>"> |
| Adam persona governs *how* things are communicated, never *what* is true | <how, or "not applicable — <reason>"> |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | <risk> | <Low/Med/High> | <Low/Med/High> | <L×I> | <mitigation> | <role> | <Low/Med/High> |

## 12. Quantitative Targets and Measures

<CMMI ML4 QPM — the decision is only manageable if its effect is measurable. Every row
must name a real signal source, not an aspiration.>

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | <SLI or KPI> | <target> | <breach point> | <Langfuse / App Insights / CI / manual> | <cadence> |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | <> |
| Data classification touched | <Public / Internal / Confidential / Personal / Special-category> |
| Personal data / PII | <> |
| Children's data and safeguarding | <relevant across FA football data — state explicitly> |
| UK GDPR lawful basis and rights impact | <> |
| Audit and evidential requirements | <> |
| Standards touched | <ISO/IEC 42001 · ISO/IEC 27001 · ISO 9001 · NIST AI RMF · EU AI Act> |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | <DEVELOPMENT-GUIDE.md §4 phase numbers> |
| Repository paths | <src/, config/, prompts/, contracts/ paths created or changed> |
| Configuration | <config keys, schema files, release-manifest entries> |
| Contracts / schemas | <Pydantic models, event schemas, tool schemas> |
| Migration | <what existing behaviour changes and how it is transitioned> |
| Dependencies on other ADRs | <ADR IDs that must land first> |
| Effort estimate | <T-shirt size with the reasoning behind it> |

## 15. Validation and Verification

<How anyone can confirm the decision is actually in force — not that it was written down.>

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | <observable statement that holds if the decision is implemented> | <test path / CI gate / evaluation suite / architecture-fitness check> |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | <dashboards, traces, metrics added> |
| Alerting | <alerts and their severities> |
| Runbook | <docs/runbooks/<file>.md, new or amended> |
| Failure mode and degradation | <what a partial failure looks like to a user> |
| Rollback | <how the decision is reversed operationally> |
| Support model impact | <on-call, escalation, service tier> |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| <element> | <> | <> | <how the figure was derived> |

## 18. Revisit Triggers and Causal Analysis Hooks

<CMMI ML5 CAR/OPM — the conditions under which this ADR is reopened, written specifically
enough that monitoring can detect them.>

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | <specific, observable condition> | <measure from §12 / event / date> | <reopen, amend, or supersede> |

**Scheduled review:** `review_due` in the front matter. **Causal analysis:** if an
incident is traced to this decision, record it here and raise a superseding ADR rather
than editing §7 in place.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-NN <sheet name> |
| Specification sections | `MD files/<doc>` §<n> |
| Requirement IDs | <FR/NFR IDs from ADR-D1-12 scheme> |
| Build phases | <> |
| Code paths | <> |
| Configuration | <> |
| Tests | <> |
| Upstream ADRs | <decisions this one depends on> |
| Downstream ADRs | <decisions that depend on this one> |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | YYYY-MM-DD | <role> | Initial decision recorded. |
