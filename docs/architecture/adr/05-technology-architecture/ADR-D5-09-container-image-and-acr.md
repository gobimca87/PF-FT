---
id: ADR-D5-09
title: Container image, ACR and image-immutability policy
domain: 5 Technology
ws_ref: [WS-24]
status: Accepted
version: 1.0.0
date: 2026-08-22
decision_owner: Platform Engineer
contributors: [Security Architect, SRE, Backend Lead]
reviewers: [Principal Architect]
approver: Architecture Review Board
supersedes: []
superseded_by: []
related_adrs: [ADR-D5-08, ADR-D5-04, ADR-D6-18, ADR-D7-10, ADR-D5-06]
source_docs:
  - "MD files/6 Production/25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14, §15, §16, §17, §18, §69"
build_phases: [1]
impacted_paths:
  - Dockerfile
  - infra/
classification: Internal
review_due: 2027-08-22
---

# ADR-D5-09 — Container image, ACR and image-immutability policy

## 1. Summary

PFF AI will build **minimal, multi-stage, non-root container images**, publish them to
**Azure Container Registry (ACR)** with **immutable, digest-pinned tags**, vulnerability
scanning and (target) signing, and deploy images **by digest** so what runs is exactly
what was built and scanned (25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14–§18, §69). No `latest`, no in-place tag reuse.

## 2. Context and Problem Statement

25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14 defines the container image, §15 the registry (ACR), §16 image immutability,
§17–§18 container/runtime security, §69 the build artifact. Mutable tags let a
different image run than the one tested/scanned — a supply-chain and reproducibility
hazard. This ADR fixes image build, registry and immutability.

## 3. Decision Drivers

| ID | Driver | Source |
|---|---|---|
| DR-F-01 | Immutable, digest-pinned images in ACR | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §15–§16 |
| DR-F-02 | Minimal, non-root, hardened images | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14, §17–§18 |
| DR-C-01 | Deploy by digest (what built = what runs) | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §16; ADR-D5-06 |
| DR-N-01 | Vulnerability scan (+ signing target) | ADR-D6-18 |

### 3.4 Assumptions

| ID | Assumption | If false | Validation |
|---|---|---|---|
| DR-A-01 | ACR available in tenancy | Alternative registry in Azure | Infra review |

## 4. Evaluation Criteria and Weights

| ID | Criterion | Weight | Rationale | Measurement |
|---|---|---|---|---|
| EC-01 | Immutability/reproducibility | 28 | What-runs = what-built | Digest deploys |
| EC-02 | Security (minimal/non-root/scan/sign) | 26 | Attack surface | Hardening + scan |
| EC-03 | Azure-native integration | 18 | ACR↔AKS↔MI | Native auth |
| EC-04 | Build speed/size | 16 | CI + pull time | Image size |
| EC-05 | Simplicity | 12 | Maintainability | Concepts |
| | **Total** | **100** | | |

## 5. Alternatives Considered

### 5.1 Option A — Multi-stage minimal non-root image + ACR + digest-pinned immutable tags + scan/sign

**Description.** Multi-stage build (slim base, e.g. distroless/slim), non-root user;
push to ACR with immutable tags; deploy by digest; Defender/Trivy scan; cosign signing
(target); MI-based ACR auth.
**Strengths.** Reproducible, secure, Azure-native.
**Weaknesses.** Signing pipeline is extra setup (target, not day-1).
**Cost / effort.** Low-medium.

### 5.2 Option B — Single-stage image, mutable tags (e.g. `latest`)

**Description.** Simple build, floating tags.
**Strengths.** Simplest.
**Weaknesses.** Non-reproducible; wrong image can run; larger; violates §16.
**Cost / effort.** Low; unsafe.

### 5.3 Option C — Docker Hub / external registry

**Description.** Public/external registry.
**Strengths.** Familiar.
**Weaknesses.** Off-tenancy; rate limits; weaker MI/private integration than ACR.
**Cost / effort.** Low; misaligned.

### 5.4 Option D — Buildpacks (no Dockerfile)

**Description.** Cloud Native Buildpacks.
**Strengths.** No Dockerfile maintenance; good defaults.
**Weaknesses.** Less control over hardening/GPU base for SLM; opaque layers.
**Cost / effort.** Low-medium; less control.

### 5.5 Option E — Multi-stage + ACR but mutable environment tags (e.g. `:prod`)

**Description.** Immutable build tags but a moving `:prod` pointer.
**Strengths.** Convenient promotion pointer.
**Weaknesses.** Moving tag reintroduces ambiguity; deploy-by-digest is safer (manifest
holds digest, ADR-D5-06).
**Cost / effort.** Low; weaker guarantee.

### 5.6 Options considered and eliminated before scoring

| Option | Eliminated by |
|---|---|
| Root-running containers | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §17–§18 |
| `latest` in production | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §16 |

## 6. Evaluation Method and Decision Matrix

**Method.** Weighted scoring against §4, informed by 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14–§18/§69 and ADR-D6-18.

| Criterion | Weight | A: multi-stage+ACR+digest | B: mutable tags | C: ext registry | D: buildpacks | E: moving :prod tag |
|---|---|---|---|---|---|---|
| EC-01 Immutability | 28 | 5 | 1 | 3 | 3 | 3 |
| EC-02 Security | 26 | 5 | 2 | 3 | 4 | 4 |
| EC-03 Azure-native | 18 | 5 | 3 | 1 | 4 | 5 |
| EC-04 Build speed/size | 16 | 4 | 3 | 3 | 4 | 4 |
| EC-05 Simplicity | 12 | 4 | 5 | 4 | 4 | 4 |
| **Weighted total** | **100** | **468** | **248** | **282** | **376** | **392** |

