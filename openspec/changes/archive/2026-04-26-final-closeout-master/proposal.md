## Why

CleanBook has already completed an initial closeout normalization pass, but the repository still is not in a true archive-ready final state. Code surface, AI/tooling configuration, GitHub presentation, and generated documentation assets still show drift that increases maintenance cost and makes future handoff to GLM less reliable.

## What Changes

- Perform one final end-to-end closeout pass across architecture surface, docs, workflows, GitHub metadata, and AI/developer tooling.
- Remove or retire low-value generated assets, stale docs, redundant configuration, and tooling noise that do not belong in the maintained CLI end state.
- Re-audit runtime paths, packaging, CLI entry points, dependency declarations, and validated bugs so the shipped product story matches real behavior.
- Rebuild GitHub Pages and repository metadata as a polished product surface aligned with the maintained README story.
- Produce a final OpenSpec task surface that a follow-up model can execute or finish without re-discovering project context.

## Capabilities

### New Capabilities
- `ai-tooling-governance`: Defines the maintained AI instruction, editor, MCP/skills, and local tooling boundaries for the closeout-phase repository.

### Modified Capabilities
- `project-surface`: Tighten the maintained docs surface, GitHub Pages information architecture, and generated-asset rules.
- `project-governance`: Extend the single-maintainer OpenSpec workflow to cover final-closeout execution and handoff rules.
- `release-operations`: Refine CI/CD scope, GitHub metadata management, and low-noise automation requirements.
- `bookmark-classifier`: Tighten final-state runtime, packaging, dependency, and CLI coherence requirements.
- `classification-testing`: Align required verification and bug-fix validation with the final closeout baseline.

## Impact

- Affected areas: `openspec/specs/`, `openspec/changes/`, `README*`, `docs/`, `.github/`, `.claude/`, `.vscode/`, `pyproject.toml`, `requirements*.txt`, `main.py`, `src/`, and selected tests.
- External systems: GitHub repository metadata, GitHub Pages, and workflows managed through `gh` and GitHub Actions.
- Non-goals: new platform scope, API/database work, or speculative feature expansion beyond stabilizing the maintained offline-first CLI.
