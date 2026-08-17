# 1. Record architecture decisions

Date: 2026-08-16

## Status

Accepted

## Context

Several implementation choices are deliberately left open by the `MD files/` spec set
(vector store, memory/cache store, IaC tool, manifest tool, deployment strategy — see
`DEVELOPMENT-GUIDE.md` §2) and others get decided as build phases are reached. These need
a durable, reviewable record.

## Decision

We use Architecture Decision Records (ADRs) in this directory, one file per decision,
numbered sequentially, following Michael Nygard's format (Title / Date / Status / Context /
Decision / Consequences).

## Consequences

Every deferred or reconciliation decision from `DEVELOPMENT-GUIDE.md` §2 gets its own ADR
when it is actually made — not guessed ahead of time. `0003-deferred-decisions-log.md` tracks
which ones are still open.
