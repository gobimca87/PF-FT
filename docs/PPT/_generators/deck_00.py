#!/usr/bin/env python3
"""Deck 00 — PFF AI Technical ARB: Executive & whole-system overview."""
import os
from orion import (Deck, PP_ALIGN, MSO_ANCHOR, MSO_SHAPE,
                   WHITE, GREY, MUTED, CYAN, BLUE, PURPLE, PINK, VIOLET, YELLOW, GREEN,
                   PANEL, PANEL2)

OUT = os.path.join(os.path.dirname(__file__), "..", "00-overview.pptx")
DATE = "September 2026"


def master_diagram(d, s):
    # zone container for the AI runtime
    d.box(s, "", 0.5, 3.05, 12.33, 2.55, fill=PANEL, line=VIOLET, line_w=1.0)
    d.text(s, "AI RUNTIME  ·  single LangGraph process  ·  agents = logical capabilities",
           0.7, 3.12, 8.0, 0.3, size=10, color=VIOLET, bold=True)
    d.text(s, "Guardrails at every boundary (input · context · prompt · tool · model · output)",
           4.7, 3.12, 7.9, 0.3, size=10, color=PINK, bold=True, align=PP_ALIGN.RIGHT)

    # Band A — request path
    bandA = [("Chat UI", CYAN), ("APIM\nauthN / authZ", BLUE),
             ("FastAPI\nthin API", CYAN), ("Supervisor\nintent routing", YELLOW),
             ("LangGraph\norchestration", GREEN)]
    x = 0.6; w = 2.15; gap = 0.34; y = 1.85; h = 0.72
    centers = []
    for i, (label, col) in enumerate(bandA):
        d.box(s, label, x, y, w, h, fill=PANEL2, line=col, textcolor=WHITE, size=12)
        centers.append((x + w/2, x, x + w))
        if i > 0:
            d.connector(s, prev_r, y + h/2, x, y + h/2, color=GREY, width=1.5)
        prev_r = x + w
        x += w + gap
    # LangGraph down into runtime
    d.connector(s, centers[-1][0], y + h, centers[-1][0], 3.05, color=GREEN, width=1.75)

    # Inside runtime: Agents + capability row
    d.box(s, "Agents\n(AffiliationAgent first)", 0.75, 3.55, 2.4, 0.95,
          fill=PANEL2, line=YELLOW, size=12)
    caps = [("ERC\nenterprise context", CYAN), ("Tools / MCP", BLUE),
            ("RAG\nknowledge", GREEN), ("Memory / Cache\nRedis", PINK),
            ("SLM\nHF → vLLM", VIOLET)]
    cx = 3.45; cw = 1.78; cgap = 0.12; cy = 3.9; ch = 0.95
    for label, col in caps:
        d.box(s, label, cx, cy, cw, ch, fill=PANEL2, line=col, size=11)
        cx += cw + cgap
    d.connector(s, 3.15, 4.02, 3.45, 4.02, color=YELLOW, width=1.5)

    # Band C — system of record + response
    y2 = 5.05
    d.box(s, "Enterprise APIs / Events  —  PFF System of Record (decides & executes)",
          0.75, y2, 7.4, 0.42, fill=PANEL2, line=BLUE, size=11)
    d.box(s, "Output\nGuardrail", 8.35, y2 - 0.02, 1.7, 0.46, fill=PANEL2, line=PINK, size=11)
    d.box(s, "Response", 10.25, y2 - 0.02, 2.05, 0.46, fill=PANEL2, line=CYAN, size=11)
    d.connector(s, 4.4, 4.85, 4.4, y2, color=BLUE, width=1.5)
    d.connector(s, 8.15, y2 + 0.2, 8.35, y2 + 0.2, color=GREY, width=1.4)
    d.connector(s, 10.05, y2 + 0.2, 10.25, y2 + 0.2, color=GREY, width=1.4)

    # precedence footnote
    d.text(s, "Authoritative-truth precedence:  Enterprise API / Event  ›  ERC  ›  Cache  ›  RAG  ›  SLM output",
           0.5, 5.75, 12.33, 0.3, size=11, color=YELLOW, bold=True, align=PP_ALIGN.CENTER)


