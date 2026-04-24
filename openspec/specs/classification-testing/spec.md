# Capability: Classification Testing

## Overview

Behavior-Driven Development (BDD) test specifications for the CleanBook bookmark classification system, covering plugin registry, classifier pipeline, feature store, embedding service, active learning, and other core components.

## Requirements

### Requirement: Plugin Registry Testing
Verify plugin registration, lifecycle, and consistency.

#### Scenario: Plugin Registration
- **GIVEN** a PluginRegistry instance
- **WHEN** a valid ClassifierPlugin is registered
- **THEN** the plugin is available in the registry
- **AND** the plugin is in enabled state

#### Scenario: Duplicate Plugin Registration
- **GIVEN** a plugin named "test_plugin" already registered
- **WHEN** another plugin with the same name is registered
- **THEN** registration fails
- **AND** an error is logged

#### Scenario: Runtime Plugin Toggle
- **GIVEN** a PluginRegistry with registered plugins
- **WHEN** a plugin is disabled
- **THEN** the plugin is not returned by get_enabled_plugins
- **WHEN** the plugin is enabled again
- **THEN** the plugin is returned by get_enabled_plugins

### Requirement: Classifier Pipeline Testing
Verify ordered plugin execution and failure handling.

#### Scenario: Priority Order Execution
- **GIVEN** a ClassifierPipeline with multiple enabled plugins
- **WHEN** a bookmark is classified
- **THEN** plugins are invoked in configured priority order

#### Scenario: Plugin Failure Isolation
- **GIVEN** a ClassifierPipeline with multiple plugins
- **WHEN** one plugin fails during classification
- **THEN** the error is logged
- **AND** remaining plugins continue execution
- **AND** a result is still returned

### Requirement: Feature Store Testing
Verify caching and retrieval with TTL and LRU eviction.

#### Scenario: TTL Expiration
- **GIVEN** a FeatureStore instance
- **WHEN** a feature is stored with TTL
- **THEN** the feature is retrievable before TTL expires
- **AND** the feature is expired after TTL

#### Scenario: LRU Eviction
- **GIVEN** a FeatureStore at maximum capacity
- **WHEN** a new feature is added
- **THEN** the least recently used feature is evicted

### Requirement: Embedding Service Testing
Verify embedding generation and caching.

#### Scenario: Embedding Generation
- **GIVEN** an EmbeddingService with loaded model
- **WHEN** a bookmark title is embedded
- **THEN** a dense vector is returned
- **AND** vector dimension matches model config

#### Scenario: Embedding Cache
- **GIVEN** a BookmarkFeatureStore
- **WHEN** the same bookmark is embedded twice
- **THEN** the second embedding comes from cache

#### Scenario: TF-IDF Fallback
- **GIVEN** an EmbeddingService without Transformer model
- **WHEN** a bookmark is embedded
- **THEN** TF-IDF vectorization is used
- **AND** a valid embedding is returned

### Requirement: Active Learning Testing
Verify low-confidence detection and uncertainty sampling.

#### Scenario: Low-Confidence Detection
- **GIVEN** an ActiveLearningEngine with threshold 0.7
- **WHEN** a bookmark is classified with confidence 0.5
- **THEN** the bookmark is queued for user review

#### Scenario: Uncertainty Sampling Priority
- **GIVEN** multiple bookmarks with different confidences
- **WHEN** the engine prioritizes samples
- **THEN** lower confidence samples are prioritized first

#### Scenario: Session Request Limit
- **GIVEN** an ActiveLearningEngine with session limit 10
- **WHEN** 10 feedback requests are made
- **THEN** the 11th request is rejected

### Requirement: Incremental Trainer Testing
Verify incremental model updates and version history.

#### Scenario: Incremental Update Trigger
- **GIVEN** an IncrementalTrainer with batch size 100
- **WHEN** 100 new labeled samples are collected
- **THEN** the model is updated

#### Scenario: Model Rollback
- **GIVEN** a model updated multiple times
- **WHEN** model rollback is requested
- **THEN** a previous version is restored

### Requirement: Taxonomy Service Testing
Verify category management and propagation.

