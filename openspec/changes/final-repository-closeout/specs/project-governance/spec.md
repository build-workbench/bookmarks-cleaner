## MODIFIED Requirements

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
