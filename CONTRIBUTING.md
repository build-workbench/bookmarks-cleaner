# Contributing to CleanBook

CleanBook is in a **stable maintenance** phase. The project workflow, scope rules, and verification baseline are defined in `AGENTS.md`. This file covers contribution-specific guidance only.

## Reporting Problems

When reporting a bug or proposing a cleanup:

- describe the current behavior
- explain why it is incorrect or high-maintenance
- include a reproduction path if runtime behavior is affected
- point to the relevant spec, workflow file, or doc if process drift is involved

## Documentation Rules

- `openspec/specs/` is the requirements source of truth for active changes.
- README is the canonical repository entry point.
- The docs source tree should remain a concise maintained surface, not a mirror of every markdown file.
- Remove or consolidate stale docs instead of layering new duplicates on top.
