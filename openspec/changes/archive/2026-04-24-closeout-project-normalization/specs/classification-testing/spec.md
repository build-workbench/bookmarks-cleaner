## ADDED Requirements

### Requirement: Required verification commands are explicit
The project MUST define a minimal maintained verification set for closeout work, and governance docs plus automation MUST reference the same commands.

#### Scenario: Maintainer runs verification
- **GIVEN** a maintainer prepares to push a closeout change
- **WHEN** they consult project instructions or CI configuration
- **THEN** the documented required verification commands MUST match the enforced automation

### Requirement: Required checks do not soft-pass
Testing and quality-check automation MUST NOT use intentional soft-pass patterns for required commands.

#### Scenario: Static analysis failure
- **GIVEN** a required lint, type, security, or test command reports an error
- **WHEN** the automation runs
- **THEN** the affected workflow or local verification step MUST report failure
- **AND** the repository MUST not advertise the check as passing

## Correctness Properties

- Verification instructions and CI stay aligned.
- Required checks surface real failures instead of success-shaped output.
