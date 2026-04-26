## 1. OpenSpec baseline and repository inventory

- [x] 1.1 Audit the current repository surface (`docs/`, `.github/`, `.claude/`, `.vscode/`, `src/`, root docs) and record retain/remove/merge decisions inside this change's artifacts.
- [x] 1.2 Identify tracked generated assets and local-residue directories (including docs build output and installed docs dependencies) and define the exact cleanup scope.
- [x] 1.3 Reconcile this change's task ordering with the maintained verification anchors in `tests/test_runtime_paths.py` and the repository workflow docs.

## 2. Documentation surface pruning and GitHub Pages rebuild

- [x] 2.1 Remove tracked generated documentation artifacts that are reproducible from source, while preserving required docs source, theme config, and static assets.
- [x] 2.2 Review every maintained docs page and retire, merge, or breadcrumb weak-signal pages so the docs tree matches the final closeout information architecture.
- [x] 2.3 Rebuild `docs/index.md`, locale landing pages, and supporting theme/config content so Pages acts as a polished product landing site instead of a markdown mirror.
- [x] 2.4 Recheck `README.md`, `README.zh-CN.md`, and docs entry points for narrative consistency after the docs pruning.

## 3. Runtime, packaging, and dependency normalization

- [x] 3.1 Audit CLI entry points, runtime resource loading, and documented command paths across `main.py`, packaged `cleanbook`, and resource loaders.
- [x] 3.2 Normalize dependency declarations across `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and docs package metadata so maintained dependency sources are coherent.
- [x] 3.3 Remove or tighten misleading documented/runtime paths and repair validated packaging or resource-path defects exposed by the audit.
- [x] 3.4 Add or update targeted regression coverage for any closeout bug fixed in this group, with `tests/test_runtime_paths.py` and adjacent focused tests as the primary anchors.

## 4. GitHub operations and maintainer workflow simplification

- [x] 4.1 Review `.github/workflows/ci.yml`, `pages.yml`, and `release.yml` for trigger scope, matrix size, and low-value automation paths; simplify to the maintained minimum.
- [x] 4.2 Audit GitHub helper assets (`dependabot`, issue templates, repo metadata touchpoints) and remove or reduce items that no longer serve closeout maintenance.
- [x] 4.3 Update maintainer-facing workflow docs (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and related guidance) so the one-change closeout flow and lightweight `/review` checkpoint are explicit.
- [x] 4.4 Use `gh` to synchronize repository description, homepage, topics, and Pages URL with the finalized README/Pages story.

## 5. AI tooling, editor defaults, and project instruction minimization

- [x] 5.1 Refresh `.github/copilot-instructions.md` so it matches the final maintained CLI story, OpenSpec workflow, and closeout verification baseline.
- [x] 5.2 Audit `.claude/`, repository-scoped skills/assets, and local Claude settings; keep only repository-relevant assets and remove or reduce generic residue.
- [x] 5.3 Tighten `.vscode/` settings and extension recommendations so formatting, type analysis, and pytest execution align with the maintained Python stack without extra complexity.
- [x] 5.4 Document the MCP vs CLI skills boundary and decide whether any project-level Copilot or Opencode plugin/config is justified; default to the minimal viable surface.

## 6. Final handoff, verification, and archive

- [x] 6.1 Convert the remaining implementation work into a structured GLM handoff backlog with explicit file targets, dependencies, and acceptance boundaries.
- [x] 6.2 Run the maintained verification baseline (`pytest -q tests/test_runtime_paths.py`, `pytest -q`) plus workflow-equivalent local checks for any workflow/tooling/package changes.
- [x] 6.3 Update this change's tasks/specs/design if scope shifted during execution so the artifacts remain truthful.
- [x] 6.4 Archive the change once repository surface, verification, and handoff outputs all match the final closeout requirements.
