#!/usr/bin/env python3
"""Deck 03 — AI Architecture (D3)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "03-ai-architecture.pptx")


def prompt_stack(d, s):
    layers = [("System", "platform rules, non-negotiable", CYAN),
              ("Security", "injection defence, allow/deny", PINK),
              ("Persona", "Adam — versioned, reusable", VIOLET),
              ("Task", "workflow objective & steps", YELLOW),
              ("Context", "ERC · RAG · state (budgeted)", GREEN),
              ("Tools", "schemas & instructions", BLUE),
              ("Output", "structured schema & validation", PURPLE)]
    y = 1.95; h = 0.64; w = 7.4; x = 0.9
    for t, sub, col in layers:
        d.box(s, "", x, y, w, h, fill=PANEL2, line=col, line_w=1.1)
        d.text(s, t, x + 0.2, y + 0.06, 2.2, 0.5, size=14, color=col, bold=True)
        d.text(s, sub, x + 2.4, y + 0.09, w - 2.6, 0.5, size=11, color=GREY)
        y += h + 0.11
    d.box(s, "Composed\nby the\nPrompt\nEngineering\ncapability\n— every layer\nversioned",
          8.6, 1.95, 3.7, 5.05, fill=PANEL, line=YELLOW, textcolor=WHITE, size=13)


def rag_pipeline(d, s):
    pipeline(d, s, [("Query", "rewrite"), ("Embed", "768-dim"), ("Vector +\nkeyword", "hybrid"),
                    ("Rerank", "when needed"), ("Context", "budgeted"), ("Cite", "ACL-checked")],
             y=2.5, h=1.0, colors=[CYAN, BLUE, GREEN, PURPLE, YELLOW, PINK])
    d.bullets(s, [
        "RAG is knowledge-only (D3-20) — it never carries authoritative transactional truth.",
        "Ingestion & chunking (D3-21) with a defined trigger mechanism (D3-27); agentic retrieval loop (D3-26).",
        "Every answer is grounded and cited; ACL enforced at retrieval (deck 06).",
    ], 0.9, 4.2, 11.5, 1.9, size=14, gap=11)


def build():
    d = Deck()
    d.title_slide("03 · AI Architecture",
                  "Agents · prompts · SLM · RAG · embeddings · refinement  (D3, 28 ADRs — 3 open)",
                  notes="The AI core: how agents reason, how prompts are composed and secured, how "
                        "the SLM is abstracted and made reliable, and how RAG grounds answers. "
                        "28 ADRs; three are Proposed and go to deck 09 (embedding model, vector store, refinement loop).")

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

    s = d.content_slide("AI capability taxonomy & style", "D3-01 / D3-02")
    two_col(d, s,
            "Capabilities", [
                "Reasoning/orchestration, prompt engineering, RAG, embeddings/vector, SLM inference, guardrails.",
                "Each is a versioned software artifact with its own config & evaluation.",
            ],
            "Agentic style", [
                "Supervisor + tool-using agents on LangGraph.",
                "Bounded, observable, deterministic-where-possible.",
                "Agents reason and call controlled tools — they never decide business outcomes.",
            ])
    s.notes_slide.notes_text_frame.text = ("A clear taxonomy of AI capabilities, each versioned and "
        "evaluated. The style is supervised tool-using agents, bounded and observable.")

    s = d.content_slide("Agent contract & tool-calling", "D3-03 / D3-04")
    two_col(d, s,
            "Agent contract & lifecycle", [
                "Typed inputs/outputs; declared tools, prompts, guardrails.",
                "Lifecycle: init → plan → act (tools) → validate → respond.",
                "Versioned and independently evaluable.",
            ],
            "Tool-calling & validation", [
                "Tools are allow-listed per agent; parameters validated (Pydantic).",
                "Outputs validated before use; failures are typed (ToolError).",
                "No tool result is trusted as authority without enterprise confirmation.",
            ])
    s.notes_slide.notes_text_frame.text = ("Agents have explicit contracts and lifecycles. The "
        "tool-calling boundary validates parameters and outputs and is allow-listed per agent.")

    s = d.content_slide("Intent classification & routing", "D3-05 / D3-06")
    two_col(d, s,
            "Classification", [
                "Intent classification selects the candidate agent/workflow.",
                "Confidence-aware; ambiguous intent triggers clarification, not a guess.",
            ],
            "Deterministic vs model-decided", [
                "Prefer deterministic routing where rules suffice.",
                "Model-decided routing only where justified and bounded.",
                "Routing is observable and loop-limited.",
            ])
    s.notes_slide.notes_text_frame.text = ("Deterministic routing is preferred; model-decided "
        "routing is used only where necessary and is always bounded and observable.")

    s = d.content_slide("Clarify, confirm & handle uncertainty", "D3-07 / D3-08")
    d.bullets(s, [
        "Ambiguous or incomplete requests → Adam asks a clarifying question rather than guessing.",
        "Before any state-changing action → explicit confirmation (HIL).",
        "Transaction-uncertainty policy: on a failed/ambiguous outcome Adam never silently guesses — it states the uncertainty, and reconciliation (deck 02) resolves the true state.",
        "Never celebrate an unconfirmed transaction — 'GOAL' only after the enterprise confirms.",
    ], 0.9, 2.0, 11.5, 4.0, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("This is the conversational safety core: clarify, confirm, "
        "and never fabricate a transaction outcome. Ties directly to the Golden Rule.")

    s = d.content_slide("Prompt engineering — layered composition", "D3-09 / D3-10")
    prompt_stack(d, s)
    s.notes_slide.notes_text_frame.text = ("Prompts are composed from independent, versioned layers. "
        "The Adam persona is one reusable layer (D3-10); it never contains the whole workflow. Security "
        "and system layers are non-negotiable and cannot be overridden by lower layers.")

    s = d.content_slide("Prompt storage, versioning & injection defence", "D3-11 / D3-12")
    two_col(d, s,
            "Storage & promotion", [
                "Git is the canonical prompt source; naming <domain>.<agent>.<task>.<type>.vX.Y.Z.",
                "Immutable versioned bundles; promoted through environments.",
                "No in-place production mutation.",
            ],
            "Injection defence", [
                "Prompt-injection & jailbreak defence lives in the prompt/security layer.",
                "Untrusted content is quarantined & never treated as instructions.",
                "Reinforced by guardrails at every boundary (deck 06).",
            ])
    s.notes_slide.notes_text_frame.text = ("Prompts are versioned software in Git and promoted as "
        "immutable bundles. Injection defence is layered — prompt layer plus guardrails.")

    s = d.content_slide("SLM strategy, abstraction & registry", "D3-13 / D3-14 / D3-15")
    pipeline(d, s, [("Provider\nabstraction", "one interface"), ("HF Inference API", "initial"),
                    ("Self-hosted vLLM", "target (GPU)"), ("Model registry", "approved · versioned")],
             y=2.6, h=1.0, colors=[CYAN, BLUE, VIOLET, GREEN])
    d.bullets(s, [
        "Hosted-first (HF) → self-hosted vLLM on AKS GPU target — the serving stack is a Proposed decision (deck 09).",
        "Provider abstraction means models are swappable behind one interface; the registry lists only approved, evaluated models.",
    ], 0.9, 4.2, 11.5, 1.8, size=14, gap=12)
    s.notes_slide.notes_text_frame.text = ("SLM access is abstracted so hosted and self-hosted "
        "providers are interchangeable. Only approved, evaluated, observable models are registered.")

    s = d.content_slide("Generation, structured output & streaming", "D3-16 / D3-17 / D3-19")
    stat_cards(d, s, [
        ("Low temperature", "deterministic for enterprise tasks", CYAN),
        ("Structured output", "schema-validated, typed", GREEN),
        ("Streaming", "TTFT ≠ faster backend", YELLOW),
        ("Validated", "before it reaches the user", PINK),
    ], y=2.1, h=2.0)
    d.bullets(s, [
        "Generation parameters are task-appropriate; enterprise tasks favour determinism.",
        "Outputs are structured and validated; streaming improves perceived latency only.",
    ], 0.9, 4.5, 11.5, 1.7, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = ("Temperature and generation params are tuned per task; "
        "structured, schema-validated output; streaming is a UX improvement, not a backend speed-up.")

    s = d.content_slide("SLM reliability — fallback & circuit-breaking", "D3-18")
    d.bullets(s, [
        "Fallback models must be approved, compatible, evaluated, configured and observable.",
        "Degradation ladder: retry → approved fallback model → reduced optional processing → controlled stop.",
        "Circuit-breaking protects downstream capacity and cost (deck 08); distinct from the quality-gated refinement loop (D3-28).",
    ], 0.9, 2.0, 11.5, 3.2, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Failure-fallback (D3-18) handles provider/model failure. "
        "It is different from the refinement loop (D3-28), which is about output quality, not failure.")

    s = d.content_slide("RAG — scope & pipeline", "D3-20 / D3-21 / D3-22 / D3-26 / D3-27")
    rag_pipeline(d, s)
    s.notes_slide.notes_text_frame.text = ("RAG grounds answers in knowledge only — never "
        "authoritative transactional data. Hybrid retrieval, reranking when needed, budgeted context, "
        "and mandatory ACL-checked citations.")

    s = d.content_slide("Embedding model selection", "D3-23 · PROPOSED — ARB sign-off (deck 09)")
    kv_panel(d, s, "Recommendation (build default)", [
        ("Model class", "HF-hosted general-purpose 768-dim (bge-base-en-v1.5 class)"),
        ("Fallback", "1024-dim variant"),
        ("Why provisional", "must pass PFF-FA retrieval eval (Recall@5 ≥ 0.90)"),
        ("Awaiting", "evaluation result, then ARB sign-off"),
    ], 0.9, 1.95, 6.0, 4.4, col=YELLOW)
    d.bullets(s, [
        "Chosen by a PFF-specific retrieval evaluation, not by reputation.",
        "Dimension affects vector storage cost (deck 08) and recall — not reduced without evaluation.",
        "Re-embedding strategy defined for model/version changes.",
    ], 7.1, 2.1, 5.3, 4.2, size=14, gap=13)
    s.notes_slide.notes_text_frame.text = ("Embedding model is Proposed because doc 14 mandates an "
        "evaluation-first choice. We build against the 768-dim recommendation; ARB ratifies after the "
        "Recall@5 ≥ 0.90 evaluation.")

    s = d.content_slide("Vector store selection", "D3-24 · PROPOSED — ARB sign-off (deck 09)")
    kv_panel(d, s, "Recommendation (build default)", [
        ("Store", "Azure AI Search (vector + hybrid)"),
        ("Fallback", "pgvector on Azure Postgres"),
        ("Why", "managed, hybrid retrieval, Azure-native security"),
        ("Awaiting", "ARB sign-off"),
    ], 0.9, 1.95, 6.0, 4.4, col=YELLOW)
    d.image(s, "aisearch", 8.6, 2.3, h=1.2)
    d.text(s, "Azure AI Search", 7.6, 3.65, 4.5, 0.4, size=15, color=GREY, align=PP_ALIGN.CENTER)
    d.text(s, "Cost drivers — tier, replicas/partitions, index size, query volume — are broken down in deck 08.",
           7.1, 4.6, 5.3, 1.2, size=14, color=GREY)
    s.notes_slide.notes_text_frame.text = ("Azure AI Search is the recommended vector store — managed, "
        "supports hybrid retrieval, integrates with Azure security. pgvector is the fallback. Cost in deck 08.")

    s = d.content_slide("Context engineering & budget", "D3-25")
    d.bullets(s, [
        "Context is assembled with an explicit budget: authoritative data first, then relevant RAG, required workflow & authorization context.",
        "Token budget enforced by batch → compress (approved) → retrieve-relevant → continue — never silent truncation of authoritative data.",
        "Context size is both a latency and a cost driver (deck 08).",
    ], 0.9, 2.0, 11.5, 3.4, size=16, gap=15)
    s.notes_slide.notes_text_frame.text = ("Context assembly is budgeted and prioritised. Authoritative "
        "values are protected; compression only touches non-authoritative explanatory text.")

    s = d.content_slide("Quality-gated refinement loop", "D3-28 · PROPOSED — ARB sign-off (deck 09)")
    pipeline(d, s, [("Generate", "candidate output"), ("Score", "deterministic controller"),
                    ("Below threshold?", "regenerate / escalate"), ("Model ladder", "bounded"),
                    ("Accept", "or strict-mode block")], y=2.5, h=1.0,
             colors=[CYAN, YELLOW, PINK, VIOLET, GREEN])
    d.bullets(s, [
        "A deterministic controller scores each output; below a configured threshold it regenerates and/or escalates up a model ladder, bounded.",
        "Strict mode for governance-critical task classes; opt-in per task class (config/base/refinement.yaml).",
        "Distinct from failure-fallback (D3-18) and offline eval gates (D7-13). Awaiting ARB + Phase 20 latency/cost benchmark.",
    ], 0.9, 4.1, 11.5, 2.1, size=14, gap=11)
    s.notes_slide.notes_text_frame.text = ("Runtime quality control: score → regenerate/escalate, "
        "bounded, with strict mode for governance-critical classes. Proposed; ratified after ARB and a "
        "Phase 20 latency/cost benchmark. It trades cost/latency for quality — hence ARB endorsement.")

    adr_index_slides(d, "ADR index — AI (D3)", adrs_for(3),
                     notes="All 28 AI-architecture ADRs. Three are Proposed (◆): D3-23 embedding "
                           "model, D3-24 vector store, D3-28 refinement loop — all in deck 09.")

    d.final_slide("AI architecture — summary",
                  "Bounded agents · layered secure prompts · abstracted reliable SLM · grounded cited RAG · quality-gated",
                  notes="Takeaway: the AI is powerful but bounded — grounded, cited, validated, and "
                        "never the source of business authority.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
