## ADDED Requirements

### Requirement: Dependency declarations remain coherent across maintained package surfaces
The maintained project MUST keep runtime and development dependency declarations synchronized across the package metadata and auxiliary dependency files that are still supported.

#### Scenario: Auditing dependency declarations
- **GIVEN** dependency versions or package lists are declared in more than one maintained file
- **WHEN** the closeout pass reviews dependency strategy
- **THEN** the repository MUST define one coherent declaration model or keep mirrored files intentionally synchronized
- **AND** redundant or misleading dependency declarations MUST be removed or updated

### Requirement: The maintained runtime surface is intentionally limited
Only documented CLI entry points, runtime resources, and actively supported code paths MUST be presented as maintained behavior for the classifier product.

#### Scenario: Reviewing a documented runtime path
- **GIVEN** a user-facing command, configuration path, or resource-loading path is documented
- **WHEN** the runtime audit validates that behavior
- **THEN** the path MUST work with the maintained packaging and repository layout
- **AND** unsupported historical paths MUST not remain documented as supported behavior

## Correctness Properties

- Dependency declarations do not contradict the shipped package surface.
- Documented runtime paths reflect tested behavior.
- The product surface stays focused on maintained entry points.
