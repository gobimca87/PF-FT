---
id: ADR-D7-14
title: Test strategy and test pyramid, incl. deterministic mock SLM
domain: 7 Operations
ws_ref: [WS-32]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: QA Lead
contributors: [Backend Lead, ML Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D7-09, ADR-D7-13, ADR-D3-14, ADR-D2-07, ADR-D6-12]
source_docs:
  - "MD files/5 QualityGovernance/22.PF-FT-AI-TESTING.md §5, §6, §7, §8, §10, §12, §20, §21, §30, §37, §38, §41, §50, §56"
build_phases: [1]
impacted_paths:
  - tests/
classification: Internal
review_due: 2027-08-22
---

# ADR-D7-14 — Test strategy and test pyramid, incl. deterministic mock SLM

## 1. Summary

PFF AI will follow a **test pyramid** — many fast unit tests, fewer component/integration
tests, few end-to-end — with a **deterministic mock SLM** and **mock enterprise APIs** so
AI-dependent tests are stable and fast (22.PF-FT-AI-TESTING.md §5–§8, §12, §20–§21, §37–§38). Non-
deterministic model behaviour is tested at the eval layer (ADR-D7-13), not in unit tests;
security/ACL/idempotency tests are first-class.

## 2. Context and Problem Statement

22.PF-FT-AI-TESTING.md §5–§6 test pyramid/layers, §7–§8 categories/structure, §10–§12 unit principles/
AI-component testing, §20–§21 mocking enterprise APIs, §30 state tests, §37–§38 SLM/SLM-
failure testing, §41 RAG ACL testing, §50 idempotency, §56 memory isolation. LLM
non-determinism makes naive AI tests flaky. This ADR fixes the test strategy and the
mock-SLM approach that keeps CI deterministic.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Test pyramid (unit-heavy) | 22.PF-FT-AI-TESTING.md §5 |
| DR-F-02 | Deterministic mock SLM + mock enterprise APIs | 22.PF-FT-AI-TESTING.md §12, §20–§21, §37 |
| DR-F-03 | Non-determinism tested at eval layer | ADR-D7-13 |
| DR-F-04 | Security/ACL/idempotency/isolation tests | 22.PF-FT-AI-TESTING.md §41, §50, §56 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Provider abstraction supports a mock | Add a mock provider (ADR-D3-14) | Contract |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Determinism/stability | 28 | No flake | Flake rate |
| EC-02 | Coverage (incl. security/ACL/idempotency) | 24 | Catch defects | Coverage |
| EC-03 | Speed (pyramid shape) | 20 | Fast CI | Test duration |
| EC-04 | Realism (integration/e2e where needed) | 16 | Catch integration bugs | Integration coverage |
| EC-05 | Maintainability | 12 | Sustainable | Test upkeep |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Test pyramid + deterministic mock SLM + mock enterprise APIs; non-determinism at eval layer

**Description.** Unit-heavy pyramid; a deterministic mock `SLMProvider` (ADR-D3-14) and
contract-based enterprise-API mocks (22.PF-FT-AI-TESTING.md §20–§21); component/integration for wiring;
few e2e; security/ACL/idempotency/isolation suites; model quality at eval (ADR-D7-13).
**Strengths.** Stable, fast, well-covered, realistic where needed.
**Weaknesses.** Mock upkeep + contract drift risk (mitigated by contract tests).
**Cost / effort.** Medium.

### 5.2 Option B — Heavy end-to-end testing (few units)

**Description.** Inverted pyramid, mostly e2e.
**Strengths.** High realism.
**Weaknesses.** Slow, flaky, hard to localise failures.
**Cost / effort.** High; brittle.

### 5.3 Option C — Live-SLM tests (call real model in CI)

