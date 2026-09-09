#!/usr/bin/env python3
"""Deck 03 — AI Architecture (D3), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "03-ai-architecture.pptx")


def prompt_stack(d, s):
    layers = [("System", "platform rules, non-negotiable"),
              ("Security", "injection defence, allow/deny"),
              ("Persona", "Adam — versioned, reusable"),
              ("Task", "workflow objective & steps"),
              ("Context", "ERC · RAG · state (budgeted)"),
              ("Tools", "schemas & instructions"),
              ("Output", "structured schema & validation")]
    y = 1.95; h = 0.62; w = 7.3; x = CX0
    for t, sub in layers:
        d.card(s, x, y, w, h)
        d._rect(s, x, y, 0.1, h, BLUE)
        d.text(s, t, x + 0.25, y + 0.06, 2.1, 0.5, size=13.5, color=NAVY, bold=True, font="Cambria")
        d.text(s, sub, x + 2.4, y + 0.09, w - 2.6, 0.5, size=11, color=GREY)
        y += h + 0.1
    d.box(s, "Composed by the\nPrompt Engineering\ncapability —\nevery layer versioned",
          9.5, 1.95, 3.2, 5.0, style="navy", size=13)


def build():
    d = Deck()
    d.title_slide("AI", "Architecture",
                  "Agents · prompts · SLM · RAG · embeddings · refinement  —  D3 (28 ADRs, 3 open)",
                  kicker="Deck 03 · AI architecture",
                  notes="The AI core: how agents reason, how prompts are composed and secured, how the "
                        "SLM is abstracted and made reliable, and how RAG grounds answers. Three ADRs "
                        "are Proposed (embedding model, vector store, refinement loop) — deck 09.")

    d.agenda_slide("What this deck covers", [
        "AI capability taxonomy & agentic style",
        "Agent contract, lifecycle & tool-calling boundary",
        "Intent classification & routing strategy",
        "Clarification, confirmation & transaction-uncertainty",
        "Prompt engineering — layered composition & security",
        "SLM strategy, provider abstraction & model registry",
        "Generation params, structured output, streaming, fallback",
        "RAG — scope, ingestion, retrieval, citation",
        "Embedding model & vector store (Proposed)",
        "Context engineering & the quality-gated refinement loop (Proposed)",
    ])

    s = d.content_slide("AI capability taxonomy & style", kicker="D3-01 / D3-02")
    d.two_col(s, "Capabilities", [
        "Reasoning/orchestration, prompt engineering, RAG, embeddings/vector, SLM inference, guardrails.",
        "Each is a versioned software artifact with its own config & evaluation.",
    ], "Agentic style", [
        "Supervisor + tool-using agents on LangGraph.",
        "Bounded, observable, deterministic-where-possible.",
        "Agents reason and call controlled tools — they never decide business outcomes.",
    ])
    d.set_notes(s, "A clear taxonomy of AI capabilities, each versioned and evaluated; supervised "
                   "tool-using agents, bounded and observable.")

    s = d.content_slide("Agent contract & tool-calling", kicker="D3-03 / D3-04")
    d.two_col(s, "Agent contract & lifecycle", [
        "Typed inputs/outputs; declared tools, prompts, guardrails.",
        "Lifecycle: init → plan → act (tools) → validate → respond.",
        "Versioned and independently evaluable.",
    ], "Tool-calling & validation", [
        "Tools are allow-listed per agent; parameters validated (Pydantic).",
        "Outputs validated before use; failures are typed (ToolError).",
        "No tool result is trusted as authority without enterprise confirmation.",
    ])
    d.set_notes(s, "Agents have explicit contracts and lifecycles; the tool-calling boundary validates "
                   "parameters and outputs and is allow-listed per agent.")

    s = d.content_slide("Intent classification & routing", kicker="D3-05 / D3-06")
    d.two_col(s, "Classification", [
        "Intent classification selects the candidate agent/workflow.",
        "Confidence-aware; ambiguous intent triggers clarification, not a guess.",
    ], "Deterministic vs model-decided", [
        "Prefer deterministic routing where rules suffice.",
        "Model-decided routing only where justified and bounded.",
        "Routing is observable and loop-limited.",
    ])
    d.set_notes(s, "Deterministic routing preferred; model-decided only where necessary, always bounded and observable.")

    s = d.content_slide("Clarify, confirm & handle uncertainty", kicker="D3-07 / D3-08")
    d.bullets(s, [
        "Ambiguous or incomplete requests → Adam asks a clarifying question rather than guessing.",
        "Before any state-changing action → explicit confirmation (HIL).",
        "Transaction-uncertainty policy: on a failed/ambiguous outcome Adam never silently guesses — it states the uncertainty, and reconciliation (deck 02) resolves the true state.",
        "Never celebrate an unconfirmed transaction — 'GOAL' only after the enterprise confirms.",
    ], CX0, 1.95, CW, 4.0, size=16, gap=15)
    d.set_notes(s, "The conversational safety core: clarify, confirm, never fabricate a transaction outcome.")

    s = d.content_slide("Prompt engineering — layered composition", kicker="D3-09 / D3-10")
    prompt_stack(d, s)
    d.set_notes(s, "Prompts are composed from independent, versioned layers. The Adam persona is one "
                   "reusable layer; system & security layers are non-negotiable and cannot be overridden.")

    s = d.content_slide("Prompt storage, versioning & injection defence", kicker="D3-11 / D3-12")
    d.two_col(s, "Storage & promotion", [
        "Git is the canonical prompt source; naming <domain>.<agent>.<task>.<type>.vX.Y.Z.",
        "Immutable versioned bundles; promoted through environments.",
        "No in-place production mutation.",
    ], "Injection defence", [
        "Prompt-injection & jailbreak defence lives in the prompt/security layer.",
        "Untrusted content is quarantined & never treated as instructions.",
        "Reinforced by guardrails at every boundary (deck 06).",
    ])
    d.set_notes(s, "Prompts are versioned software in Git, promoted as immutable bundles; injection "
                   "defence is layered — prompt layer plus guardrails.")

    s = d.content_slide("SLM strategy, abstraction & registry", kicker="D3-13 / D3-14 / D3-15")
    d.pipeline(s, [("Provider\nabstraction", "one interface"), ("HF Inference API", "initial"),
                   ("Self-hosted vLLM", "target (GPU)"), ("Model registry", "approved · versioned")],
               y=2.7, h=1.05)
    d.bullets(s, [
        "Hosted-first (HF) → self-hosted vLLM on AKS GPU target — the serving stack is a Proposed decision (deck 09).",
        "Provider abstraction makes models swappable behind one interface; the registry lists only approved, evaluated models.",
    ], CX0, 4.3, CW, 1.7, size=14, gap=12)
    d.set_notes(s, "SLM access is abstracted so hosted and self-hosted providers are interchangeable; "
                   "only approved, evaluated, observable models are registered.")

    s = d.content_slide("Generation, structured output & streaming", kicker="D3-16 / D3-17 / D3-19")
    d.stat_cards(s, [("Low temperature", "deterministic for enterprise tasks"),
                     ("Structured output", "schema-validated, typed"),
                     ("Streaming", "TTFT ≠ faster backend"),
                     ("Validated", "before it reaches the user")], y=2.1, h=1.9)
    d.bullets(s, [
        "Generation parameters are task-appropriate; enterprise tasks favour determinism.",
        "Outputs are structured and validated; streaming improves perceived latency only.",
    ], CX0, 4.4, CW, 1.7, size=14, gap=12)
    d.set_notes(s, "Temperature/params tuned per task; structured, schema-validated output; streaming is a UX improvement.")

    s = d.content_slide("SLM reliability — fallback & circuit-breaking", kicker="D3-18")
    d.bullets(s, [
        "Fallback models must be approved, compatible, evaluated, configured and observable.",
        "Degradation ladder: retry → approved fallback model → reduced optional processing → controlled stop.",
        "Circuit-breaking protects downstream capacity and cost (deck 08); distinct from the quality-gated refinement loop (D3-28).",
    ], CX0, 1.95, CW, 3.2, size=16, gap=15)
    d.set_notes(s, "Failure-fallback (D3-18) handles provider/model failure — different from the "
                   "refinement loop (D3-28), which is about output quality.")

    s = d.content_slide("RAG — scope & pipeline", kicker="D3-20/21/22/26/27")
    d.pipeline(s, [("Query", "rewrite"), ("Embed", "768-dim"), ("Vector +\nkeyword", "hybrid"),
                   ("Rerank", "when needed"), ("Context", "budgeted"), ("Cite", "ACL-checked")],
               y=2.6, h=1.05)
    d.bullets(s, [
        "RAG is knowledge-only (D3-20) — it never carries authoritative transactional truth.",
        "Ingestion & chunking (D3-21) with a defined trigger mechanism (D3-27); agentic retrieval loop (D3-26).",
        "Every answer is grounded and cited; ACL enforced at retrieval (deck 06).",
    ], CX0, 4.3, CW, 1.8, size=14, gap=11)
    d.set_notes(s, "RAG grounds answers in knowledge only; hybrid retrieval, reranking when needed, "
                   "budgeted context, mandatory ACL-checked citations.")

    s = d.content_slide("Embedding model selection", kicker="D3-23 · PROPOSED",
                        subtitle="Build-default recommendation — ARB sign-off (deck 09)")
    d.kv_panel(s, "Recommendation (build default)", [
        ("Model class", "HF-hosted general-purpose 768-dim (bge-base-en-v1.5 class)"),
        ("Fallback", "1024-dim variant"),
        ("Why provisional", "must pass PFF-FA retrieval eval (Recall@5 ≥ 0.90)"),
        ("Awaiting", "evaluation result, then ARB sign-off"),
    ], CX0, 1.95, 5.9, 4.4, col=GOLD)
    d.bullets(s, [
        "Chosen by a PFF-specific retrieval evaluation, not by reputation.",
        "Dimension affects vector storage cost (deck 08) and recall — not reduced without evaluation.",
        "Re-embedding strategy defined for model/version changes.",
    ], 8.2, 2.1, 4.5, 4.2, size=14, gap=13)
    d.set_notes(s, "Embedding model is Proposed because doc 14 mandates an evaluation-first choice; we "
                   "build against 768-dim; ARB ratifies after Recall@5 ≥ 0.90.")

    s = d.content_slide("Vector store selection", kicker="D3-24 · PROPOSED",
                        subtitle="Build-default recommendation — ARB sign-off (deck 09)")
    d.kv_panel(s, "Recommendation (build default)", [
        ("Store", "Azure AI Search (vector + hybrid)"),
        ("Fallback", "pgvector on Azure Postgres"),
        ("Why", "managed, hybrid retrieval, Azure-native security"),
        ("Awaiting", "ARB sign-off"),
    ], CX0, 1.95, 5.9, 4.4, col=GOLD)
    d.image(s, "aisearch", 9.4, 2.3, h=1.1)
    d.text(s, "Azure AI Search", 8.2, 3.55, 4.5, 0.4, size=15, color=NAVY, bold=True,
           align=PP_ALIGN.CENTER)
    d.text(s, "Cost drivers — tier, replicas/partitions, index size, query volume — are broken down in deck 08.",
           8.2, 4.2, 4.5, 1.2, size=13, color=GREY)
    d.set_notes(s, "Azure AI Search is the recommended vector store — managed, hybrid retrieval, "
                   "Azure security; pgvector is the fallback.")

    s = d.content_slide("Context engineering & budget", kicker="D3-25")
    d.bullets(s, [
        "Context is assembled with an explicit budget: authoritative data first, then relevant RAG, required workflow & authorization context.",
        "Token budget enforced by batch → compress (approved) → retrieve-relevant → continue — never silent truncation of authoritative data.",
        "Context size is both a latency and a cost driver (deck 08).",
    ], CX0, 1.95, CW, 3.4, size=16, gap=15)
    d.set_notes(s, "Context assembly is budgeted and prioritised; authoritative values are protected.")

    s = d.content_slide("Quality-gated refinement loop", kicker="D3-28 · PROPOSED",
                        subtitle="Runtime quality control — ARB sign-off (deck 09)")
    d.pipeline(s, [("Generate", "candidate output"), ("Score", "deterministic"),
                   ("Below\nthreshold?", "regenerate"), ("Model ladder", "bounded"),
                   ("Accept", "or strict-block")], y=2.5, h=1.05)
    d.bullets(s, [
        "A deterministic controller scores each output; below a configured threshold it regenerates and/or escalates up a model ladder, bounded.",
        "Strict mode for governance-critical task classes; opt-in per task class (config/base/refinement.yaml).",
        "Distinct from failure-fallback (D3-18) and offline eval gates (D7-13). Awaiting ARB + Phase 20 latency/cost benchmark.",
    ], CX0, 4.2, CW, 2.0, size=13.5, gap=10)
    d.set_notes(s, "Runtime quality control: score → regenerate/escalate, bounded, strict mode for "
                   "governance-critical classes; it trades cost/latency for quality — hence ARB endorsement.")

    d.adr_index_slides("ADR index — AI (D3)", adrs_for(3),
                       notes="All 28 AI-architecture ADRs. Three are Proposed (◆): D3-23 embedding "
                             "model, D3-24 vector store, D3-28 refinement loop — all in deck 09.")

    d.final_slide("AI architecture — summary",
                  "Bounded agents · layered secure prompts · abstracted reliable SLM · grounded cited RAG · quality-gated",
                  notes="The AI is powerful but bounded — grounded, cited, validated, and never the "
                        "source of business authority.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
