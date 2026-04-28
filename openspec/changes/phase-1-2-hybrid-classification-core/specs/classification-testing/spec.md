## ADDED Requirements

### Requirement: ANN acceleration and fallback paths are both regression-tested
The test surface MUST verify both the accelerated ANN path and the maintained fallback path for similarity-based operations.

#### Scenario: ANN-backed similarity behavior is validated
- **GIVEN** ANN-backed similarity support is available in the test environment
- **WHEN** the maintained similarity path is exercised
- **THEN** targeted tests MUST verify that ANN-backed search returns compatible nearest-neighbor results
- **AND** the tests MUST confirm the maintained contract expected by classifier and deduplication callers

#### Scenario: Fallback behavior is validated without ANN support
- **GIVEN** ANN support is unavailable or disabled in the test environment
- **WHEN** the maintained similarity path is exercised
- **THEN** targeted tests MUST verify the deterministic local fallback behavior
- **AND** the maintained baseline test run MUST not depend on optional ANN tooling being installed

### Requirement: Calibrated confidence and abstention behavior are regression-tested
The test surface MUST verify calibrated confidence handling, including abstention/review routing decisions driven by calibrated values.

#### Scenario: Calibrated confidence remains bounded
- **GIVEN** the final ensemble output is calibrated before threshold evaluation
- **WHEN** targeted confidence tests run
- **THEN** the calibrated confidence value MUST remain within `0.0` to `1.0`
- **AND** threshold-driven abstention behavior MUST be validated against that calibrated value

### Requirement: Embedding-based ensemble participation is regression-tested
The test surface MUST verify that embedding-based classification contributes when available and degrades cleanly when unavailable.

#### Scenario: Optional embedding signal participates without replacing rules-first behavior
- **GIVEN** the embedding backend is available in the test environment
- **WHEN** a bookmark classification run exercises the maintained ensemble path
- **THEN** targeted tests MUST verify that embedding-based results can contribute to the ensemble
- **AND** the tests MUST confirm that rules-first behavior remains intact

#### Scenario: Missing embedding backend does not break maintained runtime tests
- **GIVEN** the embedding backend is unavailable in the test environment
- **WHEN** the maintained classification path is exercised
- **THEN** targeted tests MUST verify graceful degradation
- **AND** the maintained baseline test run MUST still pass without the optional embedding backend

### Requirement: Feedback-loop workflows are regression-tested
The test surface MUST verify review export/import, incremental training integration, and optional audit gating for the offline feedback loop.

#### Scenario: Review export/import round trip is validated
- **GIVEN** low-confidence results are exported for offline review
- **WHEN** edited feedback is re-imported
- **THEN** targeted tests MUST verify that the corrected labels are applied to the local feedback pipeline
- **AND** the round-trip artifact contract MUST remain stable

#### Scenario: Optional audit tooling is gated explicitly
- **GIVEN** the feedback-data audit path depends on optional tooling
- **WHEN** targeted audit tests run with and without that tooling
- **THEN** the optional path MUST be covered explicitly
- **AND** the maintained baseline verification set MUST stay valid without the optional audit dependency

## Correctness Properties

- Optional dependency coverage does not weaken the maintained baseline verification story.
- Calibration and abstention behavior remain observable in targeted regression tests.
- Feedback-loop artifacts stay round-trip safe under test.