def precedence_diagram(d, s):
    steps = [("Enterprise API / Event", "System of record — decides & executes", GREEN),
             ("ERC", "Enterprise Runtime Context — validated, provenanced", CYAN),
             ("Cache", "Authorization-aware, freshness-bounded", BLUE),
             ("RAG", "Retrieved knowledge — cited, ACL-enforced", PURPLE),
             ("SLM output", "Language only — never a source of authority", PINK)]
    y = 1.85; h = 0.82; w = 11.4; x = 0.95
    for i, (t, sub, col) in enumerate(steps):
        d.box(s, "", x, y, 0.16, h, fill=col, line=None)
        d.box(s, f"{i+1}", x + 0.28, y + 0.13, 0.56, 0.56, fill=PANEL2, line=col,
              textcolor=col, size=18, shape=MSO_SHAPE.OVAL)
        d.text(s, t, x + 1.05, y + 0.08, 4.5, 0.4, size=17, color=WHITE, bold=True)
        d.text(s, sub, x + 1.05, y + 0.44, 9.8, 0.35, size=12, color=GREY)
        if i < len(steps) - 1:
            d.text(s, "▼  higher source wins on conflict — always",
                   x + 1.05, y + h - 0.02, 8.0, 0.28, size=9, color=MUTED)
        y += h + 0.14


