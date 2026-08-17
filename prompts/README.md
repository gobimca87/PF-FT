# Prompts

This directory holds the versioned prompt artifacts described by doc 16
(`MD files/4 AI/16.PF-FT-AI-PROMPT-ENGINEERING.md`, Phase 10 of `DEVELOPMENT-GUIDE.md`).
`MD files/` stays the read-only source of truth for *what a prompt must contain*; this
directory is the actual implementation.

## Composition order (doc 16 §20/§23)

System → Security → Persona → Task → Tool Instructions → ERC → RAG → Memory → API Results →
User Request → Output Contract

## Trust tiers (doc 16 §6)

- **TRUSTED** — system, security, approved application instructions, controlled tool contracts
- **CONTROLLED** — persona, workflow task, output schema
- **UNTRUSTED DATA** — user input, retrieved documents, enterprise API text fields, event
  payloads, external content — never promoted to trusted instructions

## Folder → phase/doc map

| Folder | Governs | Phase | Doc |
|---|---|---|---|
| `system/` | platform-wide TRUSTED instructions | 10 | 16 |
| `security/` | guardrail/injection-defense instructions | 11 | 18 |
| `persona/` | per-agent role + communication style (CONTROLLED) | 10 | 16 |
| `task/` | per-scenario task instructions | 10 | 16 |
| `context/` | ERC/RAG/memory/API context injection | 5, 6, 7, 8 | 8, 9, 10, 13 |
| `tools/` | tool/API/MCP instruction prompts | 6 | 10 |
| `output/` | output contract / response schemas | 10+ | 16 |
| `few-shot/` | worked dialogue examples | 10 | 16 |
| `evaluation/` | golden-dataset-linked prompt evaluation notes | 16 | 21 |
| `schemas/` | `output_schema` definitions referenced by task prompts | 10 | 16 |

Every artifact follows doc 16 §168's recommended schema (`id, version, type, status, owner,
risk, compatibility, variables, template`) and starts at `status: DRAFT` per the lifecycle in
doc 16 §34 (`DRAFT → TESTING → APPROVED → ACTIVE → DEPRECATED → RETIRED → BLOCKED`) — nothing
here is production-active until it's been evaluated and approved.

## The Adam AI persona

The mandatory persona rules live in `CLAUDE.md` ("Adam AI Persona & Conversational Style") —
that's the canonical, development-time governance spec. `persona/affiliation/affiliation.assistant.persona.yaml`
is the concise runtime implementation of those rules for the Affiliation Assistant.
`MD files/Examples/SampleWorkflowchat.md` remains the canonical tone reference — compare new
persona/prompt behavior against it before considering it aligned with the project.
