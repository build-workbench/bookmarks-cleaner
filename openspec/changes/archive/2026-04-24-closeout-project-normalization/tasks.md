## 1. Governance normalization

- [x] 1.1 Rewrite `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md` so they all reference `openspec/` as the sole active workflow and describe the single-maintainer direct-push model.
- [x] 1.2 Retire PR-first and legacy-spec guidance by removing or replacing `.github/pull_request_template.md`, `QWEN.md`, `CLAUDE.local.md`, and stale `.claude/commands/opsx/*` references to `/specs/`.

## 2. Spec and docs surface pruning

- [x] 2.1 Retire or reduce legacy `specs/` content and placeholder OpenSpec capabilities (`api`, `database`) so only maintained capability surfaces remain.
- [x] 2.2 Remove or consolidate low-value root docs and changelog material, leaving a small maintained repository entry surface.
- [x] 2.3 Prune the VitePress information architecture to a concise landing-oriented docs surface with only maintained guides and references.

## 3. Engineering baseline rationalization

- [x] 3.1 Audit `pyproject.toml`, requirements files, and package entry points; fix any mismatches between declared packages and the actual source tree. Verify with `pytest -q tests/test_runtime_paths.py`.
- [x] 3.2 Add or update project-level editor and AI tool guidance (`.editorconfig`, `.vscode/*`, `.github/copilot-instructions.md`, relevant Claude settings) so maintained tooling is explicit and consistent.
- [x] 3.3 Simplify pre-commit and helper scripts so local verification guidance matches the maintained closeout workflow.

## 4. GitHub operations simplification

- [x] 4.1 Rebuild `.github/workflows/` so required checks fail loudly, stale/noise automation is removed, and Pages/release behavior matches the maintained product.
- [x] 4.2 Tune repository automation metadata (`dependabot.yml`, repo description/homepage/topics, outstanding low-value PR residue) for a single-maintainer low-noise model.

## 5. Public project presentation

- [x] 5.1 Rewrite `README.md` and `README.zh-CN.md` into concise canonical repository entry points that match the maintained product story.
- [x] 5.2 Rebuild the GitHub Pages landing experience (`docs/index.md`, locale homepages, theme/config assets) so it sells the project clearly without mirroring a sprawling docs tree.

## 6. Runtime stabilization and closeout verification

- [x] 6.1 Audit runtime/resource loading, packaging paths, and CLI entry behavior; fix validated defects in code or tests uncovered during the closeout sweep.
- [x] 6.2 Update affected tests/docs/spec references and run the maintained verification set (`pytest -q`, targeted runtime tests, and any enforced workflow-equivalent checks) until the repository reflects the new closeout baseline.
