#!/usr/bin/env python3
"""Deck 01 — Business Architecture & Value (D0 + D1 + D8), FA light theme."""
import os
from fa import (Deck, adrs_for, PP_ALIGN, MSO_SHAPE, MSO_ANCHOR,
                NAVY, NAVY_DEEP, BLUE, GOLD, GREY, WHITE, MUTEDBLUE, CARD, CARD_LINE,
                CX0, CX1, CW)

OUT = os.path.join(os.path.dirname(__file__), "..", "01-business-architecture.pptx")


def affiliation_flow(d, s):
    r1 = ["Club\nchecks", "Select teams\n+ fees", "Insurance", "Other\nproducts", "Summary\n& submit"]
    x = CX0; w = 1.98; gap = 0.24; y = 2.0; h = 0.85; prev = None
    for lab in r1:
        d.box(s, lab, x, y, w, h, style="light", size=11.5)
        if prev is not None:
            d.connector(s, prev, y + h / 2, x, y + h / 2, color=BLUE, width=1.5)
        prev = x + w; x += w + gap
    d.connector(s, CX0 + CW / 2, y + h, CX0 + CW / 2, 3.55, color=BLUE, width=1.6)
    d.text(s, "ROUTING", CX0, 3.35, 3, 0.28, size=11, color=BLUE, bold=True)
    r2 = ["Auto-approve\nor CFA review (HIL)", "Invoice /\npayment", "COMPLETE", "WGS sync\n(national DB)"]
    x = CX0; y2 = 3.7; w2 = (CW - 3 * gap) / 4; prev = None
    for i, lab in enumerate(r2):
        d.box(s, lab, x, y2, w2, h, style=("navy" if lab == "COMPLETE" else "light"), size=11.5)
        if prev is not None:
            d.connector(s, prev, y2 + h / 2, x, y2 + h / 2, color=BLUE, width=1.5)
        prev = x + w2; x += w2 + gap
    d.box(s, "Affiliation confirmed — only after the enterprise event confirms success",
          CX0, 4.95, CW, 0.55, style="accent", size=13)
    d.text(s, "27 scenarios covered (auto-approve, CFA approve/reject/cancel, £0, refund, fold, "
              "payment-fail reconciliation). PFF Chat AI narrates state; PFF decides & executes.",
           CX0, 5.7, CW, 0.6, size=12, color=GREY)


