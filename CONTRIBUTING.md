# Contributing to CleanBook

CleanBook is a small repository in a **closeout and stabilization** phase. Contributions are welcome when they improve the maintained CLI, documentation surface, or repository health without reopening broad product scope.

## Start Here

1. Read `AGENTS.md` for the repository workflow.
2. Use `openspec/` as the only active specification system.
3. Work on one change at a time.

## Development Workflow

For any non-trivial change, follow:

1. `/opsx:explore`
2. `/opsx:propose`
3. `/opsx:apply`
4. `/opsx:archive`

The maintainer workflow defaults to **direct pushes on the default branch**. Temporary branches or worktrees are optional isolation tools, not a required norm.

## Scope Rules

Good contributions for this phase:

- runtime or packaging fixes
- docs cleanup with a clear maintained purpose
- workflow and CI simplification
- fixes that reduce maintenance cost or clarify the product story

Out of scope unless explicitly requested:

- new API layers
- database work
- speculative feature expansion
- adding redundant docs or automation

## Verification

Use the maintained verification baseline:

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

If you touch formatting, linting, typing, or workflow configuration, run the matching local commands used by the maintained CI setup.

## Documentation Rules

- `openspec/specs/` is the requirements source of truth.
- README is the canonical repository entry point.
- GitHub Pages should remain a concise landing surface, not a mirror of every markdown file.
- Remove or consolidate stale docs instead of layering new duplicates on top.

## Reporting Problems

When reporting a bug or proposing a cleanup:

- describe the current behavior
- explain why it is incorrect or high-maintenance
- include a reproduction path if runtime behavior is affected
- point to the relevant spec, workflow file, or doc if process drift is involved
