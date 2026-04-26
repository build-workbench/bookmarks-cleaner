## ADDED Requirements

### Requirement: Final closeout work proceeds through one umbrella change with ordered phases
The repository MUST allow a final closeout initiative to run as one umbrella OpenSpec change, provided its internal tasks preserve explicit phase ordering and dependency tracking.

#### Scenario: Executing the final closeout initiative
- **GIVEN** the maintainer is performing the final repository-wide closeout pass
- **WHEN** they create the governing OpenSpec change
- **THEN** the work MAY be organized under one umbrella change
- **AND** the change MUST define phase order, task dependencies, and archive criteria clearly enough for handoff

### Requirement: Lightweight review is defined for direct-push maintenance
Governance documents MUST explain how `/review` or equivalent review steps are used in a single-maintainer direct-push workflow without reintroducing PR-first process overhead.

#### Scenario: Maintainer reaches a logical checkpoint
- **GIVEN** the repository is operated in direct-push mode by a single maintainer
- **WHEN** a logical chunk of closeout work is ready for verification
- **THEN** the workflow MUST define a lightweight review step before or around push/archive decisions
- **AND** that review guidance MUST remain compatible with the default non-PR workflow

## Correctness Properties

- One umbrella closeout change does not imply unordered execution.
- Review remains present as quality control without becoming a branching ritual.
- Handoff expectations are explicit enough for a follow-up model or maintainer.