def build():
    d = Deck()
    d.title_slide("Business Architecture", "& Value",
                  "Governance · scope · persona · workflows · value  —  ADR domains D0 / D1 / D8",
                  kicker="Deck 01 · The FA · PFF",
                  notes="Why the platform exists, how decisions are governed, the business scope and "
                        "boundary, the PFF Chat AI persona, the workflow catalogue, and the value case. "
                        "26 ADRs: D0 (4), D1 (12), D8 (10).")

    d.agenda_slide("What this deck covers", [
        "Decision governance — the ADR programme (D0)",
        "The Golden Rule & authoritative-truth precedence",
        "Platform scope, boundary & success definition (D1)",
        "Business capability map & ownership",
        "PFF Chat AI persona model, access archetypes & charter",
        "Conversational journey & human-in-the-loop touchpoints",
        "Workflow catalogue, phasing & affiliation-first",
        "Club Affiliation — the first end-to-end workflow",
        "Requirements baseline & traceability",
        "Business value, metrics & outcomes (D8)",
    ], notes="Governance first, then scope, persona, workflows, and the value case.")

    s = d.content_slide("Decision governance — the ADR programme", kicker="D0 · governance",
                        subtitle="Every significant choice is recorded & governed")
    d.kv_panel(s, "How decisions are made", [
        ("ADR-driven governance", "D0-01 — architecture decided via versioned ADRs"),
        ("Authority & review board", "D0-03 — the ARB approves; owners & reviewers named"),
        ("Lifecycle & supersession", "D0-02 — Proposed → Accepted; never mutate in place"),
        ("Open-decision register", "D0-04 — escalation path for unresolved choices"),
    ], CX0, 1.95, 5.25, 4.5)
    d.bullets(s, [
        "145 ADRs across 9 domains — the audit trail of the architecture.",
        "5 remain Proposed with a stated recommendation we build against.",
        "Each ADR carries owner, reviewers, approver (ARB), status, version, source-doc refs and impacted paths.",
        "Deck 09 presents the 5 open decisions for your sign-off.",
    ], 7.5, 2.05, 5.25, 4.3, size=14, gap=13)
    d.set_notes(s, "Governance is itself an ADR (D0-01). The ARB is the approving authority; the "
                   "register keeps open items visible.")

    s = d.content_slide("The Golden Rule", kicker="D1-02 · binding constraint")
    d.box(s, "Enterprise systems DECIDE and EXECUTE.\nThe AI platform INTERPRETS, ORCHESTRATES,\n"
             "CONTEXTUALISES, EXPLAINS and COMMUNICATES.",
          CX0, 1.9, CW, 1.6, style="navy", size=20)
    d.text(s, "Precedence:  Enterprise API / Event  ›  ERC  ›  Cache  ›  RAG  ›  SLM output",
           CX0, 3.7, CW, 0.4, size=14, color=BLUE, bold=True)
    d.bullets(s, [
        "AI never authenticates/authorizes, re-implements business rules, or writes to the enterprise DB.",
        "A model output is never an authorization decision; unconfirmed transactions are never celebrated.",
        "Agents are logical capabilities in one runtime — not a microservice per agent.",
    ], CX0, 4.25, CW, 2.0, size=14, gap=12)
    d.set_notes(s, "The single most important constraint, repeated in every spec doc (D1-02/D1-03).")

    s = d.content_slide("Scope, boundary & success", kicker="D1-01 / D1-04")
    d.two_col(s, "In scope", [
        "Conversational orchestration over PFF for club/county administration.",
        "Interpretation, ERC context, reasoning, controlled tool-calls, communication.",
        "Affiliation workflow end-to-end first; WGS integration on complete.",
    ], "Out of scope (by rule)", [
        "Business/compliance rule re-implementation.",
        "Direct enterprise DB writes; auth decisions.",
        "Inventing portal URLs, IDs, or transaction outcomes.",
        "Exposing raw enterprise/PII to an external SLM.",
    ])
    d.set_notes(s, "Success = correct, safe progression of real workflows with the AI strictly on the "
                   "interpret/communicate side of the boundary.")

    s = d.content_slide("Business capability map & ownership", kicker="D1-06")
    d.table(s, [
        ["Capability", "Owner (system of record)", "AI platform role"],
        ["Club affiliation", "PFF", "orchestrate, contextualise, communicate"],
        ["Team & player registration", "PFF / WGS", "deferred agent — interpret & guide"],
        ["Insurance (PL / PA)", "PFF + providers", "gather ERC, explain options"],
        ["Discipline & GRF", "PFF", "deferred — status & guidance"],
        ["Officials & safeguarding", "PFF / WGS", "check surfacing, no decisions"],
        ["County cups & competitions", "PFF", "deferred agent"],
        ["Payments & invoicing", "PFF / PAAS / Xero", "narrate state, never confirm unverified"],
    ], CX0, 1.95, CW, 4.5, col_widths=[3.0, 3.9, 4.0], font_size=11.5)
    d.set_notes(s, "Ownership stays with PFF/WGS. The AI-role column is verbs on the "
                   "interpret/communicate side — never decide/execute.")

    s = d.content_slide("PFF Chat AI persona — model & charter", kicker="D1-07 / D1-09",
                        subtitle="Workflow-first, with a natural football-commentary tone")
    d.two_col(s, "Persona rules", [
        "Workflow-first: personality supports completion, never distracts.",
        "Football-commentary tone, used at meaningful moments only.",
        "Enterprise truth overrides persona — always.",
        "Never celebrate an unconfirmed transaction ('GOAL!' only on confirmed success).",
        "Errors & pending/HIL states stay factual and explicit.",
    ], "Access archetypes", [
        "Club Admin — primary affiliation actor.",
        "CFA Admin / reviewer — approvals (HIL).",
        "County & league roles — scoped visibility.",
        "Persona is a versioned prompt layer, reusable across workflows.",
    ])
    d.set_notes(s, "PFF Chat AI is a workflow-first enterprise assistant with a natural commentary tone. "
                   "Persona controls how PFF Chat AI communicates, never what the result is.")

    s = d.content_slide("Conversational journey & HIL", kicker="D1-08",
                        subtitle="Where humans stay in the loop")
    d.pipeline(s, [("Intent", "what the user wants"), ("Gather", "ERC context"),
                   ("Reason", "eligibility via enterprise"), ("Confirm", "HIL checkpoint"),
                   ("Execute", "enterprise API"), ("Communicate", "state + next step")],
               y=2.7, h=1.05)
    d.bullets(s, [
        "HIL touchpoints: user confirmation before submission; CFA review/approval; payment authorisation; external portal actions.",
        "PFF Chat AI clearly states who/what the workflow is waiting for during pending states.",
    ], CX0, 4.3, CW, 1.8, size=14, gap=12)
    d.set_notes(s, "Human-in-the-loop is explicit and designed — confirmations, CFA review, payment "
                   "authorisation and external portal steps.")

    s = d.content_slide("Workflow catalogue & phasing", kicker="D1-10 / D1-11",
                        subtitle="Affiliation first")
    d.two_col(s, "Catalogue (phased)", [
        "Affiliation — built first, end-to-end (Phase 23).",
        "Registration, discipline, accreditation, insurance, officials, league mgmt, approvals — deferred.",
        "Catalogue finalised by a real product decision, not invented.",
    ], "Why affiliation first", [
        "Exercises every platform capability: ERC, tools, RAG, SLM, guardrails, eventing, HIL.",
        "Highest business value and clearest success metric.",
        "Proves the architecture before breadth.",
    ])
    d.set_notes(s, "We build one agent (AffiliationAgent) fully rather than many shallowly.")

    s = d.content_slide("Club Affiliation — the first E2E workflow", kicker="D1-05",
                        subtitle="PFF Chat AI narrates; PFF decides & executes")
    affiliation_flow(d, s)
    d.set_notes(s, "The canonical flow: club checks → select teams & fees → insurance → other "
                   "products → summary & submit → routing (auto-approve or CFA review HIL) → "
                   "invoice/payment → COMPLETE → WGS sync. 27 scenarios incl. payment-fail "
                   "reconciliation. PFF Chat AI only confirms success when the enterprise confirms it.")

    s = d.content_slide("Requirements & traceability", kicker="D1-12")
    d.bullets(s, [
        "A requirements baseline with a stable traceability scheme (WS-refs) links each requirement to the ADRs and source docs that satisfy it.",
        "Every ADR cites its source-doc sections; the decision register and traceability matrix are generated artifacts.",
        "The ARB can trace any decision back to a business requirement and forward to impacted code paths.",
    ], CX0, 1.95, CW, 3.4, size=16, gap=15)
    d.set_notes(s, "Traceability is a first-class governance artifact — requirement → ADR → source "
                   "doc → impacted path — maintained in the ADR register.")

    s = d.content_slide("Business value & outcomes", kicker="D8",
                        subtitle="Why this is worth building")
    d.stat_cards(s, [("Faster", "guided affiliation, fewer failed pre-checks"),
                     ("Fewer errors", "ERC-grounded, guardrailed responses"),
                     ("Lower support load", "self-service with clear next actions"),
                     ("Auditable", "every decision traced & governed")], y=2.1, h=1.9)
    d.bullets(s, [
        "D8 frames value, defines success metrics, and keeps a decision-register/traceability link so value claims are measurable.",
        "Cost-per-successful-affiliation (deck 08) is the meaningful unit, not cost-per-request.",
    ], CX0, 4.4, CW, 1.8, size=14, gap=12)
    d.set_notes(s, "D8 keeps the value case measurable and tied to the decision register.")

    d.adr_index_slides("ADR index — Business & Value (D0 · D1 · D8)", adrs_for(0, 1, 8),
                       notes="All 26 business-domain ADRs. D0 governs the decision process; D1 the "
                             "business architecture; D8 the value case. None open in this domain.")

    d.final_slide("Business architecture — summary",
                  "Governed decisions · a hard AI/enterprise boundary · affiliation-first · measurable value",
                  notes="Takeaway: governed end-to-end, an absolute AI/enterprise boundary, value "
                        "proven on affiliation first.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
