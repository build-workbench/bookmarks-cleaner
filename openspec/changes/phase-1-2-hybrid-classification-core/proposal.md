## Why

CleanBook already ships the maintained CLI path for rules-first bookmark processing, but several higher-value capabilities remain only partially wired: ANN-backed similarity search, richer local embedding support, calibrated confidence handling, and the low-confidence review / incremental learning loop. Bringing these into the maintained runtime now improves quality and trust without expanding the product beyond its offline-first CLI boundary.

## What Changes

- Wire ANN-backed similarity search into the existing feature store with graceful fallback when optional ANN dependencies are unavailable.
- Strengthen local embedding runtime support and connect embedding-based classification into the maintained ensemble path without replacing the current rules-first orchestration.
- Calibrate final classification confidence and expose benchmark / calibration verification for the maintained runtime.
- Add a lightweight offline review queue, feedback import/application, incremental training flow, and dataset audit path for classification feedback.
- Keep all new heavy capabilities optional and file-based; do not introduce a service, database, or web application surface.

## Non-goals

- Refactoring the maintained runtime to use the plugin pipeline as its primary orchestration layer.
- Replacing rules-first classification with embedding-first or LLM-first routing.
- Introducing always-on web fetching, archiving, or hosted/vector-database infrastructure.
- Expanding the project into a multi-user or web product.

## Capabilities

### New Capabilities
- `classification-feedback-loop`: Offline review queue export/import, labeled feedback application, incremental training, and optional dataset-audit workflows for low-confidence bookmark classifications.

### Modified Capabilities
- `bookmark-classifier`: Add ANN-assisted similarity support, stronger local embedding integration, calibrated confidence handling, and maintained CLI/runtime behavior for the hybrid classification core.
- `classification-testing`: Extend verification requirements to cover ANN fallback behavior, calibrated confidence/reporting, embedding-based ensemble behavior, and feedback-loop regression coverage.

## Impact

- Affected code: `main.py`, `src/bookmark_processor.py`, `src/ai_classifier.py`, `src/services/feature_store.py`, `src/services/embedding_service.py`, `src/services/confidence_calibrator.py`, `src/services/active_learning.py`, `src/services/incremental_trainer.py`, selected CLI modules, and targeted tests under `tests/`.
- Dependencies: optional ANN and data-audit dependencies may be added, but must remain non-mandatory for the maintained baseline install.
- Specs: modifies `openspec/specs/bookmark-classifier/spec.md` and `openspec/specs/classification-testing/spec.md`, and adds `openspec/specs/classification-feedback-loop/spec.md`.
