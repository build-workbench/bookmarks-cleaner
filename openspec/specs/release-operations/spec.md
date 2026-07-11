## ADDED Requirements

### Requirement: Quality automation fails loudly
Repository automation MUST fail when validation commands fail and MUST NOT intentionally mask failures in required closeout checks.

#### Scenario: CI command failure
- **GIVEN** a required validation command exits non-zero
- **WHEN** the CI workflow runs
- **THEN** the workflow job MUST fail
- **AND** the failure MUST be visible in the workflow result

### Requirement: GitHub automation stays low-noise
The repository MUST keep only automation that serves the maintained CLI closeout model and MUST remove or disable workflows that create maintenance noise without meaningful value.

#### Scenario: Workflow portfolio review
- **GIVEN** GitHub workflow files exist in the repository
- **WHEN** their purpose is evaluated
- **THEN** only workflows that support verification for the maintained product MUST remain

### Requirement: Repository metadata is maintained from the product surface
Repository description, homepage, and topics MUST match the maintained README story.

#### Scenario: GitHub repository presentation
- **GIVEN** the repository is viewed on GitHub
- **WHEN** a visitor reads the repository metadata
- **THEN** the description, homepage URL, and topics MUST accurately describe the maintained product
- **AND** topics MUST include: bookmark-manager, classification, offline-first, python-cli, machine-learning

### Requirement: GitHub repository metadata is synchronized intentionally
Repository description, homepage, and topics MUST be updated from the maintained local product surface rather than drifting independently on GitHub.

#### Scenario: Updating repository presentation
- **GIVEN** README has been normalized for the maintained CLI story
- **WHEN** the maintainer updates remote repository metadata
- **THEN** description, homepage, and topics MUST match the maintained product narrative
- **AND** the update path MUST be documented as part of repository operations

#### Scenario: Cleaning up stale remote branches
- **GIVEN** dependabot or other automation branches exist in the remote
- **WHEN** they are no longer needed for the stable maintenance phase
- **THEN** they MUST be deleted from the remote
- **AND** only the master/main branch MUST remain in the remote

### Requirement: Workflow triggers stay narrowly scoped
GitHub Actions workflows MUST use triggers and matrices that are intentionally limited to the maintained closeout surface so that CI noise stays low for a single maintainer.

#### Scenario: Reviewing an existing workflow
- **GIVEN** a workflow file exists for CI operations
- **WHEN** its trigger conditions and job matrix are evaluated
- **THEN** only triggers and combinations that serve the maintained CLI product MUST remain
- **AND** redundant or low-value automation paths MUST be removed

## ADDED Requirements

### Requirement: Version control excludes runtime artifacts
The repository MUST NOT track runtime-generated files including logs, model artifacts, test caches, and hypothesis databases.

#### Scenario: Checking .gitignore coverage
- **GIVEN** the repository is in stable maintenance
- **WHEN** checking .gitignore rules
- **THEN** the following patterns MUST be ignored: logs/, models/, .hypothesis/, .pytest_cache/, *.pyc, __pycache__/, docs/package-lock.json

#### Scenario: Repository clean state verification
- **GIVEN** the closeout tasks are complete
- **WHEN** running git status
- **THEN** no untracked runtime data files MUST appear
- **AND** no backup files MUST exist in the repository

## Correctness Properties

- Required checks never soft-pass hidden errors.
- GitHub automation is understandable by a single maintainer.
- Public repository metadata matches the maintained product narrative.
- Remote GitHub presentation matches local maintained docs.
- Workflow scope is explainable and low-noise.
- Required automation stays aligned with current project operations.
- Runtime artifacts are never tracked in version control.
- Remote repository contains only the master/main branch.
