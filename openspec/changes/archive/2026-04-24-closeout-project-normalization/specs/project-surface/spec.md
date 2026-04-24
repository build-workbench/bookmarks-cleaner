## ADDED Requirements

### Requirement: The public documentation surface is intentionally small
The repository MUST keep a small set of maintained public-facing documents and MUST remove or retire low-value, redundant, or stale documentation that is not needed for users or maintainers.

#### Scenario: Redundant docs are pruned
- **GIVEN** multiple documents cover the same setup, workflow, or historical material
- **WHEN** the project surface is reviewed
- **THEN** one canonical maintained document MUST remain
- **AND** redundant documents MUST be removed, archived, or replaced with a brief migration breadcrumb

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

## Correctness Properties

- Every maintained public doc has a clear owner-purpose.
- README and Pages tell a consistent product story.
- Removed docs do not leave broken primary entry points.
