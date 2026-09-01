# PFF AI — Open Decisions Register

> The ADRs below carry `status: Proposed`: each presents a complete CMMI-DAR evaluation
> and a **stated recommendation**, but is **not yet Accepted** — it awaits the sign-off
> named in its row. This register is governed by
> [ADR-D0-04](../00-decision-programme/ADR-D0-04-open-decision-register-and-escalation.md)
> and listed as a verification target by
> [ADR-D8-07](../08-business-value/ADR-D8-07-decision-register-and-traceability.md).
> Generated 2026-08-22.

Four of these were flagged open from the outset in `CLAUDE.md` / `DEVELOPMENT-GUIDE.md`
§2 (vector store, SLM serving stack, IaC tool, K8s manifest tool). The fifth
(**ADR-D3-23 embedding model**) is Proposed because 14.PFF-FA-AI-EMBEDDING-VECTOR.md §13 mandates that the
embedding model be chosen by a PFF-FA-specific retrieval evaluation, not by reputation —
so its recommendation is explicitly provisional on that evaluation.

| ADR | Decision | Recommendation | Awaiting | Gated at phase |
|---|---|---|---|---|
| [ADR-D3-23](../03-ai-architecture/ADR-D3-23-embedding-model-selection-and-re-embedding.md) | Embedding model selection | HF-hosted general-purpose **768-dim (`bge-base-en-v1.5` class)**; fallback 1024-dim | PFF-FA retrieval evaluation (Recall@5 ≥ 0.90) then ARB sign-off | 8 |
| [ADR-D3-24](../03-ai-architecture/ADR-D3-24-vector-store-selection.md) | Vector store selection | **Azure AI Search** (vector + hybrid); fallback pgvector on Azure Postgres | ARB sign-off | 8 |
| [ADR-D5-10](../05-technology-architecture/ADR-D5-10-self-hosted-slm-serving-stack.md) | Self-hosted SLM serving stack | **vLLM** on AKS GPU; fallbacks Azure ML / TGI / Triton | Throughput/latency/quality benchmark on chosen model + SKU, then ARB | 20 |
| [ADR-D5-12](../05-technology-architecture/ADR-D5-12-iac-tool.md) | Infrastructure-as-Code tool | **Terraform** (OpenTofu-compatible); fallback Azure Bicep | Platform-team house-standard confirmation | 1 |
| [ADR-D5-13](../05-technology-architecture/ADR-D5-13-kubernetes-manifest-tool.md) | Kubernetes manifest tool | **Kustomize** for first-party; Helm hybrid for third-party charts | Platform-team confirmation | 1 |

## How an open decision is closed

1. The awaited evidence is produced (evaluation, benchmark) or the named approver signs off.
2. The ADR's `status` changes `Proposed → Accepted` (a new version per
   [ADR-D0-02](../00-decision-programme/ADR-D0-02-adr-identification-lifecycle-supersession.md)),
   with the confirming evidence recorded in its Change Log and §7 Status rationale.
3. If the evaluation selects a different option than the recommendation, the ADR is
   updated to record the selected option and why — the recommendation was always
   provisional on the evidence.
4. This register and the decision register are regenerated; the row moves out of "open".

**Note on count:** the programme plan anticipated exactly four open decisions; a fifth
(ADR-D3-23) is Proposed as a deliberate, documented consequence of 14.PFF-FA-AI-EMBEDDING-VECTOR.md §13's
evaluation-first requirement — recording it as Proposed is more faithful than marking it
Accepted before the mandated retrieval evaluation has run.
