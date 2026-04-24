## ADDED Requirements

### Requirement: Supported CLI entry points remain coherent
The shipped bookmark-classifier product MUST expose only maintained CLI entry points and MUST keep packaging metadata aligned with the actual code layout.

#### Scenario: Package entry point resolution
- **GIVEN** a user installs the project from the supported distribution metadata
- **WHEN** they invoke a documented CLI entry point
- **THEN** the referenced module path MUST exist
- **AND** the entry point MUST start the maintained CLI flow

### Requirement: Runtime resources match documented behavior
The maintained classifier runtime MUST ship the configuration and resource files required by documented CLI workflows.

#### Scenario: Documented runtime path works
- **GIVEN** a user follows a documented local run command
- **WHEN** the CLI loads configuration, taxonomy, or model resources
- **THEN** required files MUST be discoverable through maintained runtime paths
- **AND** unsupported optional paths MUST not be presented as guaranteed behavior

## Correctness Properties

- Documented CLI entry points resolve to real modules.
- Runtime resource loading matches the maintained packaging surface.
