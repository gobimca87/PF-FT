---
id: ADR-D5-07
title: Secret management — Azure Key Vault with `*_secret_ref` indirection
domain: 5 Technology
ws_ref: [WS-23]
status: Accepted
version: 1.1.0
date: 2026-08-22
decision_owner: Security Architect
contributors: [Platform Engineer, Backend Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-06, ADR-D5-08, ADR-D6-05, ADR-D6-04, ADR-D5-09, ADR-D5-20]
source_docs:
  - "MD files/4 AI/17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6, §7, §10"
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28, §30, §31, §32"
build_phases: [1, 7]
impacted_paths:
  - src/pff_fa_ai/config/
classification: Confidential
review_due: 2027-08-22
---

# ADR-D5-07 — Secret management — Azure Key Vault with `*_secret_ref` indirection

> **Amendment (v1.1.0, 2026-09-05) — Key Vault access mechanism.** Per the enterprise
> application standard (**ADR-D5-20**, owner decision), PFF AI authenticates to Key Vault
> **only** through the enterprise **service principal (MI-SPN)** — tenant id + client id +
> client secret, held in the Azure DevOps pipeline variable group and injected into the
> workload environment — **not** through Managed Identity. This **changes the access
> mechanism** of §7 (and relaxes DR-F-02 / EC-02 "no static credentials") for the Key Vault
> connection: the SPN client secret is itself a pipeline-held / Key-Vault-linked secret, so
> exposure stays minimal. **Everything else in this ADR stands** — secrets live in Key
> Vault, are referenced only through `*_secret_ref` indirection resolved at load time, reach
> the vault over a private endpoint, support rotation without redeploy, and are never
> committed, baked or logged. The single supported client is
> `KeyVaultSecretResolver` / `AzureKeyVaultSecretClient` in
> `src/pff_fa_ai/configuration/secrets.py` (`ClientSecretCredential` only; no
> `DefaultAzureCredential`, no CLI/interactive credential, no managed identity).

## 1. Summary

PFF AI will store all secrets in **Azure Key Vault**, accessed at runtime via **Azure
Managed Identity** (no secrets in images, env files or YAML), with configuration
referencing secrets only through **`*_secret_ref` indirection** that resolves to a Key
Vault secret at load time (17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6–§7, §10; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28, §30–§32). Secrets are never
committed, logged or baked in.

## 2. Context and Problem Statement

17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6 separates configuration from secrets, §7 defines secret references, §10
forbids YAML becoming the runtime secret source; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28/§30–§32 define managed
identity, Key Vault and secret management. Leaked secrets are among the highest-impact
security failures. This ADR fixes where secrets live and how they are referenced and
retrieved.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Secrets in Key Vault, referenced not embedded | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6–§7; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §30–§31 |
| DR-F-02 | Managed Identity access (no static creds) | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28 |
| DR-C-01 | No secrets in YAML/images/logs | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §10; ADR-D5-06 |
| DR-N-01 | Rotation without redeploy | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §31; ADR-D6-05 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | Managed Identity available on AKS | Use workload identity federation | Infra review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Secret confidentiality (no leakage) | 32 | Highest-impact risk | Leak surface |
| EC-02 | Azure-native + Managed Identity | 22 | No static creds | Identity-based access |
| EC-03 | Rotation support | 18 | Reduce exposure window | Rotate w/o redeploy |
| EC-04 | Auditability | 16 | Access logging | Audit logs |
| EC-05 | Simplicity/ops | 12 | Maintainability | Integration effort |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Azure Key Vault + Managed Identity + `*_secret_ref` resolution at load

**Description.** Secrets in Key Vault; app uses Managed Identity; config holds
`*_secret_ref` keys resolved to KV secrets at startup into the immutable runtime config
(ADR-D5-06); private endpoint to KV (ADR-D6-04).
**Strengths.** Azure-native; no static creds; rotation; audited; no secrets in
YAML/image/logs.
**Weaknesses.** KV dependency at startup (mitigated by caching/retry).
**Cost / effort.** Low-medium.

### 5.2 Option B — Kubernetes Secrets only

**Description.** Store secrets as K8s Secrets.
**Strengths.** Native to AKS; simple.
**Weaknesses.** Base64 (not encrypted by default) unless extra config; weaker rotation/
audit than KV; secrets in etcd.
**Cost / effort.** Low; weaker.

### 5.3 Option C — Environment variables / .env files

**Description.** Secrets via env vars.
**Strengths.** Simplest.
**Weaknesses.** Easily leaked (logs, crash dumps, process listings); no rotation/audit;
violates 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §10.
**Cost / effort.** Low; unsafe.

### 5.4 Option D — HashiCorp Vault (self-hosted)

**Description.** Run Vault.
**Strengths.** Powerful; dynamic secrets; multi-cloud.
**Weaknesses.** Operate a stateful HA secret store; overkill vs Azure-native KV for a
single-cloud platform.
**Cost / effort.** High ops.

### 5.5 Option E — Key Vault + CSI Secrets Store driver (mount as files)

**Description.** KV secrets mounted into pods via CSI driver.
**Strengths.** KV-backed; secrets as mounted files; auto-rotation with the driver.
**Weaknesses.** Secrets on the pod filesystem (broader exposure than in-memory resolve);
extra driver to manage. A viable variant of A.
**Cost / effort.** Low-medium.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Secrets in Git (even encrypted-at-rest repo) | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §10 — never |
| Baking secrets into the image | ADR-D5-09 image immutability + leakage |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6–§10 and 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28–§32.

