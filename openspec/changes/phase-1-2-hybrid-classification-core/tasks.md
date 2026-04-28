## 1. OpenSpec and dependency surface

- [x] 1.1 Add optional dependency declarations and configuration hooks for ANN acceleration and feedback-data audit tooling in the maintained packaging surface (`pyproject.toml`, config defaults), keeping the baseline install usable without them.
- [x] 1.2 Add or update runtime/config documentation touchpoints needed for the maintained CLI path so optional acceleration, calibration, and feedback-loop behavior are discoverable without widening the product story.

## 2. Phase 1 core similarity and embedding runtime

- [x] 2.1 Implement ANN-backed search in `src/services/feature_store.py` with deterministic brute-force fallback and persistence-safe behavior; cover with targeted tests for accelerated and fallback paths.
- [x] 2.2 Upgrade `src/services/embedding_service.py` runtime/config handling so optional embedding backends initialize cleanly, degrade safely, and remain compatible with existing cache behavior; cover with targeted tests for configured and unavailable backends.

## 3. Phase 1 classifier calibration and reporting

- [ ] 3.1 Wire embedding-based classification into the maintained `src/ai_classifier.py` ensemble path as an additive rules-second signal, without replacing the existing rules-first strategy; cover with targeted classifier-path tests.
- [ ] 3.2 Integrate `src/services/confidence_calibrator.py` into final confidence, abstention, and exported stats/reporting surfaces in `src/ai_classifier.py` and `src/bookmark_processor.py`; add regression tests for bounded calibrated confidence and abstention behavior.

## 4. Phase 2 offline feedback loop

- [ ] 4.1 Add a maintained offline review export path for low-confidence results in the processing/runtime flow, producing deterministic local artifacts that capture bookmark identity, confidence, and alternatives; cover round-trip-friendly artifact tests.
- [ ] 4.2 Add local feedback import/apply flow that feeds approved labels into the maintained feedback pipeline and preserves bookmark-to-feedback attribution; cover with targeted import/apply regression tests.

## 5. Phase 2 incremental learning and audit

- [ ] 5.1 Connect approved feedback into `src/services/incremental_trainer.py` through a maintained CLI/runtime path, preserving model version history and rollback behavior; cover with targeted trainer/versioning tests.
- [ ] 5.2 Add an optional offline audit command/path for feedback or training data quality that uses extra tooling only when installed and fails gracefully otherwise; cover both present/absent dependency paths in targeted tests.

## 6. Verification and completion

- [ ] 6.1 Add or update targeted regression tests under `tests/` for ANN fallback, embedding ensemble participation, calibrated confidence, review export/import, incremental training, and optional audit gating.
- [ ] 6.2 Run the maintained verification baseline (`python3 -m pytest -q tests/test_runtime_paths.py`, `python3 -m pytest -q`) plus any new targeted commands required by this change, then update OpenSpec task checkboxes and archive the change.
