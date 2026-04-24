## Why

The repository has drifted away from its intended OpenSpec-first architecture: governance docs conflict with each other, legacy specs coexist with `openspec/specs/`, CI contains false-green checks, and the public docs surface is oversized and inconsistent. The project now needs a focused closeout pass that reduces maintenance cost, restores architectural clarity, and leaves a stable single-maintainer workflow.

## What Changes

- Normalize project governance around `openspec/` as the only active specification system.
- Remove or retire low-value legacy docs, placeholder specs, redundant changelogs, and PR-first guidance that do not fit a single-maintainer direct-push workflow.
- Simplify engineering configuration, editor guidance, AI tool instructions, and GitHub automation so they reflect the actual codebase and fail loudly when quality checks break.
- Rebuild the documentation surface so README and GitHub Pages present a clear product story instead of a sprawling reference dump.
- Audit runtime, packaging, and test paths; fix validated defects found during the closeout sweep.

## Capabilities

### New Capabilities
- `project-governance`: Defines the authoritative OpenSpec-first development workflow, AI tool instructions, and single-maintainer operating rules.
- `project-surface`: Defines the required public documentation surface for README, GitHub Pages, and core contributor docs.
- `release-operations`: Defines the minimum viable GitHub automation, repository metadata, and release checks for a low-noise maintenance model.

### Modified Capabilities
- `bookmark-classifier`: Tighten packaging, runtime-path, and documentation requirements so the shipped CLI matches the maintained architecture and supported features.
- `classification-testing`: Tighten verification requirements so CI and local quality checks cannot silently pass on failures.

## Impact

- Affected areas: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.github/`, `docs/`, `README*`, `pyproject.toml`, project editor/tooling configs, and runtime/test files touched by validated bug fixes.
- Existing OpenSpec specs in `openspec/specs/` will be updated and expanded; legacy `specs/` content will be retired or reduced to migration breadcrumbs.
- GitHub Pages, repository metadata, and workflow behavior may change to reflect the new closeout model.

## Non-goals

- Adding a REST API or database layer.
- Expanding the feature set beyond what is needed to stabilize and finish the current CLI product.
- Preserving redundant documentation or automation purely for historical completeness.