def build():
    d = Deck()

    d.title_slide(
        "PFF AI — Adam AI Platform",
        f"Technical Architecture  ·  Architecture Review Board  ·  {DATE}",
        notes="Welcome. This is the technical walkthrough of the PFF-FA Enterprise Agentic AI "
              "platform — Adam AI — for ARB. This overview deck frames the whole system; nine "
              "further decks go deep by domain (business, application, AI, information, technology, "
              "security, operations, cost, and the open decisions we need you to sign off).")

    d.agenda_slide("The presentation suite — 10 decks", [
        "00  Overview (this deck) — whole-system technical picture",
        "01  Business Architecture & Value — D0 / D1 / D8",
        "02  Application & Orchestration — D2",
        "03  AI Architecture — D3 (RAG, SLM, prompts, guardrails)",
        "04  Information, Context & Data — D4 (ERC, memory, cache)",
        "05  Technology & Infrastructure — D5 (Azure, AKS, APIM)",
        "06  Security & Governance — D6",
        "07  Operations, Observability & Quality — D7",
        "08  Cost & FinOps — per-technology cost model",
        "09  Open Decisions & ARB sign-off asks",
    ], notes="Each deck is short on the slide and deep in the speaker notes so the discussion "
             "stays live. All 145 ADRs and 29 specification documents are covered across the suite.")

    s = d.content_slide("What we are building", "Adam AI — a conversational orchestration layer over PFF")
    d.bullets(s, [
        "PFF is the FA's county/club administration platform — affiliation, registration, insurance, discipline, officials, county cups, payments; integrates with WGS (the FA's national database).",
        "Adam AI interprets requests, gathers enterprise context, reasons, calls controlled tools, and communicates results — it does not replace PFF's business logic or authority.",
        "First end-to-end workflow delivered: Club Affiliation.",
        "Persona: a workflow-first enterprise assistant with a natural football-commentary tone.",
    ], 0.9, 2.0, 11.5, 4.5, size=17, gap=14)
    d.notes_helper = None
    s.notes_slide.notes_text_frame.text = (
        "Key message: this is an orchestration layer, not a rewrite. PFF remains the system of "
        "record. Adam adds interpretation, context-gathering, reasoning, controlled tool-calling "
        "and communication. WGS is the national football database we integrate with.")

    s = d.content_slide("The Golden Rule — the binding constraint")
    d.box(s, "Enterprise systems DECIDE and EXECUTE.\nThe AI platform INTERPRETS, ORCHESTRATES,\nCONTEXTUALISES, EXPLAINS and COMMUNICATES.",
          1.4, 2.05, 10.5, 2.0, fill=PANEL, line=YELLOW, textcolor=WHITE, size=22, bold=True)
    d.bullets(s, [
        "The AI never authenticates/authorizes, re-implements business rules, or writes to the enterprise DB.",
        "A model output never becomes an authorization decision.",
        "Raw enterprise/personal data is never exposed to an external SLM (masked/tokenised, fail-closed).",
    ], 1.4, 4.35, 10.5, 2.2, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = (
        "This rule is repeated in every spec doc and is the single most important architectural "
        "constraint. Everything downstream — guardrails, ERC, truth precedence, masking — enforces it.")

    s = d.content_slide("Authoritative-truth precedence", "Higher source always wins on conflict")
    precedence_diagram(d, s)
    s.notes_slide.notes_text_frame.text = (
        "When two sources disagree, the higher one wins — no exceptions. The SLM generates language "
        "but is the lowest-trust source; it never overrides enterprise truth, ERC, cache or RAG.")

    s = d.content_slide("End-to-end platform architecture")
    master_diagram(d, s)
    s.notes_slide.notes_text_frame.text = (
        "The request path: Chat UI → APIM (the authZ boundary) → thin FastAPI → Supervisor (intent) "
        "→ LangGraph. Inside one runtime, agents are logical capabilities orchestrated by the Agent "
        "Harness, using ERC, Tools/MCP, RAG, Memory/Cache and the SLM. Enterprise APIs/events are the "
        "system of record. Guardrails run at every boundary; output is validated before it reaches the user.")

    s = d.content_slide("Four state concepts — kept strictly separate")
    quad = [("Conversation State", "turns, messages, intent — per conversation", CYAN),
            ("Session State", "auth context, correlation, ttl — per session", BLUE),
            ("Workflow / Agent State", "graph state, steps, HIL — per workflow run", GREEN),
            ("Enterprise Business State", "system-of-record truth — owned by PFF", PINK)]
    xs = [0.9, 6.85]; ys = [2.0, 4.35]
    for i, (t, sub, col) in enumerate(quad):
        x = xs[i % 2]; y = ys[i // 2]
        d.box(s, "", x, y, 5.55, 2.05, fill=PANEL, line=col, line_w=1.25)
        d.text(s, t, x + 0.3, y + 0.25, 5.0, 0.5, size=18, color=col, bold=True)
        d.text(s, sub, x + 0.3, y + 0.95, 5.0, 0.9, size=13, color=GREY)
    s.notes_slide.notes_text_frame.text = (
        "These four are never conflated in code. Conflation is a classic source of security and "
        "correctness bugs in agentic systems, so we separate them as first-class concepts.")

    s = d.content_slide("Scope — affiliation first, catalogue deferred")
    d.bullets(s, [
        "One AI runtime; agents are logical capabilities inside it — not one microservice per agent.",
        "AffiliationAgent is the only agent built in the first pass (Phase 23).",
        "The wider agent catalogue (registration, discipline, officials, competitions…) is a real product decision, deliberately deferred — not invented.",
        "Everything is a versioned software artifact: prompts, models, agents, workflows, RAG indexes, guardrails — released as immutable bundles.",
    ], 0.9, 2.0, 11.5, 4.4, size=17, gap=14)
    s.notes_slide.notes_text_frame.text = (
        "We resist scope creep at the architecture level: prove the platform end-to-end on affiliation, "
        "then extend. Immutable versioned bundles mean no in-place production mutation.")

    s = d.content_slide("Technology at a glance")
    d.chip_row(s, [("python", "Python"), ("fastapi", "FastAPI"), ("langgraph", "LangGraph"),
                   ("huggingface", "HF SLM"), ("vllm", "vLLM"), ("aisearch", "AI Search")],
               y=2.1, size=0.9)
    d.chip_row(s, [("aks", "AKS"), ("apim", "APIM"), ("servicebus", "Service Bus"),
                   ("redis", "Redis"), ("keyvault", "Key Vault"), ("langfuse", "Langfuse")],
               y=4.3, size=0.9)
    s.notes_slide.notes_text_frame.text = (
        "Python/FastAPI + LangGraph on Azure/AKS. SLM starts on Hugging Face Inference API and targets "
        "self-hosted vLLM on GPU. Azure AI Search for vectors, Managed Redis for state/cache, Service "
        "Bus for async eventing, APIM as the authZ boundary, Key Vault (SPN-only) for secrets, Langfuse "
        "for AI observability. Full detail and the cost of each is in decks 05 and 08.")

    s = d.content_slide("The ADR programme", "Every significant decision is recorded and governed")
    d.table(s, [
        ["Domain", "ADRs", "Focus"],
        ["D0 Decision Programme", "4", "ADR governance, review board, open-decision register"],
        ["D1 Business", "12", "scope, Golden Rule, persona, workflows, traceability"],
        ["D2 Application", "21", "layering, orchestration, integration, eventing"],
        ["D3 AI", "28", "agents, prompts, SLM, RAG, embeddings, refinement"],
        ["D4 Information", "13", "ERC, state, memory, cache, identifiers"],
        ["D5 Technology", "20", "Azure/AKS, APIM, Key Vault, vLLM, delivery"],
        ["D6 Security & Governance", "19", "zero-trust, masking, guardrails, GDPR"],
        ["D7 Operations", "18", "observability, CI/CD, testing, LLMOps, DR"],
        ["D8 Business Value", "10", "value, metrics, traceability"],
    ], 0.9, 1.95, 11.5, 4.9, col_widths=[3.2, 1.0, 7.3], font_size=12)
    d.text(s, "145 governed ADRs  ·  5 still Proposed and awaiting ARB sign-off (deck 09)",
           0.9, 6.95, 11.5, 0.35, size=12, color=YELLOW, bold=True)
    s.notes_slide.notes_text_frame.text = (
        "145 ADRs across nine decision domains. Most are Accepted; five remain Proposed with a stated "
        "recommendation we are building against — those are what we need the ARB to ratify (deck 09).")

    s = d.content_slide("Cost headline", "Indicative — Azure UK South, Sept 2026, verify with FinOps")
    stats = [("HF API", "hosted SLM phase", CYAN), ("vLLM / GPU", "self-hosted target", VIOLET),
             ("AI Search", "vector store", GREEN), ("Langfuse", "AI observability", PINK)]
    x = 0.9
    for t, sub, col in stats:
        d.box(s, "", x, 2.2, 2.75, 1.9, fill=PANEL, line=col, line_w=1.25)
        d.text(s, t, x + 0.25, 2.45, 2.3, 0.6, size=20, color=col, bold=True)
        d.text(s, sub, x + 0.25, 3.15, 2.3, 0.7, size=12, color=GREY)
        x += 2.95
    d.text(s, "Deck 08 breaks cost down per technology (drivers, formula, Low / Expected / High monthly).",
           0.9, 4.5, 11.5, 0.5, size=15, color=WHITE)
    s.notes_slide.notes_text_frame.text = (
        "Cost is presented per technology in deck 08 with drivers, formula and Low/Expected/High "
        "monthly scenarios. Every figure is an indicative public list price, dated and region-stamped, "
        "to be confirmed by FinOps — pricing is never hard-coded in the application.")

    d.final_slide("What we are asking the ARB",
                  "Note the architecture · ratify the 5 open decisions (deck 09) · endorse the cost model (deck 08)",
                  notes="Three asks: (1) note and challenge the architecture across the domain decks; "
                        "(2) ratify the five Proposed decisions in deck 09; (3) endorse the cost model "
                        "and budget-control approach in deck 08.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
