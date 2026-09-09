#!/usr/bin/env python3
"""Deck 00 — PFF AI Technical overview, FA enterprise light theme (blue + white)."""
import os
from fa import (Deck, PP_ALIGN, MSO_ANCHOR, MSO_SHAPE,
                WHITE, NAVY, NAVY_DEEP, BLUE, GOLD, CARD, CARD_LINE, GREY, MUTEDBLUE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "00-overview.pptx")
DATE = "September 2026"


def master_diagram(d, s):
    # runtime container (light card)
    d.card(s, CX0, 3.05, CW, 2.35)
    d.text(s, "AI RUNTIME  ·  single LangGraph process  ·  agents = logical capabilities",
           CX0 + 0.15, 3.12, 6.8, 0.3, size=10, color=BLUE, bold=True)
    d.text(s, "Guardrails at every boundary (input · context · prompt · tool · model · output)",
           CX0 + 3.9, 3.12, CW - 4.05, 0.3, size=10, color=GREY, bold=True, align=PP_ALIGN.RIGHT)

    bandA = ["Chat UI", "APIM\nauthN / authZ", "FastAPI\nthin API",
             "Supervisor\nintent routing", "LangGraph\norchestration"]
    x = CX0; w = 1.95; gap = 0.28; y = 1.85; h = 0.72; prev = None; centers = []
    for i, lab in enumerate(bandA):
        st = "accent" if lab.startswith("LangGraph") else "light"
        d.box(s, lab, x, y, w, h, style=st, size=11.5)
        centers.append(x + w / 2)
        if prev is not None:
            d.connector(s, prev, y + h / 2, x, y + h / 2, width=1.5)
        prev = x + w; x += w + gap
    d.connector(s, centers[-1], y + h, centers[-1], 3.05, color=BLUE, width=1.75)

    d.box(s, "Agents\n(AffiliationAgent first)", CX0 + 0.2, 3.58, 2.45, 0.95, style="light", size=11)
    caps = ["ERC\ncontext", "Tools / MCP", "RAG\nknowledge", "Memory /\nCache", "SLM\nHF → vLLM"]
    cx = CX0 + 2.85; cw = 1.5; ch = 0.95
    for lab in caps:
        d.box(s, lab, cx, 3.9, cw, ch, style="light", size=10.5)
        cx += cw + 0.12
    d.connector(s, CX0 + 2.65, 4.05, CX0 + 2.85, 4.05, width=1.4)

    y2 = 5.6
    d.box(s, "Enterprise APIs / Events  —  PFF System of Record (decides & executes)",
          CX0 + 0.2, y2, 6.7, 0.5, style="navy", size=11)
    d.box(s, "Output\nGuardrail", 9.05, y2, 1.6, 0.5, style="light", size=10.5)
    d.box(s, "Response", 10.8, y2, 1.85, 0.5, style="accent", size=11)
    d.connector(s, CX0 + 3.5, 4.85, CX0 + 3.5, y2, width=1.5)
    d.connector(s, 8.75, y2 + 0.25, 9.05, y2 + 0.25, width=1.4)
    d.connector(s, 10.45, y2 + 0.25, 10.8, y2 + 0.25, width=1.4)

    d.text(s, "Authoritative-truth precedence:  Enterprise API / Event  ›  ERC  ›  Cache  ›  RAG  ›  SLM output",
           CX0, 6.35, CW, 0.3, size=11, color=NAVY, bold=True, align=PP_ALIGN.CENTER)


def precedence_diagram(d, s):
    steps = [("Enterprise API / Event", "System of record — decides & executes"),
             ("ERC", "Enterprise Runtime Context — validated, provenanced"),
             ("Cache", "Authorization-aware, freshness-bounded"),
             ("RAG", "Retrieved knowledge — cited, ACL-enforced"),
             ("SLM output", "Language only — never a source of authority")]
    y = 1.9; h = 0.78; gap = 0.18
    for i, (t, sub) in enumerate(steps):
        d.card(s, CX0, y, CW, h)                       # bordered item card
        cy = y + h / 2
        d.num_circle(s, CX0 + 0.55, cy, i + 1, dia=0.5)
        d.text(s, t, CX0 + 1.1, y + 0.12, 6.0, 0.34, size=15, color=NAVY, bold=True,
               font="Cambria")
        d.text(s, sub, CX0 + 1.1, y + 0.44, 9.2, 0.3, size=11.5, color=GREY)
        if i < len(steps) - 1:
            d.text(s, "▼", CX0 + 0.4, y + h - 0.02, 0.3, gap + 0.04, size=11, color=BLUE,
                   bold=True, align=PP_ALIGN.CENTER)
        y += h + gap
    d.text(s, "Higher source always wins on conflict — no exceptions.", CX0, y + 0.02,
           CW, 0.3, size=11, color=MUTEDBLUE, italic=True)