#### Scenario: YAML Taxonomy Load
- **GIVEN** a YAML taxonomy file
- **WHEN** the TaxonomyService loads it
- **THEN** the category hierarchy is available

#### Scenario: Category Rename Propagation
- **GIVEN** a category with existing classifications
- **WHEN** the category is renamed
- **THEN** all historical classifications are updated

### Requirement: Performance Monitor Testing
Verify metrics tracking and alerting.

#### Scenario: Latency Percentiles
- **GIVEN** a PerformanceMonitor instance
- **WHEN** multiple classifications are performed
- **THEN** p50, p95, p99 latencies are accurate

#### Scenario: Prometheus Export
- **GIVEN** performance data
- **WHEN** metrics are exported
- **THEN** the output is valid Prometheus format

### Requirement: Fusion Strategy Testing
Verify multi-method result combination.

#### Scenario: Weighted Voting
- **GIVEN** multiple classifier results
- **WHEN** weighted voting is applied
- **THEN** the result with highest weighted score wins

### Requirement: Required verification commands are explicit
The project MUST define a minimal maintained verification set for closeout work, and governance docs plus automation MUST reference the same commands.

#### Scenario: Maintainer runs verification
- **GIVEN** a maintainer prepares to push a closeout change
- **WHEN** they consult project instructions or CI configuration
- **THEN** the documented required verification commands MUST match the enforced automation

### Requirement: Required checks do not soft-pass
Testing and quality-check automation MUST NOT use intentional soft-pass patterns for required commands.

#### Scenario: Static analysis failure
- **GIVEN** a required lint, type, security, or test command reports an error
- **WHEN** the automation runs
- **THEN** the affected workflow or local verification step MUST report failure
- **AND** the repository MUST not advertise the check as passing

## Property Tests

| Property ID | Description |
|-------------|-------------|
| Property 1 | Plugin Registration Consistency |
| Property 2 | Plugin Invocation Order |
| Property 3 | Plugin Failure Isolation |
| Property 4 | Runtime Plugin Toggle |
| Property 5 | Embedding Dimensionality Consistency |
| Property 6 | Embedding Cache Round-Trip |
| Property 7 | Cosine Similarity Classification |
| Property 8 | Low-Confidence Detection and Queuing |
| Property 9 | Uncertainty Sampling Priority |
| Property 10 | Session Request Limit |
| Property 11 | Feedback Persistence |
| Property 12 | Incremental Update Trigger |
| Property 13 | Model Version History |
| Property 14 | Atomic Model Serialization |
| Property 15 | Fusion Strategy Application |
| Property 16 | Dynamic Weight Adjustment |
| Property 17 | Feature Store TTL Expiration |
| Property 18 | LRU Eviction Policy |
| Property 19 | Taxonomy YAML Round-Trip |
| Property 20 | Category Name Validation |
| Property 21 | Category Rename Propagation |
| Property 22 | Category Merge Completeness |
| Property 23 | Latency Percentile Accuracy |
| Property 24 | Latency Alert Emission |
| Property 25 | Prometheus Format Validity |

## Test Execution

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_plugin_registry_properties.py -v
pytest tests/test_active_learning_properties.py -v

# Run property-based tests only
pytest -m property

# Coverage report
coverage run -m pytest tests/
coverage report
```

## Test Summary

| Test File | Tests | Status |
|-----------|-------|--------|
| test_plugin_registry_properties.py | 7 | ✅ PASSED |
| test_pipeline_properties.py | 6 | ✅ PASSED |
| test_feature_store_properties.py | 8 | ✅ PASSED |
| test_active_learning_properties.py | 9 | ✅ PASSED |
| test_taxonomy_service_properties.py | 11 | ✅ PASSED |
| test_performance_monitor_properties.py | 10 | ✅ PASSED |
| test_fusion_strategy_properties.py | 7 | ✅ PASSED |
| test_incremental_trainer_properties.py | 8 | ⏭️ SKIPPED (joblib) |
| test_embedding_service_properties.py | 8 | ⏭️ SKIPPED (sentence_transformers) |
| test_embedding_classifier_properties.py | 7 | ⏭️ SKIPPED (sentence_transformers) |

**Total: 58 passed, 23 skipped**

## References

- Test files: `tests/` directory
