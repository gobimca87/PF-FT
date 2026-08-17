# 2. Python version and primary type checker

Date: 2026-08-16

## Status

Accepted

## Context

`CLAUDE.md` and doc 27 (Development Standards §9, §13) require the project to pin an
explicit Python version range and select one primary type checker (mypy or pyright).

## Decision

- Python version range: `>=3.11,<3.13`.
- Primary type checker: **mypy**, run in `strict` mode with the `pydantic.mypy` plugin
  enabled (project uses Pydantic v2 at every boundary per `CLAUDE.md`).

## Consequences

- CI and local pre-commit both run `mypy src`.
- pyright is not installed or run in CI; contributors should not add pyright-specific
  ignore comments.
- Revisit if a future dependency requires a newer Python minimum that conflicts with
  `<3.13`.
