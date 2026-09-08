#!/usr/bin/env python3
"""Deck 05 — Technology & Infrastructure (D5)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "05-technology-infrastructure.pptx")


def svc(d, s, logo, label, x, y, w=1.85, h=0.82, col=CYAN):
    d.box(s, "", x, y, w, h, fill=PANEL2, line=col, line_w=1.0)
    d.image(s, logo, x + 0.12, y + (h - 0.5) / 2, h=0.5)
    d.text(s, label, x + 0.72, y + 0.12, w - 0.8, h - 0.2, size=10.5, color=WHITE,
           bold=True, anchor=1)


def topology(d, s):
    # tenancy boundary
    d.box(s, "", 0.45, 1.55, 12.45, 4.75, fill=PANEL, line=VIOLET, line_w=1.1)
    d.text(s, "AZURE TENANCY · UK South", 0.62, 1.6, 6, 0.3, size=10, color=VIOLET, bold=True)

    d.box(s, "Chat UI", 0.65, 3.2, 1.15, 0.7, fill=PANEL2, line=CYAN, size=11)
    svc(d, s, "apim", "APIM\nauthN/Z", 1.95, 3.15, 1.4, 0.85, col=BLUE)

    # AKS cluster
    d.box(s, "", 3.55, 1.95, 4.35, 4.05, fill=PANEL2, line=CYAN, line_w=1.1)
    d.image(s, "aks", 3.7, 2.05, h=0.5)
    d.text(s, "AKS cluster", 4.35, 2.1, 3.3, 0.4, size=13, color=CYAN, bold=True)
    d.box(s, "System node pool\nFastAPI · LangGraph · Agent Harness",
          3.75, 2.75, 3.95, 1.35, fill=PANEL, line=BLUE, size=11)
    d.box(s, "GPU node pool\nvLLM — self-hosted SLM (target)",
          3.75, 4.3, 3.95, 1.35, fill=PANEL, line=VIOLET, size=11)

    # data services column
    svc(d, s, "aisearch", "Azure AI Search", 8.25, 2.05, 2.05, 0.8, col=GREEN)
    svc(d, s, "redis", "Managed Redis", 8.25, 2.95, 2.05, 0.8, col=PINK)
    svc(d, s, "servicebus", "Service Bus", 8.25, 3.85, 2.05, 0.8, col=BLUE)
    svc(d, s, "blob", "Blob Storage", 8.25, 4.75, 2.05, 0.8, col=CYAN)

    # platform column
    svc(d, s, "keyvault", "Key Vault (SPN)", 10.55, 2.05, 2.15, 0.8, col=YELLOW)
    svc(d, s, "acr", "ACR", 10.55, 2.95, 2.15, 0.8, col=CYAN)
    svc(d, s, "monitor", "Monitor / App Ins.", 10.55, 3.85, 2.15, 0.8, col=BLUE)
    svc(d, s, "langfuse", "Langfuse", 10.55, 4.75, 2.15, 0.8, col=PINK)

    # external SLM (outside tenancy)
    d.box(s, "", 3.55, 6.55, 5.0, 0.6, fill=PANEL, line=PINK, line_w=1.1)
    d.image(s, "huggingface", 3.7, 6.62, h=0.44)
    d.text(s, "External SLM (Hugging Face) — masked/tokenised payloads only, fail-closed",
           5.6, 6.62, 6.9, 0.5, size=10, color=PINK, bold=True, anchor=1)

    # arrows
    d.connector(s, 1.8, 3.55, 1.95, 3.55, color=GREY, width=1.3)
    d.connector(s, 3.35, 3.55, 3.55, 3.55, color=GREY, width=1.3)
    d.connector(s, 7.9, 3.4, 8.25, 2.9, color=GREY, width=1.2)
    d.connector(s, 7.9, 3.7, 8.25, 3.7, color=GREY, width=1.2)
    d.connector(s, 5.7, 5.65, 5.7, 6.55, color=PINK, width=1.4)


def build():
    d = Deck()
    d.title_slide("05 · Technology & Infrastructure",
                  "Azure · AKS · APIM · Key Vault · vLLM/GPU · enterprise delivery  (D5, 20 ADRs — 1 open)",
                  notes="The concrete technology and Azure infrastructure. 20 ADRs; one is Proposed "
                        "(the self-hosted vLLM serving stack, deck 09). IaC, K8s and the delivery model "
                        "are Accepted — we conform to the enterprise application model.")

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

    s = d.content_slide("Target infrastructure topology", "on Microsoft Azure — UK South")
    topology(d, s)
    s.notes_slide.notes_text_frame.text = ("The whole platform runs in one Azure tenancy. APIM is the "
        "authZ boundary in front of the AKS cluster (system node pool for the app; GPU node pool for "
        "self-hosted vLLM). Data/platform services — AI Search, Managed Redis, Service Bus, Blob, Key "
        "Vault, ACR, Monitor/App Insights, Langfuse — are all Azure-native. The only egress is to the "
        "external SLM, and only masked/tokenised payloads cross that boundary (deck 06). Every service "
        "here has a cost line in deck 08.")

    s = d.content_slide("Engineering stack", "D5-01 / D5-02 / D5-03 / D5-04 / D5-05")
    d.chip_row(s, [("python", "Python"), ("fastapi", "FastAPI"), ("pydantic", "Pydantic"),
                   ("ruff", "Ruff")], y=2.0, size=0.85)
    d.bullets(s, [
        "Python + FastAPI; a single project type checker (mypy or pyright) chosen at Phase 0.",
        "Pydantic validates every boundary (API, tool, config, event, ERC, SLM); TypedDict for graph state.",
        "Dependencies pinned with a lock file; Ruff for lint/format; conventional commits & semantic versioning.",
    ], 0.9, 4.0, 11.5, 2.2, size=15, gap=13)
    s.notes_slide.notes_text_frame.text = ("The engineering stack is deliberately conventional and "
        "strict: typed boundaries, pinned deps, one linter, one type checker.")

    s = d.content_slide("Configuration & release manifest", "D5-06")
    d.bullets(s, [
        "Config precedence: Base → Environment → Deployment override → Secret reference.",
        "Schema-validated & fail-fast: invalid mandatory config ⇒ the app never becomes READY.",
        "Immutable release manifest with a configuration_hash (SHA-256) for drift detection.",
        "Prompts, models, agents, workflows, RAG indexes, guardrails are all versioned artifacts in the bundle.",
    ], 0.9, 2.0, 11.5, 3.8, size=16, gap=14)
    s.notes_slide.notes_text_frame.text = ("Configuration is layered, schema-validated and fail-fast. "
        "A release is an immutable, hashed manifest — enabling drift detection and safe promotion.")

    s = d.content_slide("Secret management — Key Vault, SPN-only", "D5-07 / D5-20")
    d.image(s, "keyvault", 0.95, 2.1, h=1.2)
    kv_panel(d, s, "The only path to the vault", [
        ("Credential", "enterprise service principal (MI-SPN): tenant + client id + secret"),
        ("No alternatives", "no DefaultAzureCredential, CLI, interactive, or bare MI"),
        ("Injection", "Azure DevOps variable group → workload env"),
        ("Resolution", "every *_secret_ref resolved from Key Vault; fail-closed in deployed envs"),
    ], 3.3, 1.95, 9.0, 3.5, col=YELLOW)
    d.text(s, "Local dev/test may use process-env; deployed environments are SPN-backed and fail-closed.",
           3.3, 5.6, 9.0, 0.5, size=13, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Key Vault is reached only via the enterprise SPN — no "
        "other credential method is permitted. Secrets are never inline; every *_secret_ref maps to a "
        "vault secret (underscores → hyphens). Deployed environments fail closed.")

    s = d.content_slide("Compute — AKS, containers, GPU", "D5-08 / D5-09 / D5-11")
    two_col(d, s,
            "Cluster & images", [
                "Azure / AKS is the compute platform.",
                "Containerised workloads; images in ACR.",
                "System node pool runs the app runtime.",
            ],
            "GPU & workload separation", [
                "Dedicated GPU node pool for self-hosted SLM.",
                "AI workloads separated from app workloads (D5-11).",
                "GPU is the dominant cost lever — deck 08.",
            ])
    s.notes_slide.notes_text_frame.text = ("AKS with separated system and GPU node pools; images from "
        "ACR. Workload separation isolates GPU cost and scaling from the app tier.")

    s = d.content_slide("Self-hosted SLM serving & capacity", "D5-10 (PROPOSED) / D5-19")
    kv_panel(d, s, "Serving stack — recommendation", [
        ("Stack", "vLLM on AKS GPU"),
        ("Fallbacks", "Azure ML / TGI / Triton"),
        ("Awaiting", "throughput/latency/quality benchmark, then ARB (deck 09)"),
    ], 0.9, 1.95, 6.0, 3.0, col=YELLOW)
    d.image(s, "vllm", 8.9, 2.1, h=0.9)
    d.bullets(s, [
        "VRAM planning (D5-19): model params × precision + KV cache × context × batch × concurrency.",
        "Continuous batching & quantisation are quality-validated optimisations (deck 08).",
        "Hosted HF bridges until the self-hosted stack is benchmarked and ratified.",
    ], 0.9, 5.2, 11.5, 1.7, size=14, gap=11)
    s.notes_slide.notes_text_frame.text = ("vLLM on AKS GPU is the recommended serving stack, Proposed "
        "pending a benchmark and ARB sign-off. VRAM/KV-cache capacity planning (D5-19) sizes the GPU SKU "
        "and drives the self-hosted cost model in deck 08.")

    s = d.content_slide("APIM boundary & shared HTTP client", "D5-15 / D5-16")
    two_col(d, s,
            "APIM — the authZ boundary", [
                "APIM is where authN/authZ happens; the AI only consumes validated claims.",
                "Rate limiting, versioning and policy live at the gateway.",
            ],
            "Shared HTTP client", [
                "One pooled client: keep-alive, HTTP/2 where useful.",
                "Timeouts, retry, tracing built in.",
                "Never a new connection per request.",
            ])
    s.notes_slide.notes_text_frame.text = ("APIM is the security boundary — the AI never authenticates "
        "or authorizes itself. A single shared, pooled, traced HTTP client is the standard for all egress.")

    s = d.content_slide("Five-stage environment model", "D5-14")
    pipeline(d, s, ["DEV", "TEST", "UAT", "STAGE", "PROD"], y=3.0, h=1.0,
             colors=[CYAN, BLUE, PURPLE, YELLOW, GREEN])
    d.text(s, "Superset model (UAT inserted before STAGE) so the Infrastructure doc's namespace/config "
              "examples need no renaming. Endpoint & config resolution is per-stage (deck 02).",
           0.9, 4.4, 11.5, 1.0, size=14, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Five stages DEV→TEST→UAT→STAGE→PROD. We adopt the superset "
        "so nothing from the infrastructure doc needs renaming; each stage resolves its own endpoints/config.")

    s = d.content_slide("Enterprise delivery model", "D5-20 (Accepted) · D5-12 · D5-13")
    d.chip_row(s, [("azuredevops", "Azure DevOps"), ("aks", "Shared AKS"),
                   ("sonarqube", "SonarQube")], y=2.0, size=0.85)
    d.bullets(s, [
        "PFF AI conforms to the Enterprise Application delivery model — no separate infra/CI/CD/deploy stack.",
        "Azure DevOps build.yaml / release.yaml on the shared enterprise AKS platform; same team & resources.",
        "Enterprise SonarQube quality gate. IaC (D5-12) & K8s manifest (D5-13) standards are Accepted.",
    ], 0.9, 4.0, 11.5, 2.2, size=15, gap=13)
    s.notes_slide.notes_text_frame.text = ("A key decision: we do NOT stand up our own platform. We "
        "use the enterprise Azure DevOps CI/CD on shared AKS with the enterprise SonarQube gate. This "
        "removes a whole class of cost and operational burden (deck 08).")

    s = d.content_slide("Scalability, autoscaling & latency", "D5-17 / D5-18")
    two_col(d, s,
            "Autoscaling", [
                "Signals: CPU, memory, request/concurrent count, queue depth, GPU util, VRAM.",
                "Respects model-provider, enterprise-API, DB, vector and cost limits.",
                "Avoids cold-start churn (min replicas / warm pods).",
            ],
            "Latency budget", [
                "Each layer owns a slice of the end-to-end budget (deck 08).",
                "p95/p99 targets, not averages.",
                "TTFT separated from total completion time.",
            ])
    s.notes_slide.notes_text_frame.text = ("Autoscaling is AI-aware (GPU/VRAM/queue), not just CPU, and "
        "is bounded by downstream limits and cost. Latency is budgeted per layer and measured at p95/p99.")

    adr_index_slides(d, "ADR index — Technology (D5)", adrs_for(5),
                     notes="All 20 technology ADRs. One is Proposed (◆): D5-10 self-hosted vLLM serving "
                           "stack (deck 09). IaC, K8s and the enterprise delivery model are Accepted.")

    d.final_slide("Technology & infrastructure — summary",
                  "Azure-native · SPN-only secrets · GPU-separated AKS · enterprise delivery, no bespoke stack",
                  notes="Takeaway: Azure-native and enterprise-conformant — minimal bespoke infrastructure, "
                        "strict secret handling, and GPU cost isolated for planning.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
