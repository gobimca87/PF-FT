---
id: ADR-D6-09
title: Guardrail pipeline placement at six boundaries, fail-closed policy
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
related_adrs: [ADR-D6-08, ADR-D3-12, ADR-D3-04, ADR-D6-12, ADR-D2-09, ADR-D3-19]
source_docs:
  - "MD files/4 AI/18.PFF-FA-AI-GUARDRAILS.md §3, §4, §5, §9, §10, §11, §12, §51, §54, §55"
build_phases: [9]
impacted_paths:
  - src/pff_fa_ai/guardrails/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-09 — Guardrail pipeline placement at six boundaries, fail-closed policy

## 1. Summary

PFF AI will run a **guardrail pipeline at six enforcement boundaries** — user input,
pre-SLM prompt, SLM output, pre-tool-call, tool/API/RAG result ingestion, and
user-facing output — each returning a structured guardrail result and **failing closed**
on violation (18.PFF-FA-AI-GUARDRAILS.md §3–§5, §9–§12, §51, §54–§55). Guardrails are a mandatory,
versioned pipeline, not scattered checks; defense-in-depth means a bypass at one
boundary is caught at another.

## 2. Context and Problem Statement

18.PFF-FA-AI-GUARDRAILS.md §3–§5 define the guardrail architecture, layers and defense-in-depth; §9–§12 the
decision model, result, fail-closed handling and pipeline; §51/§54–§55 output validation,
invalid-output and repair. Where guardrails run determines what they can catch. Ad-hoc
placement leaves gaps. This ADR fixes the six boundaries and the fail-closed policy that
the injection (ADR-D6-08), tool (ADR-D6-10) and RAG (ADR-D6-12) rules plug into.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Guardrails at every trust boundary | 18.PFF-FA-AI-GUARDRAILS.md §4–§5 |
| DR-F-02 | Structured result + fail-closed | 18.PFF-FA-AI-GUARDRAILS.md §10–§11 |
| DR-F-03 | Defense-in-depth (multiple boundaries) | 18.PFF-FA-AI-GUARDRAILS.md §5 |
| DR-C-01 | Mandatory, versioned pipeline | 18.PFF-FA-AI-GUARDRAILS.md §3; CLAUDE.md |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Six boundaries cover the threat surface | Add boundaries | Threat model review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Coverage of trust boundaries | 28 | No gaps | Boundary coverage |
| EC-02 | Fail-closed safety | 22 | Safe on violation | Behaviour |
| EC-03 | Defense-in-depth | 18 | Bypass resilience | Multi-boundary catch |
| EC-04 | Performance overhead | 16 | Per-boundary cost | Latency |
| EC-05 | Maintainability/consistency | 16 | One pipeline | Consistency |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Six-boundary mandatory pipeline, fail-closed, structured results

**Description.** A shared guardrail pipeline invoked at all six boundaries; each returns
allow/block/transform with reasons; violations fail closed; pipeline is versioned and
mandatory (not optional per call).
**Strengths.** Full coverage; defense-in-depth; consistent; safe.
**Weaknesses.** Per-boundary latency; pipeline to maintain.
**Cost / effort.** Medium.

### 5.2 Option B — Input + output guardrails only (two boundaries)

**Description.** Guard only user input and final output.
**Strengths.** Simpler; lower latency.
**Weaknesses.** Misses pre-tool, tool-result, RAG-ingestion, pre-SLM — key injection/
exfiltration points.
**Cost / effort.** Low; gaps.

### 5.3 Option C — Single central guardrail (one chokepoint)

**Description.** One guardrail at the API edge.
**Strengths.** Simple.
**Weaknesses.** Can't see internal hops (tool/RAG/SLM); no defense-in-depth.
**Cost / effort.** Low; insufficient.

### 5.4 Option D — Per-component ad-hoc checks (no shared pipeline)

**Description.** Each component does its own checks.
**Strengths.** Localised.
**Weaknesses.** Inconsistent; gaps; hard to version/audit; not defense-in-depth.
**Cost / effort.** Low; fragmented.

### 5.5 Option E — Six-boundary pipeline + async monitoring guardrails (some non-blocking)

**Description.** Option A but some lower-risk guardrails run async/monitoring-only to cut
latency, while high-risk ones stay blocking.
**Strengths.** Latency relief; still catches high-risk synchronously.
**Weaknesses.** Async guardrails don't prevent, only detect; must classify carefully.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Optional/per-call guardrails | 18.PFF-FA-AI-GUARDRAILS.md §3 — mandatory |
| Fail-open on error | 18.PFF-FA-AI-GUARDRAILS.md §11 — fail closed |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 18.PFF-FA-AI-GUARDRAILS.md §3–§12/§51/§54–§55.

| Criterion | Weight | A: Six-boundary | B: In/out only | C: Single central | D: Ad-hoc | E: Six + async |
|---|---|---|---|---|---|---|
| EC-01 Coverage | 28 | 5 | 2 | 2 | 3 | 5 |
| EC-02 Fail-closed | 22 | 5 | 4 | 4 | 3 | 4 |
| EC-03 Defense-in-depth | 18 | 5 | 2 | 1 | 3 | 5 |
| EC-04 Performance | 16 | 3 | 5 | 5 | 4 | 4 |
| EC-05 Maintainability | 16 | 5 | 4 | 4 | 2 | 4 |
| **Weighted total** | **100** | **460** | **328** | **312** | **300** | **452** |

