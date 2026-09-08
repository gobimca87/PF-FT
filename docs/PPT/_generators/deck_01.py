#!/usr/bin/env python3
"""Deck 01 — Business Architecture & Value (D0 + D1 + D8)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "01-business-architecture.pptx")


def affiliation_flow(d, s):
    r1 = ["Club\nchecks", "Select teams\n+ fees", "Insurance", "Other\nproducts", "Summary\n& submit"]
    cols1 = [CYAN, BLUE, GREEN, PURPLE, YELLOW]
    x = 0.55; w = 2.15; gap = 0.34; y = 2.0; h = 0.85
    prev = None
    for i, lab in enumerate(r1):
        d.box(s, lab, x, y, w, h, fill=PANEL2, line=cols1[i], size=12)
        if prev is not None:
            d.connector(s, prev, y + h/2, x, y + h/2, color=GREY, width=1.4)
        prev = x + w; x += w + gap
    # down arrow to routing row
    d.connector(s, prev - w/2, y + h, prev - w/2, 3.55, color=YELLOW, width=1.6)

    d.text(s, "ROUTING", 0.55, 3.35, 3, 0.3, size=11, color=PINK, bold=True)
    r2 = ["Auto-approve\nor CFA review (HIL)", "Invoice /\npayment", "COMPLETE", "WGS sync\n(national DB)"]
    cols2 = [PINK, BLUE, GREEN, CYAN]
    x = 0.55; y2 = 3.7; w2 = 2.7; prev = None
    for i, lab in enumerate(r2):
        col = cols2[i]
        d.box(s, lab, x, y2, w2, h, fill=PANEL2, line=col, size=12)
        if prev is not None:
            d.connector(s, prev, y2 + h/2, x, y2 + h/2, color=GREY, width=1.4)
        prev = x + w2; x += w2 + gap
    d.box(s, "GOAL!  affiliation confirmed — only after the enterprise event confirms success",
          0.55, 4.95, 11.8, 0.6, fill=PANEL, line=GREEN, textcolor=GREEN, size=13)
    d.text(s, "27 scenarios covered (auto-approve, CFA approve/reject/cancel, £0, refund, fold, "
              "payment-fail reconciliation). Adam narrates state; PFF decides & executes.",
           0.55, 5.75, 11.8, 0.6, size=12, color=GREY)


def build():
    d = Deck()
    d.title_slide("01 · Business Architecture & Value",
                  "Governance · scope · persona · workflows · value  (ADR domains D0 / D1 / D8)",
                  notes="This deck covers why the platform exists, how decisions are governed, "
                        "the business scope and boundary, the Adam persona, the workflow catalogue, "
                        "and the business-value case. 26 ADRs: D0 (4), D1 (12), D8 (10).")

    d.agenda_slide("What this deck covers", [
        "Decision governance — the ADR programme (D0)",
        "The Golden Rule & authoritative-truth precedence",
        "Platform scope, boundary & success definition (D1)",
        "Business capability map & ownership",
        "Adam persona model, access archetypes & charter",
        "Conversational journey & human-in-the-loop touchpoints",
        "Workflow catalogue, phasing & affiliation-first",
        "Club Affiliation — the first end-to-end workflow",
        "Requirements baseline & traceability",
        "Business value, metrics & outcomes (D8)",
    ], notes="Governance first, then scope, persona, workflows, and the value case.")

    s = d.content_slide("Decision governance — the ADR programme", "D0 · every significant choice is recorded & governed")
    kv_panel(d, s, "How decisions are made", [
        ("ADR-driven governance", "D0-01 — architecture decided via versioned ADRs"),
        ("Authority & review board", "D0-03 — the ARB approves; owners & reviewers named"),
        ("Lifecycle & supersession", "D0-02 — Proposed → Accepted; never mutate in place"),
        ("Open-decision register", "D0-04 — escalation path for unresolved choices"),
    ], 0.9, 1.95, 5.7, 4.6)
    d.bullets(s, [
        "145 ADRs across 9 domains — the audit trail of the architecture.",
        "5 remain Proposed with a stated recommendation we build against.",
        "Each ADR carries owner, reviewers, approver (ARB), status, version, source-doc refs and impacted paths.",
        "Deck 09 presents the 5 open decisions for your sign-off.",
    ], 6.85, 2.1, 5.6, 4.4, size=15, gap=14)
    s.notes_slide.notes_text_frame.text = ("Governance is itself an ADR (D0-01). The ARB is the "
        "approving authority. Nothing is decided informally; the register keeps open items visible.")

    s = d.content_slide("The Golden Rule", "D1-02 · the binding architectural constraint")
    d.box(s, "Enterprise systems DECIDE and EXECUTE.\nThe AI platform INTERPRETS, ORCHESTRATES,\nCONTEXTUALISES, EXPLAINS and COMMUNICATES.",
          1.3, 1.95, 10.7, 1.85, fill=PANEL, line=YELLOW, size=21, bold=True)
    d.text(s, "Precedence:  Enterprise API / Event  ›  ERC  ›  Cache  ›  RAG  ›  SLM output",
           1.3, 4.05, 10.7, 0.4, size=15, color=CYAN, bold=True)
    d.bullets(s, [
        "AI never authenticates/authorizes, re-implements business rules, or writes to the enterprise DB.",
        "A model output is never an authorization decision; unconfirmed transactions are never celebrated.",
        "Agents are logical capabilities in one runtime — not a microservice per agent.",
    ], 1.3, 4.6, 10.7, 2.0, size=14, gap=12)
    s.notes_slide.notes_text_frame.text = ("The single most important constraint, repeated in every "
        "spec doc and encoded by D1-02/D1-03. Everything else enforces it.")

    s = d.content_slide("Scope, boundary & success", "D1-01 / D1-04 · what is in and out")
    two_col(d, s,
            "In scope", [
                "Conversational orchestration over PFF for club/county administration.",
                "Interpretation, ERC context, reasoning, controlled tool-calls, communication.",
                "Affiliation workflow end-to-end first; WGS integration on complete.",
            ],
            "Out of scope (by rule)", [
                "Business/compliance rule re-implementation.",
                "Direct enterprise DB writes; auth decisions.",
                "Inventing portal URLs, IDs, or transaction outcomes.",
                "Exposing raw enterprise/PII to an external SLM.",
            ])
    s.notes_slide.notes_text_frame.text = ("Success = correct, safe progression of real business "
        "workflows with the AI strictly on the interpret/communicate side of the boundary.")

    s = d.content_slide("Business capability map & ownership", "D1-06")
    d.table(s, [
        ["Capability", "Owner (system of record)", "AI platform role"],
        ["Club affiliation", "PFF", "orchestrate, contextualise, communicate"],
        ["Team & player registration", "PFF / WGS", "deferred agent — interpret & guide"],
        ["Insurance (PL / PA)", "PFF + providers", "gather ERC, explain options"],
        ["Discipline & GRF", "PFF", "deferred — status & guidance"],
        ["Officials & safeguarding", "PFF / WGS", "check surfacing, no decisions"],
        ["County cups & competitions", "PFF", "deferred agent"],
        ["Payments & invoicing", "PFF / PAAS / Xero", "narrate state, never confirm unverified"],
    ], 0.9, 1.95, 11.5, 4.6, col_widths=[3.0, 4.2, 4.3], font_size=12)
    s.notes_slide.notes_text_frame.text = ("Ownership stays with PFF/WGS. The AI role column is "
        "deliberately verbs on the interpret/communicate side — never decide/execute.")

    s = d.content_slide("Adam persona — model & charter", "D1-07 / D1-09 · workflow-first, football-commentary tone")
    two_col(d, s,
            "Persona rules", [
                "Workflow-first: personality supports completion, never distracts.",
                "Football-commentary tone, used at meaningful moments only.",
                "Enterprise truth overrides persona — always.",
                "Never celebrate an unconfirmed transaction ('GOAL!' only on confirmed success).",
                "Errors & pending/HIL states stay factual and explicit.",
            ],
            "Access archetypes", [
                "Club Admin — primary affiliation actor.",
                "CFA Admin / reviewer — approvals (HIL).",
                "County & league roles — scoped visibility.",
                "Persona is a versioned prompt layer, reusable across workflows.",
            ])
    s.notes_slide.notes_text_frame.text = ("Adam is a workflow-first enterprise assistant with a "
        "natural commentary tone. SampleWorkflowchat.md is the canonical reference. Persona controls "
        "how Adam communicates, never what the result is.")

    s = d.content_slide("Conversational journey & HIL", "D1-08 · where humans stay in the loop")
    pipeline(d, s, [("Intent", "what the user wants"), ("Gather", "ERC context"),
                    ("Reason", "eligibility via enterprise"), ("Confirm", "HIL checkpoint"),
                    ("Execute", "enterprise API"), ("Communicate", "state + next step")],
             y=2.6, h=1.0)
    d.bullets(s, [
        "HIL touchpoints: user confirmation before submission; CFA review/approval; payment authorisation; external portal actions.",
        "Adam clearly states who/what the workflow is waiting for during pending states.",
    ], 0.9, 4.2, 11.5, 1.8, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = ("Human-in-the-loop is explicit and designed, not an "
        "afterthought — confirmations, CFA review, payment authorisation and external portal steps.")

    s = d.content_slide("Workflow catalogue & phasing", "D1-10 / D1-11 · affiliation first")
    two_col(d, s,
            "Catalogue (phased)", [
                "Affiliation — built first, end-to-end (Phase 23).",
                "Registration, discipline, accreditation, insurance, officials, league management, approvals — deferred.",
                "Catalogue finalised by a real product decision, not invented.",
            ],
            "Why affiliation first", [
                "Exercises every platform capability: ERC, tools, RAG, SLM, guardrails, eventing, HIL.",
                "Highest business value and clearest success metric.",
                "Proves the architecture before breadth.",
            ])
    s.notes_slide.notes_text_frame.text = ("We build one agent (AffiliationAgent) fully rather than "
        "many shallowly. D1-11 fixes the first-pass agent catalogue to affiliation only.")

    s = d.content_slide("Club Affiliation — the first E2E workflow", "D1-05 · Adam narrates; PFF decides & executes")
    affiliation_flow(d, s)
    s.notes_slide.notes_text_frame.text = ("The canonical flow (pff_affiliation_e2e_flow.md): club "
        "checks → select teams & fees → insurance → other products → summary & submit → routing "
        "(auto-approve or CFA review HIL) → invoice/payment → COMPLETE → WGS sync. 27 scenarios "
        "including payment-fail reconciliation. Adam only says 'GOAL' when the enterprise confirms.")

    s = d.content_slide("Requirements & traceability", "D1-12")
    d.bullets(s, [
        "A requirements baseline with a stable traceability scheme (WS-refs) links each requirement to the ADRs and source docs that satisfy it.",
        "Every ADR cites its source-doc sections; the decision register and traceability matrix are generated artifacts.",
        "This lets the ARB trace any decision back to a business requirement and forward to impacted code paths.",
    ], 0.9, 2.0, 11.5, 3.5, size=16, gap=16)
    s.notes_slide.notes_text_frame.text = ("Traceability is a first-class governance artifact — "
        "requirement → ADR → source doc → impacted path — maintained in the ADR register.")

    s = d.content_slide("Business value & outcomes", "D8 · why this is worth building")
    stat_cards(d, s, [
        ("Faster", "guided affiliation, fewer failed pre-checks", CYAN),
        ("Fewer errors", "ERC-grounded, guardrailed responses", GREEN),
        ("Lower support load", "self-service with clear next actions", PURPLE),
        ("Auditable", "every decision traced & governed", YELLOW),
    ], y=2.1, h=2.0)
    d.bullets(s, [
        "D8 frames value, defines success metrics, and keeps a decision-register/traceability link so value claims are measurable.",
        "Cost-per-successful-affiliation (deck 08) is the meaningful unit, not cost-per-request.",
    ], 0.9, 4.5, 11.5, 1.8, size=15, gap=12)
    s.notes_slide.notes_text_frame.text = ("D8 keeps the value case measurable and tied to the "
        "decision register. The right cost unit is per successful outcome.")

    adr_index_slides(d, "ADR index — Business & Value (D0 · D1 · D8)",
                     adrs_for(0, 1, 8),
                     notes="All 26 business-domain ADRs. D0 governs the decision process; D1 the "
                           "business architecture; D8 the value case. None are open in this domain.")

    d.final_slide("Business architecture — summary",
                  "Governed decisions · a hard AI/enterprise boundary · affiliation-first · measurable value",
                  notes="Takeaway: the business architecture is governed end-to-end, the AI/enterprise "
                        "boundary is absolute, and we prove value on affiliation first.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
