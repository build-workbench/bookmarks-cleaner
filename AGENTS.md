# AGENTS.md

## Project Phase

CleanBook is in a **closeout and stabilization** phase. The goal is to finish the current CLI product cleanly, reduce maintenance noise, and leave the repository in a coherent archive-ready state. Avoid speculative expansion.

## Canonical Workflow

This repository uses **OpenSpec** as the only active specification workflow.

1. `/opsx:explore` — clarify the problem and inspect the current state
2. `/opsx:propose` — create or update the change artifacts
3. `/opsx:apply` — implement tasks from the change
4. `/opsx:archive` — archive the change after implementation is complete

Use **one change at a time**. The default maintainer workflow is **direct push on the default branch**. Temporary branches or worktrees are optional tools for risky refactors, not a required process step.

## Authoritative Paths

- `openspec/config.yaml` — OpenSpec schema rules
- `openspec/specs/` — persistent capability requirements
- `openspec/changes/` — active changes
- `openspec/changes/archive/` — completed changes

Do not recreate a legacy `specs/` workflow surface.

## Closeout Guardrails

- Do not introduce a REST API or database layer as part of closeout work.
- Do not reintroduce PR-first guidance into docs or tooling.
- Do not expand the docs surface without a specific maintained purpose.
- Prefer fewer, trustworthy workflows and checks over noisy automation.
- Keep README and GitHub Pages aligned with the maintained product story.

## Product Boundaries

CleanBook is an **offline-first bookmark cleaning and classification CLI**:

- **Primary entry points**: `cleanbook`, `python main.py`
- **Core inputs**: browser bookmark HTML exports
- **Core outputs**: cleaned bookmark HTML, JSON data, markdown/report-style outputs
- **Classification stack**: rules first, ML assisted, optional LLM integration

## Architecture Snapshot

```text
CLI / main.py
  -> BookmarkProcessor
  -> AI classifier orchestration
  -> Plugin pipeline (rule / ML / embedding / LLM)
  -> Services (feature store, taxonomy, performance, etc.)
```

Keep packaging metadata, runtime resource loading, and documented entry points aligned with this structure.

## Verification Baseline

Use the smallest verification set that still gives trustworthy signal:

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

If you touch workflow-equivalent tooling, also run the enforced local format/lint/type commands that match the maintained CI configuration.

## Maintained Conventions

- Type hints throughout
- Docstrings for public APIs
- `logging.getLogger(__name__)` instead of `print`
- Mixed Chinese/English comments and docs are acceptable when they add clarity
- Project-specific guidance should live in a small set of maintained instruction files, not in duplicate AI documents