def build():
    d = Deck()

    d.title_slide("PFF AI — Adam AI", "Enterprise Agentic AI Platform",
                  f"Technical architecture for the Architecture Review Board  ·  {DATE}",
                  kicker="The FA · PFF · Technical Architecture",
                  notes="Welcome. This is the technical walkthrough of the PFF-FA Enterprise Agentic "
                        "AI platform — Adam AI — for the ARB. This overview frames the whole system; "
                        "nine further decks go deep by domain, plus cost and the open decisions.")

    s = d.content_slide("Presentation suite", kicker="Agenda", accent_tail="— 10 decks",
                        subtitle="Short on the slide, deep in the narration — all 145 ADRs and 29 spec docs covered")
    left = ["00  Overview — whole-system picture", "01  Business Architecture & Value",
            "02  Application & Orchestration", "03  AI Architecture",
            "04  Information, Context & Data"]
    right = ["05  Technology & Infrastructure", "06  Security & Governance",
             "07  Operations, Observability & Quality", "08  Cost & FinOps",
             "09  Open Decisions & ARB sign-off asks"]
    d.bullets(s, left, CX0, 2.0, 5.3, 4.4, size=15, gap=14)
    d.bullets(s, right, 7.35, 2.0, 5.3, 4.4, size=15, gap=14)
    d.set_notes(s, "Ten decks. Each is short on the slide and deep in the "
        "speaker notes so discussion stays live. All 145 ADRs and 29 specification documents are covered.")

    s = d.content_slide("What we are building", kicker="Context",
                        subtitle="Adam AI — a conversational orchestration layer over PFF")
    d.bullets(s, [
        "PFF is the FA's county/club administration platform — affiliation, registration, insurance, discipline, officials, county cups, payments; integrates with WGS (the FA's national database).",
        "Adam AI interprets requests, gathers enterprise context, reasons, calls controlled tools, and communicates results — it does not replace PFF's business logic or authority.",
        "First end-to-end workflow delivered: Club Affiliation.",
        "Persona: a workflow-first enterprise assistant with a natural football-commentary tone.",
    ], CX0, 1.95, CW, 4.6, size=16, gap=14)
    d.set_notes(s, "This is an orchestration layer, not a rewrite. PFF remains "
        "the system of record. WGS is the national football database we integrate with.")

    s = d.content_slide("The Golden Rule", kicker="Binding constraint",
                        subtitle="The single most important architectural principle")
    d.box(s, "Enterprise systems DECIDE and EXECUTE.\nThe AI platform INTERPRETS, ORCHESTRATES,\nCONTEXTUALISES, EXPLAINS and COMMUNICATES.",
          CX0, 1.95, CW, 1.75, style="navy", size=21)
    d.bullets(s, [
        "The AI never authenticates/authorizes, re-implements business rules, or writes to the enterprise DB.",
        "A model output never becomes an authorization decision.",
        "Raw enterprise/personal data is never exposed to an external SLM (masked/tokenised, fail-closed).",
    ], CX0, 4.0, CW, 2.2, size=15, gap=12)
    d.set_notes(s, "Repeated in every spec doc. Everything downstream — "
        "guardrails, ERC, truth precedence, masking — enforces it.")

    s = d.content_slide("Authoritative-truth precedence", kicker="Golden Rule",
                        subtitle="Higher source always wins on conflict")
    precedence_diagram(d, s)
    d.set_notes(s, "When two sources disagree, the higher wins — no exceptions. "
        "The SLM generates language but is the lowest-trust source.")

    s = d.content_slide("End-to-end platform architecture", kicker="System overview")
    master_diagram(d, s)
    d.set_notes(s, "Chat UI → APIM (authZ boundary) → thin FastAPI → "
        "Supervisor → LangGraph. Inside one runtime, agents are logical capabilities using ERC, "
        "Tools/MCP, RAG, Memory/Cache and the SLM. Enterprise APIs/events are the system of record; "
        "guardrails run at every boundary; output is validated before the user sees it.")

    s = d.content_slide("Four state concepts", kicker="Information model",
                        subtitle="Kept strictly separate — never conflated in code")
    quad = [("Conversation State", "turns, messages, intent — per conversation"),
            ("Session State", "auth context, correlation, ttl — per session"),
            ("Workflow / Agent State", "graph state, steps, HIL — per workflow run"),
            ("Enterprise Business State", "system-of-record truth — owned by PFF")]
    xs = [CX0, 7.4]; ys = [1.95, 4.25]; cw = 5.25; ch = 1.95
    for i, (t, sub) in enumerate(quad):
        x = xs[i % 2]; y = ys[i // 2]
        col = NAVY if i % 2 == 0 else BLUE
        d.card(s, x, y, cw, ch)
        d._rect(s, x, y + 0.32, 0.12, 0.9, col)      # accent tab (not a full border stripe)
        d.text(s, t, x + 0.35, y + 0.32, cw - 0.6, 0.5, size=18, color=col, bold=True, font="Cambria")
        d.text(s, sub, x + 0.35, y + 1.02, cw - 0.6, 0.8, size=13, color=GREY)
    d.set_notes(s, "Enterprise business state is owned entirely by PFF; the "
        "AI holds only conversation, session and workflow state.")

    s = d.content_slide("Scope", kicker="Delivery approach",
                        subtitle="Affiliation first, wider catalogue deferred")
    d.bullets(s, [
        "One AI runtime; agents are logical capabilities inside it — not one microservice per agent.",
        "AffiliationAgent is the only agent built in the first pass.",
        "The wider agent catalogue (registration, discipline, officials, competitions…) is a real product decision, deliberately deferred — not invented.",
        "Everything is a versioned software artifact: prompts, models, agents, workflows, RAG indexes, guardrails — released as immutable bundles.",
    ], CX0, 1.95, CW, 4.4, size=16, gap=14)
    d.set_notes(s, "Prove the platform end-to-end on affiliation, then extend. "
        "Immutable versioned bundles mean no in-place production mutation.")

    s = d.content_slide("Technology at a glance", kicker="Technology stack")
    d.chip_row(s, [("python", "Python"), ("fastapi", "FastAPI"), ("langgraph", "LangGraph"),
                   ("huggingface", "HF SLM"), ("vllm", "vLLM"), ("aisearch", "AI Search")],
               y=2.15, size=0.85)
    d.chip_row(s, [("aks", "AKS"), ("apim", "APIM"), ("servicebus", "Service Bus"),
                   ("redis", "Redis"), ("keyvault", "Key Vault"), ("langfuse", "Langfuse")],
               y=4.35, size=0.85)
    d.set_notes(s, "Python/FastAPI + LangGraph on Azure/AKS. SLM starts on "
        "Hugging Face and targets self-hosted vLLM on GPU. AI Search for vectors, Managed Redis for "
        "state/cache, Service Bus for eventing, APIM as the authZ boundary, Key Vault for secrets, "
        "Langfuse for AI observability. Cost of each is in deck 08.")

    s = d.content_slide("The ADR programme", kicker="Governance",
                        subtitle="Every significant decision recorded and governed")
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
    ], CX0, 1.9, CW, 4.6, col_widths=[3.0, 0.9, 6.95], font_size=11.5)
    d.text(s, "145 governed ADRs  ·  5 still Proposed and awaiting ARB sign-off (deck 09)",
           CX0, 6.6, CW, 0.35, size=12, color=BLUE, bold=True)
    d.set_notes(s, "145 ADRs across nine domains. Most Accepted; five remain "
        "Proposed with a stated recommendation we build against — deck 09 asks the ARB to ratify them.")

    s = d.content_slide("Cost headline", kicker="Cost & FinOps",
                        subtitle="Indicative — Azure UK South, Sept 2026, verify with FinOps")
    d.stat_cards(s, [("HF → vLLM", "SLM inference — dominant lever"),
                     ("Azure AI Search", "vector store"),
                     ("Langfuse", "AI observability"),
                     ("AKS / GPU", "compute")], y=2.15, h=1.9)
    d.text(s, "Deck 08 breaks cost down per technology — drivers, formula, Low / Expected / High monthly.",
           CX0, 4.4, CW, 0.5, size=15, color=NAVY)
    d.set_notes(s, "Cost is per technology in deck 08 with drivers, formula and "
        "Low/Expected/High scenarios — indicative public list prices, dated and region-stamped, to be "
        "confirmed by FinOps; never hard-coded in the application.")

    d.final_slide("What we are asking the ARB",
                  "Note the architecture  ·  ratify the 5 open decisions (deck 09)  ·  endorse the cost model (deck 08)",
                  notes="Three asks: note and challenge the architecture; ratify the five Proposed "
                        "decisions; endorse the cost model and budget controls.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
