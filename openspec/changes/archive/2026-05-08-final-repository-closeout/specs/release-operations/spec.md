## MODIFIED Requirements

### Requirement: Repository metadata is maintained from the product surface
Repository description, homepage, and topics MUST match the maintained README and Pages story.

#### Scenario: GitHub repository presentation
- **GIVEN** the repository is viewed on GitHub
- **WHEN** a visitor reads the repository metadata
- **THEN** the description, homepage URL, and topics MUST accurately describe the maintained product and docs surface
- **AND** topics MUST include: bookmark-manager, classification, offline-first, python-cli, machine-learning

### Requirement: GitHub repository metadata is synchronized intentionally
Repository description, homepage, topics, and published Pages URL MUST be updated from the maintained local product surface rather than drifting independently on GitHub.

#### Scenario: Updating repository presentation
- **GIVEN** README and GitHub Pages have been normalized for the maintained CLI story
- **WHEN** the maintainer updates remote repository metadata
- **THEN** description, homepage, topics, and Pages URL MUST match the maintained product narrative
- **AND** the update path MUST be documented as part of repository operations

#### Scenario: Cleaning up stale remote branches
- **GIVEN** dependabot or other automation branches exist in the remote
- **WHEN** they are no longer needed for the stable maintenance phase
- **THEN** they MUST be deleted from the remote
- **AND** only the master/main branch MUST remain in the remote

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