**Description.** Use the real model in tests.
**Strengths.** Real behaviour.
**Weaknesses.** Non-deterministic/flaky; slow; costly; not for unit CI (that's eval).
**Cost / effort.** High; flaky.

### 5.4 Option D — Unit-only (no integration/e2e)

**Description.** Only unit tests.
**Strengths.** Fast.
**Weaknesses.** Misses wiring/integration bugs (ERC/tool/graph).
**Cost / effort.** Low; gaps.

### 5.5 Option E — Pyramid + mock SLM + contract tests (consumer-driven) for enterprise APIs + recorded fixtures

**Description.** Option A with consumer-driven contract tests against enterprise APIs and
recorded response fixtures to prevent mock drift.
**Strengths.** A + guards against mock/real divergence.
**Weaknesses.** Contract-test maintenance.
**Cost / effort.** Medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Non-deterministic model asserts in unit tests | 22.PF-FT-AI-TESTING.md §12; flake |
| No security/ACL tests | 22.PF-FT-AI-TESTING.md §41 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 22.PF-FT-AI-TESTING.md §5–§56.

| Criterion | Weight | A: Pyramid+mock | B: Heavy e2e | C: Live-SLM | D: Unit-only | E: A+contract+fixtures |
|---|---|---|---|---|---|---|
| EC-01 Determinism | 28 | 5 | 2 | 1 | 5 | 5 |
| EC-02 Coverage | 24 | 5 | 4 | 4 | 2 | 5 |
| EC-03 Speed | 20 | 5 | 1 | 2 | 5 | 5 |
| EC-04 Realism | 16 | 4 | 5 | 5 | 1 | 5 |
| EC-05 Maintainability | 12 | 4 | 2 | 2 | 4 | 3 |
| **Weighted total** | **100** | **472** | **288** | **272** | **332** | **488** |

Totals (×20): **E = 488**, **A = 472**, **D = 332**, **B = 288**, **C = 272**.

**Sensitivity.** E (A + consumer-driven contract tests + recorded fixtures) edges A by
guarding against mock/real drift — important given many enterprise integrations. Adopted.
Heavy-e2e (B) and live-SLM (C) are flaky/slow; unit-only (D) misses integration bugs.

## 7. Decision

**PFF AI will follow a unit-heavy test pyramid with a deterministic mock SLM and
consumer-driven contract tests + recorded fixtures for enterprise APIs, component/
integration tests for wiring, few e2e, and first-class security/ACL/idempotency/isolation
suites; model non-determinism is tested at the eval layer (ADR-D7-13) (Option E).**
Heavy-e2e (B), live-SLM-in-CI (C) and unit-only (D) are rejected.

## 8. Architecture Detail

- `tests/` structured per 22.PF-FT-AI-TESTING.md §8; a deterministic `MockSLMProvider` (ADR-D3-14) returns
  fixed outputs; enterprise-API mocks are contract-driven (22.PF-FT-AI-TESTING.md §19–§21) with recorded
  fixtures; TypedDict/graph state tested (22.PF-FT-AI-TESTING.md §30; ADR-D2-07).
- Security suites: prompt-injection/tool-abuse (22.PF-FT-AI-TESTING.md §34/§45), RAG ACL (§41; ADR-D6-12),
  memory isolation (§56), idempotency (§50). Model quality → ADR-D7-13. All gate CI
  (ADR-D7-09).

## 9. Consequences

### 9.1 Positive
- Stable, fast, well-covered tests; integration realism; drift-guarded mocks.
### 9.2 Negative
- Mock + contract-test maintenance.
### 9.3 Neutral
- Complements eval (D7-13) at the quality layer.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Live-model realism in unit CI | Determinism + speed (quality via eval) | QA Lead |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Tests assert AI-layer behaviour |
| Precedence chain | ACL/precedence behaviours tested |
| Four-state separation | State + isolation tests |
| Versioned artefacts | Test fixtures versioned |
| Adam persona governs *how*, not *what* | Persona quality tested at eval (D7-13) |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Mock diverges from real API | Med | Med | M | Consumer-driven contract tests + fixtures (E) | Backend Lead | Low |
| RSK-02 | Flaky AI tests | Med | Med | M | Deterministic mock SLM | QA Lead | Low |
| RSK-03 | Integration bugs missed | Low | Med | M | Component/integration + few e2e | QA Lead | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Unit test coverage | ≥ target | below | Coverage | Per release |
| QM-02 | Flake rate | ≈ 0 | rising | CI | Weekly |
| QM-03 | Security/ACL/idempotency suites present | yes | missing | Repo audit | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Security/ACL tests strengthen posture |
| Data classification touched | Synthetic test data only |
| Personal data / PII | No real PII in tests |
| Children's data and safeguarding | No real children's data in tests |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Test results retained |
| Standards touched | ISO 9001, ISO/IEC 27001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `tests/` |
| Configuration | Mock SLM; contract fixtures |
| Contracts / schemas | Contract test definitions |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D3-14, D2-07, D6-12, D7-13 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Deterministic mock SLM in AI tests | Test infra |
| AC-02 | Enterprise mocks contract-verified | Contract tests |
| AC-03 | Security/ACL/idempotency suites present | Repo audit |
| AC-04 | Pyramid shape (unit-heavy) | Test metrics |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Coverage, flake, duration |
| Alerting | Flake/coverage regressions |
| Runbook | `docs/runbooks/testing.md` |
| Failure mode and degradation | Test fail → block merge (ADR-D7-09) |
| Rollback | N/A |
| Support model impact | QA + backend |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Test suites + mocks | M | CI minutes | Build |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Mock/real drift causes prod bug | Incident | Strengthen contract tests |
| RT-02 | Flake rises | QM-02 | Stabilise/quarantine (no skip in prod code) |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-32 |
| Specification sections | 22.PF-FT-AI-TESTING.md §5–§8, §10–§12, §20–§21, §30, §37–§38, §41, §50, §56 |
| Requirement IDs | TEST-* |
| Build phases | 1 |
| Code paths | `tests/` |
| Configuration | mock/contract fixtures |
| Tests | the suites themselves |
| Upstream ADRs | ADR-D3-14, D2-07 |
| Downstream ADRs | ADR-D7-09, D7-13 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | QA Lead | Initial decision recorded. |
