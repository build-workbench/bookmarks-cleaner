# Capability: Classification Feedback Loop

## Overview

Offline-first review export/import, incremental training, and optional audit workflows for low-confidence bookmark classifications.

## Requirements

### Requirement: Low-confidence results can be exported for offline review
The system MUST support exporting low-confidence classification outcomes into a deterministic offline review artifact that can be inspected and edited without external services.

#### Scenario: Review artifact is generated
- **GIVEN** a bookmark processing run produces low-confidence or abstained results
- **WHEN** the maintainer requests review export
- **THEN** the runtime MUST generate a local review artifact containing the bookmark identity, predicted category, confidence, and available alternatives
- **AND** the artifact MUST be usable without a database or network service

### Requirement: Reviewed feedback can be imported and applied locally
The system MUST support importing reviewed classification feedback from the offline review artifact format and applying the corrected labels to the maintained feedback pipeline.

#### Scenario: Reviewed labels are applied
- **GIVEN** a maintainer has edited or approved an exported review artifact
- **WHEN** the feedback import/apply flow runs
- **THEN** the corrected labels MUST be ingested into the local feedback pipeline
- **AND** the system MUST preserve enough metadata to associate the feedback with the original bookmark item

### Requirement: Incremental training remains versioned and rollback-safe
The system MUST support local incremental training from approved feedback while preserving model version history and rollback behavior.

#### Scenario: Incremental update uses approved feedback
- **GIVEN** approved feedback samples are available locally
- **WHEN** the maintainer triggers incremental training
- **THEN** the incremental trainer MUST create or update a versioned local model artifact
- **AND** the previous version MUST remain recoverable through the maintained rollback path

### Requirement: Feedback data can be audited without changing the maintained baseline install
The system MUST support an optional offline audit path for reviewed/training data quality, and MUST keep that audit tooling outside the required baseline runtime when optional dependencies are absent.

#### Scenario: Optional audit tooling is present
- **GIVEN** optional audit dependencies are installed
- **WHEN** the maintainer runs the feedback-data audit flow
- **THEN** the system MUST analyze local reviewed/training data for quality issues using the optional audit path
- **AND** the results MUST be emitted as a local offline report or artifact

#### Scenario: Optional audit tooling is absent
- **GIVEN** optional audit dependencies are not installed
- **WHEN** the maintainer requests the feedback-data audit flow
- **THEN** the system MUST fail gracefully with a clear maintained message or skip path
- **AND** the rest of the maintained runtime MUST remain usable

## Correctness Properties

- Review artifacts are deterministic, local, and service-free.
- Imported feedback remains attributable to the original bookmark item.
- Incremental training preserves rollback safety.
- Optional audit tooling never becomes mandatory for the maintained baseline workflow.
