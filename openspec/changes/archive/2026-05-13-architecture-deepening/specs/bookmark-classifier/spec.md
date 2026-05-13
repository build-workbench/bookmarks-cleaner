# Capability: Bookmark Classifier (Modified)

## MODIFIED Requirements

### Requirement: Bookmark Processing
Process browser bookmark HTML files for automatic organization into meaningful categories. The BookmarkProcessor is now a pure coordinator using dependency injection.

#### Scenario: HTML Input Processing
- **GIVEN** a valid HTML bookmark file
- **WHEN** the file is processed
- **THEN** bookmarks are extracted with titles, URLs, and metadata
- **AND** results are output in HTML, JSON, and Markdown formats

#### Scenario: Dependency Injection
- **GIVEN** a BookmarkProcessor with injected components
- **WHEN** processor is initialized with classifier, deduplicator, exporter
- **THEN** injected components are used instead of creating new instances

#### Scenario: Parallel Processing
- **GIVEN** a bookmark file with multiple entries
- **WHEN** processing is initiated
- **THEN** bookmarks are processed in parallel using multi-threading

### Requirement: Classification Configuration
Allow users to customize classification rules and categories through injected ConfigProvider.

#### Scenario: Custom Rules
- **GIVEN** a ConfigProvider with custom configuration
- **WHEN** processor is initialized with the config provider
- **THEN** classification matches the custom configuration

#### Scenario: Category Hierarchy
- **GIVEN** a category configuration
- **WHEN** parent-child relationships are defined
- **THEN** bookmarks are organized hierarchically

### Requirement: Performance Optimization
Provide fast bookmark processing with intelligent caching through injected components.

#### Scenario: LRU Cache
- **GIVEN** repeated bookmark classifications
- **WHEN** the same URL is processed again
- **THEN** cached results are returned without recomputation

#### Scenario: Batch Processing
- **GIVEN** multiple bookmark files
- **WHEN** batch processing is initiated
- **THEN** all files are processed efficiently

### Requirement: Multiple Output Formats
Support various output formats through injected IExporter.

#### Scenario: HTML Output
- **GIVEN** classified bookmarks
- **WHEN** HTML output is requested
- **THEN** the result is importable to browsers

#### Scenario: JSON Output
- **GIVEN** classified bookmarks
- **WHEN** JSON output is requested
- **THEN** detailed classification metadata is included

## ADDED Requirements

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
- **THEN** _ensemble_classification() method does not exist
