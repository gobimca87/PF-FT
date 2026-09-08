#!/usr/bin/env python3
"""Deck 06 — Security & Governance (D6)."""
import os
from orion import (Deck, PP_ALIGN, MSO_SHAPE, WHITE, GREY, MUTED, CYAN, BLUE,
                   PURPLE, PINK, VIOLET, YELLOW, GREEN, PANEL, PANEL2)
from common import adrs_for, adr_index_slides, stat_cards, two_col, pipeline, kv_panel

OUT = os.path.join(os.path.dirname(__file__), "..", "06-security-governance.pptx")


def trust_zones(d, s):
    zones = [("UNTRUSTED", "user input · external SLM · public content", PINK),
             ("PERIMETER", "APIM — authN / authZ / rate-limit", YELLOW),
             ("TRUSTED RUNTIME", "AKS — agents, harness, guardrails (in-tenancy)", CYAN),
             ("SYSTEM OF RECORD", "PFF enterprise APIs / DB — decides & executes", GREEN)]
    x = 0.7
    widths = [2.7, 2.6, 3.9, 2.7]
    for (t, sub, col), w in zip(zones, widths):
        d.box(s, "", x, 2.2, w, 3.2, fill=PANEL2, line=col, line_w=1.3)
        d.text(s, t, x + 0.2, 2.4, w - 0.4, 0.5, size=14, color=col, bold=True)
        d.text(s, sub, x + 0.2, 3.0, w - 0.4, 2.2, size=12, color=GREY)
        if x > 0.8:
            d.connector(s, x - 0.18, 3.8, x, 3.8, color=WHITE, width=1.4)
        x += w + 0.18
    d.text(s, "Trust decreases left→right for data; authority increases left→right. Nothing crosses a "
              "boundary without validation; egress to the untrusted zone is masked & fail-closed.",
           0.7, 5.7, 11.9, 0.8, size=13, color=GREY)


def guardrail_pipeline(d, s):
    pipeline(d, s, ["Input", "Context", "Prompt", "Tool", "Model", "Output"],
             y=2.6, h=1.0, colors=[PINK, CYAN, VIOLET, YELLOW, BLUE, GREEN])
    d.bullets(s, [
        "Guardrails are middleware applied at every boundary, not a single output filter.",
        "Each stage can block, sanitise, or escalate; failures are typed (GuardrailError).",
        "Placement (D6-09) guarantees no path reaches the model or the user unchecked.",
    ], 0.9, 4.2, 11.5, 1.9, size=14, gap=11)


