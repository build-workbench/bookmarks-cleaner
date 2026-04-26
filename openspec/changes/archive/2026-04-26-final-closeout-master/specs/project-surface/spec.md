## ADDED Requirements

### Requirement: Generated documentation assets are not maintained as source
The repository MUST NOT treat generated documentation outputs or installed documentation dependencies as maintained source artifacts when those assets can be reproduced from committed source files.

#### Scenario: Reviewing tracked docs build artifacts
- **GIVEN** the repository contains generated docs output or installed docs dependencies
- **WHEN** the project surface is normalized for final closeout
- **THEN** reproducible generated assets MUST be removed from tracked source
- **AND** the maintained docs surface MUST be defined by source markdown, theme config, and required static assets only

### Requirement: Public docs stay intentionally small and current
The maintained docs site MUST keep only pages that serve the product landing story, essential usage guidance, or active reference material for the shipped CLI.

#### Scenario: Evaluating a deep documentation page
- **GIVEN** a docs page exists outside the essential landing, guide, or reference surface
- **WHEN** the closeout review evaluates whether it should remain
- **THEN** the page MUST be retained only if it documents maintained behavior with clear user value
- **AND** stale, redundant, or weak-signal pages MUST be removed or replaced with a short breadcrumb

## Correctness Properties

- The docs source tree contains maintainable source, not large reproducible build outputs.
- Pages content stays aligned with active product messaging.
- Deep pages exist only when they still explain maintained behavior.
