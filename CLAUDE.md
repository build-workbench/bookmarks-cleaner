# CLAUDE.md

This file provides repository-specific guidance for Claude Code.

## First Principles

- Treat `openspec/` as the only active specification system.
- Optimize for the **current maintained CLI**, not for future platform expansion.
- Default to the **single-maintainer direct-push** workflow.
- Keep the repository surface small, specific, and low-noise.

## Required Workflow

For any non-trivial change:

1. `/opsx:explore`
2. `/opsx:propose`
3. `/opsx:apply`
4. `/opsx:archive`

Only work on one change at a time. Do not rely on legacy `/specs` paths, PR-first review rituals, or redundant planning documents.

## What to Preserve

- `cleanbook` remains the canonical packaged CLI entry point.
- The bookmark processing pipeline stays rules-first, ML-assisted, and LLM-optional.
- Public docs stay aligned with actual supported behavior.
- CI and verification must fail loudly on real errors.

## What to Avoid

- Adding API/database scope during closeout
- Reintroducing generic or duplicated AI instructions
- Expanding docs just to look comprehensive
- Soft-failing checks with `|| true` for required validation

## High-Value Files

- `main.py`
- `pyproject.toml`
- `config.json`
- `src/bookmark_processor.py`
- `src/ai_classifier.py`
- `src/plugins/`
- `src/services/`
- `openspec/specs/`
- `openspec/changes/`
- `docs/.vitepress/`

## Verification Baseline

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

If a change touches packaging, workflows, or developer tooling, align local verification with the maintained CI configuration before pushing.
