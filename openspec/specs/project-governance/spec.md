## ADDED Requirements

### Requirement: OpenSpec is the sole active specification workflow
The repository MUST treat `openspec/` as the only normative specification system for planning, proposal, implementation, and archival workflows.

#### Scenario: Governance documents point to one source of truth
- **GIVEN** a maintainer reads project workflow documentation
- **WHEN** the documentation references specifications or change management
- **THEN** it MUST point to `openspec/`
- **AND** it MUST NOT instruct contributors to use legacy `specs/` as an active workflow

### Requirement: Governance instructions fit a single-maintainer direct-push model
Project governance documents MUST describe a single-maintainer workflow that defaults to direct pushes on the default branch, with temporary branches or worktrees documented only as optional risk-management tools.

#### Scenario: Development workflow description
- **GIVEN** a maintainer follows AGENTS or tool instruction files
- **WHEN** they read the implementation workflow
- **THEN** the default sequence MUST be `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, review, verify, direct push, archive
- **AND** pull-request-only steps MUST NOT be required

### Requirement: AI instruction files stay synchronized
All maintained AI instruction files MUST communicate the same repository workflow, architecture summary, and closeout constraints without conflicting process rules.

#### Scenario: Tool instruction parity
- **GIVEN** multiple AI instruction files exist in the repository
- **WHEN** they describe workflow or repository conventions
- **THEN** they MUST agree on OpenSpec-first governance, direct-push operation, and the authoritative project surface

## Correctness Properties

- There is exactly one active specification workflow.
- Governance docs do not require PR-first behavior for normal maintenance.
- AI tools receive compatible repository instructions.
