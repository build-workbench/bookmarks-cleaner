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

## Correctness Properties

1. **Classification Confidence**: All classifiers return confidence scores in range [0.0, 1.0]
2. **Plugin Registration Consistency**: Registered plugins are immediately available for classification
3. **Plugin Failure Isolation**: A plugin failure does not affect other plugins in the pipeline
4. **Cache TTL Expiration**: Cached features expire after configured TTL
5. **LRU Eviction Policy**: Least recently used entries are evicted first

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

- Product requirements: `specs/product/bookmark-classifier-system.md` (historical)
- Architecture RFC: `openspec/changes/archive/2026-04-23-architecture-upgrade/`
- Tests: `tests/` directory
