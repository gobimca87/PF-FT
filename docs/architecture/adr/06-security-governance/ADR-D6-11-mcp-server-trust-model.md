---
id: ADR-D6-11
title: MCP server trust model and response validation
domain: 6 Security & Governance
ws_ref: [WS-27]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [AI Architecture Lead, Integration Engineer]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D6-10, ADR-D2-13, ADR-D6-08, ADR-D6-09, ADR-D3-04]
source_docs:
  - "MD files/4 AI/18.PF-FT-AI-GUARDRAILS.md §30, §47, §48, §49, §50"
  - "MD files/5 QualityGovernance/19.PF-FT-AI-SECURITY.md §61, §62, §63, §64"
build_phases: [9]
impacted_paths:
  - src/pf_ft_ai/integration/mcp/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D6-11 — MCP server trust model and response validation

## 1. Summary

MCP (Model Context Protocol) servers will be treated as **semi-trusted external
integrations**: only **allowlisted MCP servers and tools** with **pinned version
compatibility** may be used, all MCP **responses are validated and treated as untrusted
content** (injection-checked, schema-validated) before use, and MCP calls go through the
same harness allowlist/authorization as any tool (doc 18 §30, §47–§50; doc 19 §61–§64).
An MCP server is never implicitly trusted.

## 2. Context and Problem Statement

Doc 18 §30 MCP injection defence, §47–§50 MCP restrictions/server-allowlist/tool-
allowlist/version-compatibility; doc 19 §61–§64 MCP security/server-trust/tool-security/
response-security. MCP extends the platform with external capability servers — powerful
but a supply-chain and injection risk if trusted blindly. This ADR fixes the MCP trust
model and response validation (a specialisation of ADR-D6-10 for MCP).

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Allowlist MCP servers + tools | doc 18 §48–§49; doc 19 §62 |
| DR-F-02 | Version compatibility pinned | doc 18 §50 |
| DR-F-03 | MCP responses validated + untrusted | doc 18 §30; doc 19 §64 |
| DR-C-01 | MCP calls via harness authz/allowlist | ADR-D6-10, D3-04 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | MCP is used for some integrations | If unused, ADR is dormant policy | Integration plan |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Trust control (allowlist/version) | 28 | Supply-chain | Allowlist coverage |
| EC-02 | Response safety (injection/schema) | 26 | Untrusted content | Validation |
| EC-03 | Authz consistency | 18 | Same as tools | Harness gating |
| EC-04 | Auditability | 14 | Accountability | Logs |
| EC-05 | Extensibility | 14 | Add servers safely | Onboarding |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Allowlisted, version-pinned MCP servers/tools + response validation + harness authz

**Description.** Only approved MCP servers/tools (doc 18 §48–§49); versions pinned
(§50); responses validated + injection-checked + treated as untrusted (§30; doc 19 §64);
calls go through harness allowlist/authorization (ADR-D6-10).
**Strengths.** Controls supply-chain + injection; consistent with tool security.
**Weaknesses.** Onboarding process per server.
**Cost / effort.** Medium.

### 5.2 Option B — Trust approved MCP servers' responses (allowlist, no response validation)

**Description.** Allowlist servers but trust their output.
**Strengths.** Simpler.
**Weaknesses.** A compromised/poisoned server injects content; violates §30/§64.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Any MCP server, validate responses only

**Description.** Open server set, validate outputs.
**Strengths.** Flexible.
**Weaknesses.** No supply-chain control; unknown servers; scope creep.
**Cost / effort.** Low; risky.

### 5.4 Option D — No MCP (only first-party tools/enterprise APIs)

**Description.** Disallow MCP entirely.
**Strengths.** Smallest surface.
**Weaknesses.** Loses MCP extensibility where genuinely useful.
**Cost / effort.** Low; limiting.

### 5.5 Option E — Allowlist + validation + sandboxed/isolated MCP invocation

**Description.** Option A plus network/process isolation for MCP calls (dedicated egress,
no access to sensitive zones).
**Strengths.** Contains a compromised server.
**Weaknesses.** More infra.
**Cost / effort.** Medium-high.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Implicit MCP trust | doc 19 §62 |
| Unpinned MCP versions | doc 18 §50 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by doc 18 §30/§47–§50 and doc 19
§61–§64.

| Criterion | Weight | A: Allowlist+validate | B: Trust responses | C: Any server+validate | D: No MCP | E: A+sandbox |
|---|---|---|---|---|---|---|
| EC-01 Trust control | 28 | 5 | 4 | 2 | 5 | 5 |
| EC-02 Response safety | 26 | 5 | 1 | 5 | 5 | 5 |
| EC-03 Authz consistency | 18 | 5 | 4 | 4 | 5 | 5 |
| EC-04 Auditability | 14 | 5 | 3 | 3 | 4 | 5 |
| EC-05 Extensibility | 14 | 4 | 4 | 5 | 1 | 4 |
| **Weighted total** | **100** | **484** | **300** | **380** | **440** | **492** |

