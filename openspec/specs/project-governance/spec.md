## Requirements

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

#### Scenario: Branch management for stable maintenance
- **GIVEN** the project is in stable maintenance phase
- **WHEN** checking the Git repository structure
- **THEN** only the master/main branch MUST exist
- **AND** all feature branches MUST be deleted after merge
- **AND** no zombie branches MUST remain in remote repository

### Requirement: AI instruction files stay synchronized
All maintained AI instruction files MUST communicate the same repository workflow, architecture summary, and closeout constraints without conflicting process rules.

#### Scenario: Tool instruction parity
- **GIVEN** multiple AI instruction files exist in the repository
- **WHEN** they describe workflow or repository conventions
- **THEN** they MUST agree on OpenSpec-first governance, direct-push operation, and the authoritative project surface

#### Scenario: Copilot instructions are ignored
- **GIVEN** `.github/copilot-instructions.md` exists
- **WHEN** the project is cleaned for final closeout
- **THEN** the file MUST remain in `.gitignore` (already configured)
- **AND** it MUST NOT be tracked in version control

### Requirement: Final closeout work proceeds through one umbrella change with ordered phases
The repository MUST allow a final closeout initiative to run as one umbrella OpenSpec change, provided its internal tasks preserve explicit phase ordering and dependency tracking.

#### Scenario: Executing the final closeout initiative
- **GIVEN** the maintainer is performing the final repository-wide closeout pass
- **WHEN** they create the governing OpenSpec change
- **THEN** the work MAY be organized under one umbrella change
- **AND** the change MUST define phase order, task dependencies, and archive criteria clearly enough for handoff

#### Scenario: Repository closeout completion
- **GIVEN** final closeout tasks are completed
- **WHEN** the maintainer verifies the repository state
- **THEN** no runtime data files MUST be tracked in version control
- **AND** no obsolete documentation MUST remain in the repository
- **AND** Git repository MUST be in clean state with single master branch

### Requirement: Lightweight review is defined for direct-push maintenance
Governance documents MUST explain how `/review` or equivalent review steps are used in a single-maintainer direct-push workflow without reintroducing PR-first process overhead.

#### Scenario: Maintainer reaches a logical checkpoint
- **GIVEN** the repository is operated in direct-push mode by a single maintainer
- **WHEN** a logical chunk of closeout work is ready for verification
- **THEN** the workflow MUST define a lightweight review step before or around push/archive decisions
- **AND** that review guidance MUST remain compatible with the default non-PR workflow

## Correctness Properties

- There is exactly one active specification workflow.
- Governance docs do not require PR-first behavior for normal maintenance.
- AI tools receive compatible repository instructions.
- One umbrella closeout change does not imply unordered execution.
- Review remains present as quality control without becoming a branching ritual.
- Handoff expectations are explicit enough for a follow-up model or maintainer.
- All zombie branches have been removed from the remote.
- No runtime data or temporary files are tracked in version control.
- Documentation reflects current project state without obsolete artifacts.