Totals (×20): **A = 460**, **E = 452**, **B = 328**, **C = 312**, **D = 300**.

**Sensitivity.** A leads E by 8; async/monitoring guardrails (E) are adopted *only* for
demonstrably low-risk checks to relieve latency, keeping all high-risk guardrails
blocking. Reduced-boundary options (B/C/D) leave exploitable gaps.

## 7. Decision

**PFF AI will run a mandatory, versioned guardrail pipeline at six boundaries — user
input, pre-SLM prompt, SLM output, pre-tool-call, tool/API/RAG result ingestion, and
user-facing output — with structured results and fail-closed handling (Option A);
selected low-risk guardrails may run async/monitoring-only to relieve latency
(Option E), while all high-risk guardrails remain blocking.** Injection (ADR-D6-08),
tool (ADR-D6-10), RAG-ACL (ADR-D6-12) and PII (ADR-D6-06) rules plug into this pipeline.
Reduced placements (B/C/D) are rejected.

## 8. Architecture Detail

- `src/pff_fa_ai/guardrails/`: a `GuardrailPipeline` invoked at each boundary with a
  boundary-specific rule set; returns `GuardrailResult` (allow/block/transform + reason,
  18.PFF-FA-AI-GUARDRAILS.md §10); fail-closed on block or error (§11).
- Boundaries wire into: API input, prompt composer (ADR-D3-12), SLM output (ADR-D3-19
  before streaming), harness pre-tool + tool-result (ADR-D3-04/D2-09), RAG ingestion
  (ADR-D6-12), final output (PII redaction ADR-D6-06, portal-link strip ADR-D2-19).
- Versioned as an artefact (ADR-D5-06); output validation/repair (§51, §54–§55) at the
  output boundary.

## 9. Consequences

### 9.1 Positive
- Complete boundary coverage; defense-in-depth; consistent, versioned, fail-closed.
### 9.2 Negative
- Per-boundary latency; pipeline maintenance.
### 9.3 Neutral
- Central plug-point for all guardrail rule ADRs.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Some latency | Coverage + defense-in-depth | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Guardrails prevent AI overstepping its role |
| Precedence chain | Enforces authoritative-data priority at boundaries |
| Four-state separation | Guards data crossing between state/trust zones |
| Versioned artefacts | Pipeline versioned |
| Adam persona governs *how*, not *what* | Output guardrail ensures persona doesn't alter truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | A boundary left unguarded | Low | High | M | Coverage audit + tests | Security Architect | Low |
| RSK-02 | Guardrail fails open on error | Low | High | M | Fail-closed default (§11) | AI Arch Lead | Low |
| RSK-03 | Latency from six checks | Med | Med | M | Async for low-risk (E); optimise | Backend Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Boundaries with active guardrails | 6/6 | < 6 | Coverage audit | Per release |
| QM-02 | Fail-open incidents | 0 | > 0 | Tests/logs | Continuous |
| QM-03 | Guardrail latency overhead | within budget | breach | Traces | Continuous |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Comprehensive boundary enforcement |
| Data classification touched | Confidential |
| Personal data / PII | Output guardrail redacts (ADR-D6-06) |
| Children's data and safeguarding | Safeguarding content vetted at boundaries |
| UK GDPR lawful basis and rights impact | Supports integrity/confidentiality |
| Audit and evidential requirements | Guardrail results logged |
| Standards touched | ISO/IEC 27001, 42001, NIST AI RMF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9 |
| Repository paths | `src/pff_fa_ai/guardrails/` |
| Configuration | Per-boundary rule sets; blocking/async flags |
| Contracts / schemas | GuardrailResult (§10) |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D6-08, D3-04, D3-12, D6-12, D6-06 |
| Effort estimate | L |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | All six boundaries invoke the pipeline | Coverage audit |
| AC-02 | Violations fail closed | Test (§11) |
| AC-03 | Structured results emitted | Unit test |
| AC-04 | High-risk guardrails are blocking | Config audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Guardrail hits/blocks per boundary |
| Alerting | Fail-open; spike in blocks |
| Runbook | `docs/runbooks/guardrails.md` |
| Failure mode and degradation | Error → fail closed |
| Rollback | Pipeline version revert |
| Support model impact | Security + AI platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Guardrail pipeline | L | per-call | Build + inference |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | New trust boundary emerges | Threat model | Add boundary to pipeline |
| RT-02 | Latency from guardrails too high | QM-03 | Move more low-risk checks async (E) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | 18.PFF-FA-AI-GUARDRAILS.md §3–§12, §51, §54–§55 |
| Requirement IDs | SEC-GR-* |
| Build phases | 9 |
| Code paths | `src/pff_fa_ai/guardrails/` |
| Configuration | per-boundary rules |
| Tests | guardrail coverage suites |
| Upstream ADRs | ADR-D6-08 |
| Downstream ADRs | ADR-D6-10, D6-12 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