def build():
    d = Deck()
    d.title_slide("06 · Security & Governance",
                  "Zero-trust · masking · guardrails · GDPR · audit  (D6, 19 ADRs — 1 open)",
                  notes="Security and governance — the controls that make the Golden Rule and data "
                        "protection real. 19 ADRs; one is Proposed (the SLM input masking regime, deck 09).")

    d.agenda_slide("What this deck covers", [
        "Zero-trust & trust zones",
        "AuthN/authZ boundary & context propagation",
        "Network segmentation, egress, encryption & keys",
        "Data classification & PII protection",
        "External-SLM data boundary & masking regime",
        "Guardrail pipeline & prompt-injection defence",
        "Tool & MCP security; RAG ACL enforcement",
        "Responsible AI, human oversight & HIL governance",
        "GDPR, safeguarding & children's data; audit logging",
        "Change governance, release gates & standards conformance",
    ])

    s = d.content_slide("Zero-trust & trust zones", "D6-01")
    trust_zones(d, s)
    s.notes_slide.notes_text_frame.text = ("Zero-trust: every boundary validates. Data trust decreases "
        "toward the untrusted zone (user input, external SLM); business authority increases toward the "
        "system of record. Egress to the untrusted zone is masked and fails closed.")

    s = d.content_slide("AuthN/authZ boundary & propagation", "D6-02 / D6-03")
    two_col(d, s,
            "Boundary", [
                "APIM/enterprise auth authenticates & authorizes — the AI never does.",
                "The AI only consumes validated claims.",
                "A model output is never an authorization decision.",
            ],
            "Context integrity", [
                "Authorization context is integrity-protected & propagated with the request.",
                "Correlation IDs carry it through async/event paths.",
                "Cache & RAG are authorization-aware (never cross scopes).",
            ])
    s.notes_slide.notes_text_frame.text = ("Authorization happens at the boundary and is propagated "
        "with integrity through the whole request — including async paths. The AI consumes claims, "
        "never issues them.")

    s = d.content_slide("Network, egress, encryption & keys", "D6-04 / D6-05")
    two_col(d, s,
            "Segmentation & egress", [
                "Network segmentation between zones; controlled egress.",
                "The only external egress is the masked SLM path.",
            ],
            "Encryption & key management", [
                "Encryption in transit and at rest.",
                "Keys managed in Key Vault (SPN-only access, deck 05).",
                "Token vault for masking is in-tenancy (next slide).",
            ])
    s.notes_slide.notes_text_frame.text = ("Segmented network, minimal controlled egress, encryption "
        "everywhere, keys in Key Vault. The masking token vault stays in-tenancy.")

    s = d.content_slide("Data classification & PII", "D6-06")
    d.bullets(s, [
        "Data is classified (public → confidential → special-category / children's data).",
        "PII protection policies drive masking, logging redaction and retention.",
        "Special-category data, children's personal data and secrets are the most tightly controlled.",
        "Classification decides what may reach a model and how — feeding the masking regime.",
    ], 0.9, 2.0, 11.5, 3.8, size=16, gap=14)
    s.notes_slide.notes_text_frame.text = ("Classification is the input to masking, redaction and "
        "retention decisions. Children's and special-category data get the strongest protection.")

    s = d.content_slide("SLM input masking regime", "D6-19 (PROPOSED) refines D6-07 — deck 09")
    kv_panel(d, s, "Two regimes", [
        ("External / hosted SLM", "MANDATORY mask/tokenise-all, fail-closed — no raw PII/records egress"),
        ("Hard-blocked", "special-category, children's data, secrets — never sent"),
        ("Self-hosted SLM", "raw OR masked, per task class (stays in-tenancy)"),
        ("Token vault", "reversible re-identification inside the boundary"),
    ], 0.9, 1.95, 6.4, 4.4, col=YELLOW)
    d.bullets(s, [
        "Strengthens D6-07 from 'minimise & redact' into a testable, binary default.",
        "External boundary fails closed if it cannot verify masking.",
        "Awaiting ARB sign-off (DPO owner, DPIA update) + Phase 20 vault sizing.",
    ], 7.5, 2.1, 4.9, 4.2, size=14, gap=13)
    s.notes_slide.notes_text_frame.text = ("The headline security decision for ARB: nothing raw leaves "
        "the tenancy to an external model — everything is masked/tokenised, special classes hard-blocked, "
        "fail-closed. Self-hosted may use raw data since it never crosses the boundary. A reversible "
        "token vault re-identifies masked outputs in-tenancy. Proposed; needs DPO/DPIA sign-off.")

    s = d.content_slide("Guardrail pipeline", "D6-09 · at every boundary")
    guardrail_pipeline(d, s)
    s.notes_slide.notes_text_frame.text = ("Guardrails are placed at input, context, prompt, tool, "
        "model and output boundaries — middleware, not a single filter. No path reaches the model or "
        "user unchecked.")

    s = d.content_slide("Prompt-injection & jailbreak defence", "D6-08")
    d.bullets(s, [
        "Untrusted content (user text, RAG documents, tool output) is treated as data, never as instructions.",
        "Defence is layered: prompt/security layer (deck 03) + guardrail pipeline (this deck).",
        "Attempts to redirect the agent, escalate access, or exfiltrate data are detected and blocked.",
        "Suspicious redirection escalates to a human rather than being silently followed.",
    ], 0.9, 2.0, 11.5, 3.8, size=16, gap=14)
    s.notes_slide.notes_text_frame.text = ("Injection defence is defence-in-depth: quarantine untrusted "
        "content, layered detection in the prompt layer and guardrails, escalate rather than obey.")

    s = d.content_slide("Tool, MCP & RAG security", "D6-10 / D6-11 / D6-12")
    two_col(d, s,
            "Tool & MCP", [
                "Tools allow-listed per agent; parameters & outputs validated.",
                "MCP servers carry an explicit trust model — no implicit trust.",
                "Only registered, approved servers/tools are callable.",
            ],
            "RAG ACL enforcement", [
                "Retrieval is ACL-enforced — users only see documents they may see.",
                "ACLs applied at query time, not post-filtered.",
                "Citations respect the same access scope.",
            ])
    s.notes_slide.notes_text_frame.text = ("Tools and MCP servers are allow-listed and trust-modelled; "
        "RAG enforces document ACLs at retrieval so knowledge never leaks across authorization scopes.")

    s = d.content_slide("Responsible AI & human oversight", "D6-13 / D6-14")
    two_col(d, s,
            "Responsible AI & prohibited use", [
                "Explicit prohibited-use policy.",
                "No invented business rules, outcomes, URLs, IDs or technical details.",
                "Fairness, transparency and accountability by design.",
            ],
            "Human oversight & HIL governance", [
                "HIL touchpoints are governed, not ad-hoc (deck 01/02).",
                "Humans confirm state-changing actions.",
                "Oversight is auditable.",
            ])
    s.notes_slide.notes_text_frame.text = ("Responsible-AI guardrails plus governed human oversight. "
        "Prohibited uses are explicit; humans stay in control of state-changing actions.")

    s = d.content_slide("GDPR, safeguarding & audit", "D6-16 / D6-17")
    two_col(d, s,
            "GDPR & safeguarding", [
                "GDPR compliance; children's data specially protected (safeguarding).",
                "DPIA maintained; masking regime feeds it (deck 09).",
                "Retention & erasure policies applied.",
            ],
            "Audit & evidential record", [
                "Auditable, evidential logging of decisions & actions.",
                "Correlation IDs tie conversation → workflow → enterprise call.",
                "Logs are redacted per classification (deck 07).",
            ])
    s.notes_slide.notes_text_frame.text = ("GDPR and safeguarding are first-class; an evidential audit "
        "record links every step. Children's data protection is explicit and drives the DPIA.")

    s = d.content_slide("Change governance & standards", "D6-15 / D6-18")
    two_col(d, s,
            "Change governance & release gates", [
                "Security-relevant changes pass release gates.",
                "Immutable versioned bundles; no in-place prod change.",
                "Ties to CI/CD quality gates (deck 07).",
            ],
            "Standards conformance", [
                "Conformance to applicable enterprise & regulatory standards.",
                "Evidenced and reviewed.",
                "Part of ARB governance (D0).",
            ])
    s.notes_slide.notes_text_frame.text = ("Change is governed through release gates; the platform "
        "conforms to applicable standards, evidenced and reviewed under ARB governance.")

    adr_index_slides(d, "ADR index — Security & Governance (D6)", adrs_for(6),
                     notes="All 19 security & governance ADRs. One is Proposed (◆): D6-19 SLM input "
                           "masking regime (deck 09), which refines the external-SLM data boundary D6-07.")

    d.final_slide("Security & governance — summary",
                  "Zero-trust · AI never authorizes · mask-all to external models · guardrails everywhere · fully audited",
                  notes="Takeaway: defence-in-depth around an absolute boundary — the AI never decides "
                        "or authorizes, nothing raw leaves the tenancy, and everything is audited.")

    d.save(OUT)
    print("saved", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    build()
