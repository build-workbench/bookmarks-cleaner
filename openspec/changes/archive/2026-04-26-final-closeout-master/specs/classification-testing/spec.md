## ADDED Requirements

### Requirement: Closeout bug fixes require targeted regression validation
Every validated bug fixed during the final closeout pass MUST be paired with targeted verification that demonstrates the corrected behavior and protects the maintained runtime surface from regression.

#### Scenario: Fixing a validated closeout bug
- **GIVEN** a runtime, packaging, workflow, or classification bug is confirmed during closeout work
- **WHEN** the maintainer implements the fix
- **THEN** they MUST run or add targeted verification covering the corrected behavior
- **AND** the change MUST not be considered complete until that verification passes

### Requirement: Workflow-equivalent local checks remain explicit
When closeout work changes workflows, packaging, or tooling, the repository MUST define the local commands that provide the same enforcement intent as the maintained CI configuration.

#### Scenario: Changing workflow-sensitive configuration
- **GIVEN** a change modifies workflow files, package metadata, or developer tooling
- **WHEN** the maintainer prepares to finish the change
- **THEN** the required local verification commands MUST be stated clearly in the repository workflow guidance or task surface
- **AND** those commands MUST stay consistent with the maintained CI baseline

## Correctness Properties

- Bug fixes are backed by concrete regression signal.
- Workflow-sensitive changes are not merged on guesswork alone.
- Local and CI verification stories stay aligned.