| Criterion | Weight | A: KV+MI+ref | B: K8s Secrets | C: env/.env | D: Vault | E: KV+CSI |
|---|---|---|---|---|---|---|
| EC-01 Confidentiality | 32 | 5 | 3 | 1 | 5 | 4 |
| EC-02 Azure-native/MI | 22 | 5 | 4 | 2 | 3 | 5 |
| EC-03 Rotation | 18 | 5 | 2 | 1 | 5 | 5 |
| EC-04 Auditability | 16 | 5 | 3 | 1 | 5 | 5 |
| EC-05 Simplicity/ops | 12 | 4 | 5 | 5 | 2 | 4 |
| **Weighted total** | **100** | **488** | **328** | **192** | **426** | **456** |

Totals (×20): **A = 488**, **E = 456**, **D = 426**, **B = 328**, **C = 192**.

**Sensitivity.** A leads E by 32; E (CSI mount) is a close, valid KV-backed variant but
places secrets on the pod filesystem, slightly widening exposure vs in-memory
resolution. Both are KV+Managed Identity; A is chosen, with E available where
file-mount ergonomics are needed (RT-01). C is rejected outright.

## 7. Decision

**PFF AI will store all secrets in Azure Key Vault, access them via Azure Managed
Identity, and reference them in configuration only through `*_secret_ref` indirection
resolved at load time into the immutable runtime config (Option A);** Key Vault is
reached over a private endpoint (ADR-D6-04) and rotation is supported without redeploy
(ADR-D6-05). The CSI Secrets Store variant (E) is permitted where file-mounted secrets
are required. K8s-Secrets-only (B), env/.env (C) and self-hosted Vault (D) are
rejected. No secret is ever committed, baked, or logged.

**Status rationale.** `Accepted` — 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6–§10 and 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §30–§32 govern this.

## 8. Architecture Detail

- `src/pff_fa_ai/config/`: a secret resolver reads `*_secret_ref` values and fetches
  from Key Vault via Managed Identity at startup (§7); resolved secrets live only in
  the in-memory immutable config, never persisted.
- Private endpoint to KV (ADR-D6-04); RBAC on KV; access audited (§64; ADR-D6-17).
- Log redaction ensures secrets never appear in logs (ADR-D7-04).
- Rotation: KV secret versions updated; app re-resolves on restart/refresh (ADR-D6-05).

## 9. Consequences

### 9.1 Positive
- Strong confidentiality, no static creds, rotation, full audit.
### 9.2 Negative
- KV dependency at startup (mitigated by retry/caching).
### 9.3 Neutral
- Integrates with config/manifest (D5-06).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Simplicity of env vars | Confidentiality + rotation + audit | Security Architect |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Secrets protect integrations; no business authority |
| Precedence chain | N/A |
| Four-state separation | Secrets not part of runtime state stores |
| Versioned artefacts | Secret *references* versioned; values in KV |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Secret leaked in logs | Low | High | M | Redaction (ADR-D7-04); scanning | Security Architect | Low |
| RSK-02 | KV unavailable at startup | Low | High | M | Retry/backoff; cached resolution | Platform Eng | Low |
| RSK-03 | Over-broad KV access | Low | High | M | Least-privilege RBAC; per-identity scoping | Security Architect | Low |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Secrets found in code/config/logs | 0 | > 0 | Secret scan | Continuous |
| QM-02 | Static credentials in use | 0 | > 0 | Identity audit | Quarterly |
| QM-03 | Secret rotation adherence | per policy | overdue | KV audit | Quarterly |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Centralised, audited, identity-based secret access |
| Data classification touched | Confidential |
| Personal data / PII | Secrets protect systems holding PII |
| Children's data and safeguarding | Protects access to safeguarding-related systems |
| UK GDPR lawful basis and rights impact | Supports security-of-processing obligation |
| Audit and evidential requirements | KV access logs |
| Standards touched | ISO/IEC 27001, 42001 |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1, 7 |
| Repository paths | `src/pff_fa_ai/config/` |
| Configuration | `*_secret_ref` keys; KV name |
| Contracts / schemas | Secret-ref config schema |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-06, D5-08, D6-04, D6-05 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | No secret literals in repo/config/image | Secret scan |
| AC-02 | Access via Managed Identity, no static creds | Identity audit |
| AC-03 | Secrets resolved into in-memory config only | Code review |
| AC-04 | Secrets absent from logs | Redaction test |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | KV access metrics; resolution failures |
| Alerting | KV unavailable; unauthorized access attempt |
| Runbook | `docs/runbooks/secrets.md` |
| Failure mode and degradation | KV down → retry; startup fails closed if unresolved |
| Rollback | Revert secret-ref config |
| Support model impact | Security + platform |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| Key Vault | setup | low per-op | Azure KV pricing |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | File-mounted secrets needed | Ops | Adopt CSI variant (Option E) |
| RT-02 | Secret-leak incident | Incident | CAR; tighten redaction/scanning |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-23 |
| Specification sections | 17.PFF-FA-AI-CONFIGURATION-VERSIONING.md §6–§7, §10; 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §28, §30–§32 |
| Requirement IDs | SEC-KV-* |
| Build phases | 1, 7 |
| Code paths | `src/pff_fa_ai/config/` |
| Configuration | secret-ref config |
| Tests | secret-scan + redaction suites |
| Upstream ADRs | ADR-D5-06, D5-08 |
| Downstream ADRs | ADR-D6-04, D6-05 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Security Architect | Initial decision recorded. |
| 1.1.0 | 2026-09-05 | Security Architect | Access-mechanism amendment: Key Vault is authenticated **only** via the enterprise SPN (client credentials) per ADR-D5-20, not Managed Identity (changes DR-F-02/EC-02 for the vault connection). All other aspects — KV storage, `*_secret_ref` indirection, private endpoint, rotation, no secrets in images/logs — unchanged. Forward-reference + related_adrs added. Realized in `src/pff_fa_ai/configuration/secrets.py`. |
