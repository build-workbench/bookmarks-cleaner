## Requirements

### Requirement: The public documentation surface is intentionally small
The repository MUST keep a small set of maintained public-facing documents and MUST remove or retire low-value, redundant, or stale documentation that is not needed for users or maintainers.

#### Scenario: Redundant docs are pruned
- **GIVEN** multiple documents cover the same setup, workflow, or historical material
- **WHEN** the project surface is reviewed
- **THEN** one canonical maintained document MUST remain
- **AND** redundant documents MUST be removed, archived, or replaced with a brief migration breadcrumb

#### Scenario: Duplicate source files are removed
- **GIVEN** duplicate source files exist in the repository (e.g., `src/data_exporter.py` vs `src/data/exporter.py`)
- **WHEN** the project surface is normalized
- **THEN** only one version of each module MUST be retained
- **AND** the retained version MUST be in the canonical location matching `pyproject.toml` package configuration

#### Scenario: BMad Skills are removed
- **GIVEN** the repository contains 46 BMad skills unrelated to the project
- **WHEN** the project surface is cleaned
- **THEN** all `bmad-*` skills MUST be removed
- **AND** only OpenSpec-related skills (`opsx-*`) MAY be retained

### Requirement: README is the canonical repository entry point
The root README MUST present the maintained product story, supported installation paths, and links to the essential documentation surface without duplicating the entire docs site.

#### Scenario: Repository landing experience
- **GIVEN** a new visitor opens the repository
- **WHEN** they read `README.md`
- **THEN** they MUST be able to understand the product value, installation path, and where to go next
- **AND** the README MUST avoid sprawling low-signal reference content

### Requirement: GitHub Pages acts as a product landing site
The GitHub Pages site MUST present the project as a polished landing page plus essential supporting documentation rather than a raw mirror of repository markdown.

#### Scenario: Pages communicates the product clearly
- **GIVEN** a visitor opens the published Pages URL
- **WHEN** the site loads
- **THEN** it MUST present a concise product narrative, quick-start path, and links to core docs
- **AND** it MUST avoid depending on an oversized documentation information architecture

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

- Every maintained public doc has a clear owner-purpose.
- README and Pages tell a consistent product story.
- Removed docs do not leave broken primary entry points.
- The docs source tree contains maintainable source, not large reproducible build outputs.
- Pages content stays aligned with active product messaging.
- Deep pages exist only when they still explain maintained behavior.
- No duplicate source files exist in the codebase.
- All source files match the package configuration in `pyproject.toml`.
- Only project-relevant skills remain in `.claude/skills/`.
