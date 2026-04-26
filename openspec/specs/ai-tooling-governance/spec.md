## ADDED Requirements

### Requirement: AI instruction files remain project-specific and minimal
The repository MUST keep only AI instruction files and repository-scoped AI assets that directly support the maintained CleanBook closeout workflow, and those files MUST describe the project in concrete repository-specific terms rather than generic boilerplate.

#### Scenario: Retaining a project-scoped instruction file
- **GIVEN** an AI instruction file or repository-scoped AI asset exists in the repository
- **WHEN** the closeout audit reviews its purpose
- **THEN** it MUST be retained only if it directly supports the maintained offline-first bookmark CLI workflow
- **AND** its content MUST align with the repository's actual architecture, workflow, and closeout constraints

### Requirement: MCP and CLI skills boundaries are explicit
The repository MUST document which automation capabilities justify MCP-style integration and which capabilities MUST remain lightweight instruction files or CLI skills to reduce context and maintenance cost.

#### Scenario: Evaluating a tooling capability
- **GIVEN** a maintainer considers adding or retaining an AI automation capability
- **WHEN** the capability is classified during the tooling review
- **THEN** the repository MUST state whether it belongs in MCP, CLI skills, or plain instruction files
- **AND** the decision MUST be justified by recurring project value rather than tool novelty

### Requirement: Editor and LSP defaults match the maintained stack
Project-level editor configuration MUST support the maintained Python CLI stack with low-friction formatting, type-checking, and test execution defaults, without introducing unrelated tooling complexity.

#### Scenario: Opening the repository in a supported editor
- **GIVEN** a maintainer opens the repository with project-level editor settings enabled
- **WHEN** they use the provided defaults
- **THEN** formatting, import organization, type analysis, and pytest discovery MUST align with the maintained Python toolchain
- **AND** the configuration MUST avoid project-specific dependence on tools that are not actually maintained here

## Correctness Properties

- AI instructions describe the real repository rather than a generic coding workflow.
- Tooling decisions are explainable in terms of recurring repository needs.
- Editor defaults reduce friction without expanding scope.
