# AGENTS.md

## Project Phase

CleanBook is in a **stable maintenance** phase. The CLI product is complete and the repository is in an archive-ready state.

## Canonical Workflow

This repository uses **OpenSpec** as the only active specification workflow:

1. `/opsx:explore` — clarify the problem and inspect the current state
2. `/opsx:propose` — create or update the change artifacts
3. `/opsx:apply` — implement tasks from the change
4. `/opsx:archive` — archive the change after implementation is complete

**One change at a time.** Default to **single-maintainer direct-push** on master.

## Product Boundaries

CleanBook is an **offline-first bookmark cleaning and classification CLI**:

- **Primary entry points**: `cleanbook`, `python main.py`
- **Core inputs**: browser bookmark HTML exports
- **Core outputs**: cleaned bookmark HTML, JSON data, markdown reports
- **Classification stack**: rules first, ML assisted, optional LLM integration

## Architecture

```
CLI / main.py
  -> BookmarkProcessor
  -> classifier orchestration
  -> plugin pipeline
  -> services (feature store, taxonomy, etc.)
```

## Verification Baseline

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

## Maintained Conventions

- Type hints throughout
- Docstrings for public APIs
- `logging.getLogger(__name__)` instead of `print`
- Mixed Chinese/English comments and docs are acceptable
