## ADDED Requirements

### Requirement: Hybrid similarity infrastructure remains optional and offline-safe
The bookmark-classifier runtime MUST support ANN-assisted similarity operations when optional acceleration dependencies are available, and MUST fall back to deterministic local search when they are not.

#### Scenario: ANN acceleration is used when available
- **GIVEN** the maintained runtime has an initialized ANN-backed feature store
- **WHEN** the classifier or deduplication flow requests nearest-neighbor similarity results
- **THEN** the runtime MUST use the ANN-backed search path
- **AND** the returned results MUST remain compatible with the existing local feature-store contract

#### Scenario: Fallback remains available without ANN dependencies
- **GIVEN** optional ANN dependencies are not installed or ANN initialization fails
- **WHEN** the classifier or deduplication flow requests nearest-neighbor similarity results
- **THEN** the runtime MUST fall back to the existing deterministic local search behavior
- **AND** the maintained CLI path MUST continue to function without requiring the optional dependency

### Requirement: Embedding-based classification augments the rules-first ensemble
The bookmark-classifier runtime MUST allow embedding-based classification to contribute to final ensemble decisions when its backend is available, while preserving the maintained rules-first decision strategy.

#### Scenario: Embedding classifier contributes as a secondary signal
- **GIVEN** the embedding backend is configured and initialized successfully
- **WHEN** a bookmark is classified through the maintained runtime path
- **THEN** the embedding-based classifier MUST be allowed to contribute to the ensemble result
- **AND** the runtime MUST preserve rules-first weighting so embedding output does not replace rule matches as the primary strategy

#### Scenario: Embedding backend is unavailable
- **GIVEN** the embedding backend is not installed, not configured, or cannot initialize
- **WHEN** a bookmark is classified through the maintained runtime path
- **THEN** the runtime MUST continue using the remaining maintained classification methods
- **AND** the classification flow MUST not fail solely because the optional embedding backend is unavailable

### Requirement: Final classification confidence is calibrated before abstention and reporting
The bookmark-classifier runtime MUST calibrate final confidence before applying abstention/review thresholds and before surfacing confidence-driven reporting output.

#### Scenario: Calibrated confidence drives abstention
- **GIVEN** multiple classification signals produce a final ensemble result
- **WHEN** the runtime decides whether to keep the predicted category or mark the bookmark as unclassified
- **THEN** that decision MUST be based on the calibrated final confidence value
- **AND** the calibrated value MUST remain within the normative confidence range of `0.0` to `1.0`

#### Scenario: Calibrated confidence is exposed in maintained reporting
- **GIVEN** the runtime exports maintained processing statistics or confidence-driven output
- **WHEN** a classification run completes
- **THEN** the exported reporting surface MUST reflect calibrated confidence behavior rather than raw uncalibrated ensemble scores alone

## Correctness Properties

- Optional acceleration layers do not become mandatory runtime dependencies.
- Rules-first classification remains the maintained product contract.
- Confidence-based abstention uses one consistent calibrated decision value.
