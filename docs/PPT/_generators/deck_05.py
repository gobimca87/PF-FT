#!/usr/bin/env python3
"""Deck 05 — Technology & Infrastructure (D5), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "05-technology-infrastructure.pptx")


def svc(d, s, logo, label, x, y, w=1.9, h=0.8):
    d.card(s, x, y, w, h)
    d.image(s, logo, x + 0.12, y + (h - 0.46) / 2, h=0.46)
    d.text(s, label, x + 0.66, y + 0.12, w - 0.74, h - 0.2, size=10, color=NAVY, bold=True,
           anchor=MSO_ANCHOR.MIDDLE)


def topology(d, s):
    # tenancy boundary
    d.card(s, CX0, 1.62, CW, 4.55)
    d.text(s, "AZURE TENANCY · UK South", CX0 + 0.18, 1.68, 6, 0.3, size=10, color=BLUE, bold=True)
    d.box(s, "Chat UI", CX0 + 0.15, 3.25, 1.0, 0.65, style="light", size=10)
    svc(d, s, "apim", "APIM\nauthN/Z", CX0 + 1.25, 3.2, 1.35, 0.8)
    # AKS cluster
    d.card(s, CX0 + 2.85, 1.98, 3.95, 3.95)
    d.image(s, "aks", CX0 + 3.0, 2.08, h=0.45)
    d.text(s, "AKS cluster", CX0 + 3.6, 2.12, 3.0, 0.4, size=13, color=NAVY, bold=True, font="Cambria")
    d.box(s, "System node pool\nFastAPI · LangGraph · Agent Harness",
          CX0 + 3.0, 2.7, 3.65, 1.3, style="light", size=10.5)
    d.box(s, "GPU node pool\nvLLM — self-hosted SLM (target)",
          CX0 + 3.0, 4.15, 3.65, 1.3, style="navy", size=10.5)
    # data services
    svc(d, s, "aisearch", "Azure AI Search", CX0 + 7.0, 2.05, 1.85, 0.72)
    svc(d, s, "redis", "Managed Redis", CX0 + 7.0, 2.87, 1.85, 0.72)
    svc(d, s, "servicebus", "Service Bus", CX0 + 7.0, 3.69, 1.85, 0.72)
    svc(d, s, "blob", "Blob Storage", CX0 + 7.0, 4.51, 1.85, 0.72)
    # platform services
    svc(d, s, "keyvault", "Key Vault (SPN)", CX0 + 8.95, 2.05, 1.85, 0.72)
    svc(d, s, "acr", "ACR", CX0 + 8.95, 2.87, 1.85, 0.72)
    svc(d, s, "monitor", "Monitor / App Ins.", CX0 + 8.95, 3.69, 1.85, 0.72)
    svc(d, s, "langfuse", "Langfuse", CX0 + 8.95, 4.51, 1.85, 0.72)
    # external SLM
    d.box(s, "External SLM (Hugging Face) — masked / tokenised payloads only, fail-closed",
          CX0 + 2.85, 6.32, 6.0, 0.5, style="accent", size=10)
    d.connector(s, CX0 + 1.15, 3.55, CX0 + 1.25, 3.55, color=BLUE, width=1.3)
    d.connector(s, CX0 + 2.6, 3.55, CX0 + 2.85, 3.55, color=BLUE, width=1.3)
    d.connector(s, CX0 + 6.8, 3.5, CX0 + 7.0, 3.4, color=BLUE, width=1.2)


def build():
    d = Deck()
    d.title_slide("Technology &", "Infrastructure",
                  "Azure · AKS · APIM · Key Vault · vLLM/GPU · enterprise delivery  —  D5 (20 ADRs, 1 open)",
                  kicker="Deck 05 · Technology architecture",
                  notes="The concrete technology and Azure infrastructure. One ADR is Proposed (the "
                        "self-hosted vLLM serving stack, deck 09). IaC, K8s and the delivery model are Accepted.")

    d.agenda_slide("What this deck covers", [
        "Target infrastructure topology on Azure",
        "Engineering stack — language, typing, validation, deps, lint",
        "Configuration & release manifest",
        "Secret management — Key Vault, SPN-only",
        "Compute — AKS, containers/ACR, GPU node pool",
        "Self-hosted SLM serving (vLLM) & VRAM/KV-cache planning",
        "APIM authZ boundary & shared HTTP client",
        "Five-stage environment model",
        "Enterprise delivery model — Azure DevOps CI/CD on shared AKS",
        "Scalability, autoscaling & latency budgets",
    ])

    s = d.content_slide("Target infrastructure topology", kicker="System overview",
                        subtitle="on Microsoft Azure — UK South")
    topology(d, s)
    d.set_notes(s, "The whole platform runs in one Azure tenancy. APIM is the authZ boundary in front "
                   "of the AKS cluster (system node pool for the app; GPU node pool for self-hosted "
                   "vLLM). Data/platform services are Azure-native. The only egress is to the external "
                   "SLM, and only masked payloads cross that boundary (deck 06). Every service has a cost line in deck 08.")

    s = d.content_slide("Engineering stack", kicker="D5-01/02/03/04/05")
    d.chip_row(s, [("python", "Python"), ("fastapi", "FastAPI"), ("pydantic", "Pydantic"),
                   ("ruff", "Ruff")], y=2.0, size=0.8)
    d.bullets(s, [
        "Python + FastAPI; a single project type checker (mypy or pyright) chosen at Phase 0.",
        "Pydantic validates every boundary (API, tool, config, event, ERC, SLM); TypedDict for graph state.",
        "Dependencies pinned with a lock file; Ruff for lint/format; conventional commits & semantic versioning.",
    ], CX0, 3.9, CW, 2.2, size=15, gap=13)
    d.set_notes(s, "The engineering stack is deliberately conventional and strict: typed boundaries, "
                   "pinned deps, one linter, one type checker.")

    s = d.content_slide("Configuration & release manifest", kicker="D5-06")
    d.bullets(s, [
        "Config precedence: Base → Environment → Deployment override → Secret reference.",
        "Schema-validated & fail-fast: invalid mandatory config ⇒ the app never becomes READY.",
        "Immutable release manifest with a configuration_hash (SHA-256) for drift detection.",
        "Prompts, models, agents, workflows, RAG indexes, guardrails are all versioned artifacts in the bundle.",
    ], CX0, 1.95, CW, 3.8, size=16, gap=14)
    d.set_notes(s, "Configuration is layered, schema-validated and fail-fast; a release is an immutable, "
                   "hashed manifest enabling drift detection and safe promotion.")

    s = d.content_slide("Secret management — Key Vault, SPN-only", kicker="D5-07 / D5-20")
    d.image(s, "keyvault", CX0, 2.1, h=1.1)
    d.kv_panel(s, "The only path to the vault", [
        ("Credential", "enterprise service principal (MI-SPN): tenant + client id + secret"),
        ("No alternatives", "no DefaultAzureCredential, CLI, interactive, or bare MI"),
        ("Injection", "Azure DevOps variable group → workload env"),
        ("Resolution", "every *_secret_ref resolved from Key Vault; fail-closed in deployed envs"),
    ], CX0 + 2.2, 1.95, 8.45, 3.5, col=GOLD)
    d.text(s, "Local dev/test may use process-env; deployed environments are SPN-backed and fail-closed.",
           CX0 + 2.2, 5.6, 8.45, 0.5, size=13, color=GREY)
    d.set_notes(s, "Key Vault is reached only via the enterprise SPN — no other credential method; "
                   "secrets are never inline; deployed environments fail closed.")

    s = d.content_slide("Compute — AKS, containers, GPU", kicker="D5-08 / D5-09 / D5-11")
    d.two_col(s, "Cluster & images", [
        "Azure / AKS is the compute platform.",
        "Containerised workloads; images in ACR.",
        "System node pool runs the app runtime.",
    ], "GPU & workload separation", [
        "Dedicated GPU node pool for self-hosted SLM.",
        "AI workloads separated from app workloads (D5-11).",
        "GPU is the dominant cost lever — deck 08.",
    ])
    d.set_notes(s, "AKS with separated system and GPU node pools; images from ACR; workload separation "
                   "isolates GPU cost and scaling.")

    s = d.content_slide("Self-hosted SLM serving & capacity", kicker="D5-10 (PROPOSED) / D5-19")
    d.kv_panel(s, "Serving stack — recommendation", [
        ("Stack", "vLLM on AKS GPU"),
        ("Fallbacks", "Azure ML / TGI / Triton"),
        ("Awaiting", "throughput/latency/quality benchmark, then ARB (deck 09)"),
    ], CX0, 1.95, 6.0, 3.0, col=GOLD)
    d.image(s, "vllm", 9.2, 2.1, h=0.85)
    d.bullets(s, [
        "VRAM planning (D5-19): model params × precision + KV cache × context × batch × concurrency.",
        "Continuous batching & quantisation are quality-validated optimisations (deck 08).",
        "Hosted HF bridges until the self-hosted stack is benchmarked and ratified.",
    ], CX0, 5.2, CW, 1.6, size=14, gap=11)
    d.set_notes(s, "vLLM on AKS GPU is the recommended serving stack, Proposed pending a benchmark and "
                   "ARB sign-off; VRAM/KV-cache planning sizes the GPU SKU and drives the self-hosted cost model.")

    s = d.content_slide("APIM boundary & shared HTTP client", kicker="D5-15 / D5-16")
    d.two_col(s, "APIM — the authZ boundary", [
        "APIM is where authN/authZ happens; the AI only consumes validated claims.",
        "Rate limiting, versioning and policy live at the gateway.",
    ], "Shared HTTP client", [
        "One pooled client: keep-alive, HTTP/2 where useful.",
        "Timeouts, retry, tracing built in.",
        "Never a new connection per request.",
    ])
    d.set_notes(s, "APIM is the security boundary — the AI never authenticates or authorizes itself; "
                   "a single shared, pooled, traced HTTP client for all egress.")

    s = d.content_slide("Five-stage environment model", kicker="D5-14")
    d.pipeline(s, ["DEV", "TEST", "UAT", "STAGE", "PROD"], y=3.0, h=1.0)
    d.text(s, "Superset model (UAT inserted before STAGE) so the Infrastructure doc's namespace/config "
              "examples need no renaming. Endpoint & config resolution is per-stage (deck 02).",
           CX0, 4.4, CW, 1.0, size=14, color=GREY)
    d.set_notes(s, "Five stages DEV→TEST→UAT→STAGE→PROD; each stage resolves its own endpoints/config.")

    s = d.content_slide("Enterprise delivery model", kicker="D5-20 (Accepted) · D5-12 · D5-13")
    d.chip_row(s, [("azuredevops", "Azure DevOps"), ("aks", "Shared AKS"),
                   ("sonarqube", "SonarQube")], y=2.0, size=0.8)
    d.bullets(s, [
        "PFF AI conforms to the Enterprise Application delivery model — no separate infra/CI/CD/deploy stack.",
        "Azure DevOps build.yaml / release.yaml on the shared enterprise AKS platform; same team & resources.",
        "Enterprise SonarQube quality gate. IaC (D5-12) & K8s manifest (D5-13) standards are Accepted.",
    ], CX0, 3.9, CW, 2.2, size=15, gap=13)
    d.set_notes(s, "We do NOT stand up our own platform — enterprise Azure DevOps CI/CD on shared AKS "
                   "with the enterprise SonarQube gate, removing a whole class of cost and burden (deck 08).")

    s = d.content_slide("Scalability, autoscaling & latency", kicker="D5-17 / D5-18")
    d.two_col(s, "Autoscaling", [
        "Signals: CPU, memory, request/concurrent count, queue depth, GPU util, VRAM.",
        "Respects model-provider, enterprise-API, DB, vector and cost limits.",
        "Avoids cold-start churn (min replicas / warm pods).",
    ], "Latency budget", [
        "Each layer owns a slice of the end-to-end budget (deck 08).",
        "p95/p99 targets, not averages.",
        "TTFT separated from total completion time.",
    ])
    d.set_notes(s, "Autoscaling is AI-aware (GPU/VRAM/queue), bounded by downstream limits and cost; "
                   "latency is budgeted per layer and measured at p95/p99.")

    d.adr_index_slides("ADR index — Technology (D5)", adrs_for(5),
                       notes="All 20 technology ADRs. One is Proposed (◆): D5-10 self-hosted vLLM "
                             "serving stack (deck 09). IaC, K8s and the enterprise delivery model are Accepted.")

    d.final_slide("Technology & infrastructure — summary",
                  "Azure-native · SPN-only secrets · GPU-separated AKS · enterprise delivery, no bespoke stack",
                  notes="Azure-native and enterprise-conformant — minimal bespoke infrastructure, strict "
                        "secret handling, GPU cost isolated for planning.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