Totals (×20): **E = 492**, **A = 484**, **D = 440**, **C = 380**, **B = 300**.

**Sensitivity.** E (A + sandboxing) edges A by containing a compromised server. Sandbox
isolation is adopted for MCP servers handling anything sensitive or less-trusted; A is
the baseline for well-trusted internal MCP servers. No-MCP (D) is the safe fallback if
MCP is not needed. B is unsafe.

## 7. Decision

**PFF AI will treat MCP servers as semi-trusted: only allowlisted, version-pinned MCP
servers and tools are usable; all MCP responses are validated, schema-checked and
injection-checked as untrusted content; MCP calls go through the harness allowlist and
authorization (Option A), with network/process sandboxing for any less-trusted or
sensitive MCP server (Option E enhancement).** If MCP is not needed, it is disabled (D).
Trusting responses (B) and open server sets (C) are rejected.

## 8. Architecture Detail

- `src/pf_ft_ai/integration/mcp/`: MCP client restricted to allowlisted servers/tools
  (doc 18 §48–§49) with pinned versions (§50); calls routed through the harness
  (ADR-D6-10) with authorization (ADR-D6-03).
- Responses validated (schema + safety) and passed through the injection guardrail
  (ADR-D6-08/D6-09) before reasoning (doc 19 §64).
- Sensitive/less-trusted MCP servers invoked from an isolated egress path (ADR-D6-04)
  with no access to sensitive zones.
- Server onboarding is a governed change (ADR-D6-15).

## 9. Consequences

### 9.1 Positive
- MCP extensibility with supply-chain + injection control and containment.
### 9.2 Negative
- Onboarding/governance per server; sandbox infra where used.
### 9.3 Neutral
- Specialises tool security (D6-10) for MCP.
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Open MCP flexibility | Supply-chain + injection safety | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | MCP tools act within allowed scope; not authoritative |
| Precedence chain | MCP output validated, ranked below authoritative sources |
| Four-state separation | MCP responses validated before touching state |
| Versioned artefacts | MCP server/tool versions pinned |
| Adam persona governs *how*, not *what* | MCP cannot inject business truth |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Compromised MCP server injects content | Low | High | M | Response validation + injection guard + sandbox | Security Architect | Low |
| RSK-02 | Version drift breaks compatibility | Low | Med | M | Pinned versions (§50) | Integration Eng | Low |
| RSK-03 | Unapproved server used | Low | High | M | Allowlist + governance | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Non-allowlisted MCP calls | 0 | > 0 | Boundary tests | Continuous |
| QM-02 | MCP responses validated | 100% | < 100% | Audit | Per release |
| QM-03 | MCP version mismatches | 0 | > 0 | Compatibility check | Per release |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Controls an external-integration surface |
| Data classification touched | MCP payloads (per classification) |
| Personal data / PII | Minimised to MCP calls; validated responses |
| Children's data and safeguarding | Sandboxed/scoped for sensitive MCP |
| UK GDPR lawful basis and rights impact | Controlled external processing |
| Audit and evidential requirements | MCP calls + validations logged |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 9 |
| Repository paths | `src/pf_ft_ai/integration/mcp/` |
| Configuration | Server/tool allowlist; versions; sandbox |
| Contracts / schemas | MCP response validation |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D6-10, D2-13, D6-08/09, D3-04 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Only allowlisted servers/tools callable | Boundary test |
| AC-02 | Responses validated + injection-checked | Test |
| AC-03 | Versions pinned/compatible | Compatibility test |
| AC-04 | Sensitive MCP sandboxed | Network review |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | MCP call metrics; validation failures |
| Alerting | Non-allowlisted attempts; response-validation failures |
| Runbook | `docs/runbooks/mcp.md` |
| Failure mode and degradation | Invalid/unknown MCP → block |
| Rollback | Allowlist/version revert |
| Support model impact | Security + integration |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| MCP allowlist + validation | M | small | Build |
| Sandbox (where used) | M | small | Isolated egress |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Less-trusted MCP server needed | Onboarding | Mandate sandbox (E) |
| RT-02 | MCP-security incident | Incident | CAR; revoke/patch server |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-27 |
| Specification sections | doc 18 §30, §47–§50; doc 19 §61–§64 |
| Requirement IDs | SEC-MCP-* |
| Build phases | 9 |
| Code paths | `src/pf_ft_ai/integration/mcp/` |
| Configuration | server/tool allowlist |
| Tests | MCP security suites |
| Upstream ADRs | ADR-D6-10, D2-13 |
| Downstream ADRs | ADR-D6-15 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
