# Capability: Bookmark Classifier

## Overview

The CleanBook intelligent bookmark classification system uses AI technology to automatically analyze, classify, and organize browser bookmarks through rule-based, machine learning, and AI-powered ensemble methods.

## Requirements

### Requirement: Bookmark Processing
Process browser bookmark HTML files for automatic organization into meaningful categories.

#### Scenario: HTML Input Processing
- **GIVEN** a valid HTML bookmark file
- **WHEN** the file is processed
- **THEN** bookmarks are extracted with titles, URLs, and metadata
- **AND** results are output in HTML, JSON, and Markdown formats

#### Scenario: Parallel Processing
- **GIVEN** a bookmark file with multiple entries
- **WHEN** processing is initiated
- **THEN** bookmarks are processed in parallel using multi-threading

### Requirement: Classification Configuration
Allow users to customize classification rules and categories.

#### Scenario: Custom Rules
- **GIVEN** a configuration file (config.json)
- **WHEN** users modify category rules
- **THEN** classification matches their personal organization style

#### Scenario: Category Hierarchy
- **GIVEN** a category configuration
- **WHEN** parent-child relationships are defined
- **THEN** bookmarks are organized hierarchically

### Requirement: Performance Optimization
Provide fast bookmark processing with intelligent caching.

#### Scenario: LRU Cache
- **GIVEN** repeated bookmark classifications
- **WHEN** the same URL is processed again
- **THEN** cached results are returned without recomputation

#### Scenario: Batch Processing
- **GIVEN** multiple bookmark files
- **WHEN** batch processing is initiated
- **THEN** all files are processed efficiently

### Requirement: Multiple Output Formats
Support various output formats for different use cases.

#### Scenario: HTML Output
- **GIVEN** classified bookmarks
- **WHEN** HTML output is requested
- **THEN** the result is importable to browsers

#### Scenario: JSON Output
- **GIVEN** classified bookmarks
- **WHEN** JSON output is requested
- **THEN** detailed classification metadata is included

### Requirement: Supported CLI entry points remain coherent
The shipped bookmark-classifier product MUST expose only maintained CLI entry points and MUST keep packaging metadata aligned with the actual code layout.

#### Scenario: Package entry point resolution
- **GIVEN** a user installs the project from the supported distribution metadata
- **WHEN** they invoke a documented CLI entry point
- **THEN** the referenced module path MUST exist
- **AND** the entry point MUST start the maintained CLI flow

### Requirement: Runtime resources match documented behavior
The maintained classifier runtime MUST ship the configuration and resource files required by documented CLI workflows.

#### Scenario: Documented runtime path works
- **GIVEN** a user follows a documented local run command
- **WHEN** the CLI loads configuration, taxonomy, or model resources
- **THEN** required files MUST be discoverable through maintained runtime paths
- **AND** unsupported optional paths MUST not be presented as guaranteed behavior

### Requirement: Dependency declarations remain coherent across maintained package surfaces
The maintained project MUST keep runtime and development dependency declarations synchronized across the package metadata and auxiliary dependency files that are still supported.

#### Scenario: Auditing dependency declarations
- **GIVEN** dependency versions or package lists are declared in more than one maintained file
- **WHEN** the closeout pass reviews dependency strategy
- **THEN** the repository MUST define one coherent declaration model or keep mirrored files intentionally synchronized
- **AND** redundant or misleading dependency declarations MUST be removed or updated

### Requirement: The maintained runtime surface is intentionally limited
Only documented CLI entry points, runtime resources, and actively supported code paths MUST be presented as maintained behavior for the classifier product.

#### Scenario: Reviewing a documented runtime path
- **GIVEN** a user-facing command, configuration path, or resource-loading path is documented
- **WHEN** the runtime audit validates that behavior
- **THEN** the path MUST work with the maintained packaging and repository layout
- **AND** unsupported historical paths MUST not remain documented as supported behavior

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

### Requirement: Component extraction
BookmarkProcessor responsibilities are split into focused components.

#### Scenario: BookmarkLoader handles file loading
- **GIVEN** a BookmarkLoader implementation
- **WHEN** processor.process_files() is called
- **THEN** loader.load() is used to read bookmark files

#### Scenario: ClassificationCoordinator handles classification
- **GIVEN** a ClassificationCoordinator implementation
- **WHEN** processor processes bookmarks
- **THEN** coordinator.classify() is used for classification

#### Scenario: FeedbackService handles feedback loop
- **GIVEN** a FeedbackService implementation
- **WHEN** processor.apply_feedback_file() is called
- **THEN** feedback_service.apply() is used

### Requirement: Fusion delegation
AIBookmarkClassifier delegates fusion to FusionEngine.

#### Scenario: Use injected FusionEngine
- **GIVEN** an AIBookmarkClassifier with injected FusionEngine
- **WHEN** classify() is called
- **THEN** fusion_engine.fuse() is used for result fusion

#### Scenario: No internal fusion implementation
- **GIVEN** AIBookmarkClassifier code
- **WHEN** reviewed
- **THEN** _ensemble_classification() method delegates to FusionEngine

## Correctness Properties

1. **Classification Confidence**: All classifiers return confidence scores in range [0.0, 1.0]
2. **Plugin Registration Consistency**: Registered plugins are immediately available for classification
3. **Plugin Failure Isolation**: A plugin failure does not affect other plugins in the pipeline
4. **Cache TTL Expiration**: Cached features expire after configured TTL
5. **LRU Eviction Policy**: Least recently used entries are evicted first
6. Dependency declarations do not contradict the shipped package surface.
7. Documented runtime paths reflect tested behavior.
8. The product surface stays focused on maintained entry points.
9. Optional acceleration layers do not become mandatory runtime dependencies.
10. Rules-first classification remains the maintained product contract.
11. Confidence-based abstention uses one consistent calibrated decision value.

## Performance Requirements

- **Processing Speed**: Handle 100-1000 bookmarks within seconds
- **Memory Usage**: Efficient memory with LRU caching
- **Scalability**: Configurable thread count for large files
- **Accuracy**: High classification accuracy through ensemble methods

## Technical Constraints

- PEP8 Python coding standards
- Type hints throughout codebase
- Complete docstrings for public APIs
- Configuration in JSON format
- ML dependencies: scikit-learn, jieba (Chinese NLP)

## Glossary

| Term | Definition |
|------|------------|
| RuleEngine | Keyword-based fast classification engine |
| MLClassifier | Machine learning classifier using scikit-learn |
| AIClassifier | AI orchestrator coordinating multiple methods |
| BookmarkProcessor | Batch bookmark processing coordinator |
| EnhancedClassifier | Main classifier integrating all methods |

## References

- Architecture RFC: `openspec/changes/archive/2026-04-23-architecture-upgrade/`
- Tests: `tests/` directory