Totals (×20): **A = 468**, **E = 392**, **D = 376**, **C = 282**, **B = 248**.

**Sensitivity.** A leads E by 76 — the deploy-by-digest guarantee is the differentiator;
E's moving `:prod` tag reintroduces exactly the ambiguity §16 forbids. No re-weighting
favours mutable tags.

## 7. Decision

**PFF AI will build multi-stage, minimal, non-root container images, publish them to
ACR with immutable digest-pinned tags, scan them for vulnerabilities (signing as a
target), and deploy by digest via the release manifest (Option A).** Managed-Identity
auth to ACR (ADR-D5-08). Mutable tags (B/E), external registries (C) and buildpacks
(D) are rejected.

**Status rationale.** `Accepted` — 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14–§18 govern this.

## 8. Architecture Detail

- `Dockerfile`: multi-stage (build → slim runtime), non-root `USER`, no build tools in
  the final layer; installs from the committed lock (ADR-D5-04) for reproducibility.
- ACR: immutable tag policy (§16); image scanned (Defender/Trivy, ADR-D6-18); digest
  recorded in the release manifest (ADR-D5-06); deploy references the digest.
- Runtime security (§17–§18): read-only FS where possible, dropped capabilities,
  seccomp; MI-based pull auth.

## 9. Consequences

### 9.1 Positive
- What ran = what was built and scanned; smaller attack surface.
### 9.2 Negative
- Signing pipeline is additional setup (phased).
### 9.3 Neutral
- Ties to lock (D5-04) and manifest (D5-06).
### 9.4 Trade-offs explicitly accepted

| Given up | In exchange for | Accepted by |
|---|---|---|
| Convenience of moving tags | Reproducibility + supply-chain integrity | Platform Eng |

## 10. Golden-Rule and Precedence Conformance

| Constraint | Conformance |
|---|---|
| Enterprise decides; AI orchestrates | Infra artefact; no business authority |
| Precedence chain | N/A |
| Four-state separation | N/A |
| Versioned artefacts | Images immutable, digest-pinned in manifest |
| Adam persona governs *how*, not *what* | N/A |

## 11. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Exposure | Mitigation | Owner | Residual |
|---|---|---|---|---|---|---|---|
| RSK-01 | Vulnerable base image | Med | High | H | Scan + minimal base + patch cadence | Security Architect | Low |
| RSK-02 | Wrong image deployed | Low | High | M | Deploy-by-digest via manifest | Platform Eng | Low |
| RSK-03 | Supply-chain tampering | Low | High | M | Signing (target) + scan | Security Architect | Med |

## 12. Quantitative Targets and Measures

| ID | Measure | Target | Threshold (alert) | Source | Review cadence |
|---|---|---|---|---|---|
| QM-01 | Deploys by digest | 100% | < 100% | CD | Per deploy |
| QM-02 | Images with high/critical CVEs in prod | 0 | > 0 | Scanner | Continuous |
| QM-03 | Non-root images | 100% | < 100% | Image policy | Per build |

## 13. Security, Privacy and Compliance Impact

| Dimension | Impact |
|---|---|
| Attack surface change | Minimal non-root images; scanned; immutable |
| Data classification touched | Internal |
| Personal data / PII | None in images |
| Children's data and safeguarding | N/A |
| UK GDPR lawful basis and rights impact | N/A |
| Audit and evidential requirements | Image digests + scan results (SBOM) |
| Standards touched | ISO/IEC 27001, NIST SSDF |

## 14. Implementation Impact

| Aspect | Detail |
|---|---|
| Build phases | 1 |
| Repository paths | `Dockerfile`, `infra/` |
| Configuration | ACR policy; scan config |
| Contracts / schemas | Manifest image digest |
| Migration | N/A |
| Dependencies on other ADRs | ADR-D5-04, D5-06, D5-08, D6-18 |
| Effort estimate | M |

## 15. Validation and Verification

| ID | Acceptance criterion | Verification method |
|---|---|---|
| AC-01 | Images immutable + digest-deployed | ACR policy + CD check |
| AC-02 | Non-root, minimal | Image inspection |
| AC-03 | Scan gates promotion | CI/CD gate |
| AC-04 | Built from committed lock | Build audit |

## 16. Operational Impact

| Aspect | Detail |
|---|---|
| Monitoring | Image CVE posture; pull errors |
| Alerting | New critical CVE in running image |
| Runbook | `docs/runbooks/images.md` |
| Failure mode and degradation | Bad image → rollback to prior digest |
| Rollback | Deploy previous digest |
| Support model impact | Platform + security |

## 17. Cost Impact

| Cost element | One-off | Recurring | Basis |
|---|---|---|---|
| ACR | setup | storage/egress | Azure pricing |
| Scanning | setup | per-scan | Defender/Trivy |

## 18. Revisit Triggers and Causal Analysis Hooks

| ID | Trigger | Detected by | Action on trigger |
|---|---|---|---|
| RT-01 | Supply-chain incident | Incident | Prioritise signing/attestation |
| RT-02 | Image sizes/pull times grow | Metrics | Optimise layers/base |

**Scheduled review:** `review_due`.

## 19. Traceability

| Dimension | Reference |
|---|---|
| Workshop sheet | WS-24 |
| Specification sections | 25.PFF-FA-AI-INFRASTRUCTURE-OPERATIONS.md §14–§18, §69 |
| Requirement IDs | INFRA-IMG-* |
| Build phases | 1 |
| Code paths | `Dockerfile`, `infra/` |
| Configuration | ACR/scan |
| Tests | image policy tests |
| Upstream ADRs | ADR-D5-04, D5-08 |
| Downstream ADRs | ADR-D6-18, D7-10 |

## 20. Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-08-22 | Platform Engineer | Initial decision recorded. |
