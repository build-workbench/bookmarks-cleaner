# CLAUDE.md

This file provides repository-specific guidance for Claude Code.

## First Principles

- Optimize for the **current maintained CLI**, not for future platform expansion.
- Default to the **single-maintainer direct-push** workflow.
- Keep the repository surface small, specific, and low-noise.

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
- Growing the AI/tooling surface without a concrete recurring repository need

## High-Value Files

- `main.py`
- `pyproject.toml`
- `config.json`
- `src/bookmark_processor.py`
- `src/plugins/`
- `src/services/`

## Verification Baseline

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

If a change touches packaging, workflows, or developer tooling, align local verification with the maintained CI configuration before pushing.

Prefer repository-scoped instructions/skills over new MCP or plugin layers unless the extra surface clearly pays for itself.
Default to no project-level MCP or Opencode config unless a repeated repository task cannot be handled cleanly with the maintained instruction files, skills, and ordinary CLI tooling.
