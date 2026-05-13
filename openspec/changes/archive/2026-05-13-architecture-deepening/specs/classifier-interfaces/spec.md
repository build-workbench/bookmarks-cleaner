# Capability: Classifier Interfaces

## Overview

核心分类器接口定义，建立依赖倒置原则。使用 Python Protocol 定义结构化子类型，允许现有类隐式实现接口，支持依赖注入和独立测试。

## Requirements

### Requirement: IClassifier Protocol
定义分类器接口，所有分类器必须实现此接口。

#### Scenario: Classify bookmark features
- **GIVEN** a BookmarkFeatures object containing URL, title, domain
- **WHEN** classifier.classify(features) is called
- **THEN** a ClassificationResult is returned with category, confidence, method

#### Scenario: Optional batch classification
- **GIVEN** a list of BookmarkFeatures objects
- **WHEN** classifier.classify_batch(features_list) is called
- **THEN** a list of ClassificationResult is returned in same order

### Requirement: IDeduplicator Protocol
定义去重器接口。

#### Scenario: Remove duplicate bookmarks
- **GIVEN** a list of bookmark dictionaries
- **WHEN** deduplicator.remove_duplicates(bookmarks) is called
- **THEN** a tuple of (unique_bookmarks, duplicates) is returned

### Requirement: IExporter Protocol
定义导出器接口。

#### Scenario: Export bookmarks to format
- **GIVEN** classified bookmarks and output format
- **WHEN** exporter.export(bookmarks, format, output_dir) is called
- **THEN** files are written to output directory

### Requirement: IConfigProvider Protocol
定义配置提供者接口。

#### Scenario: Get configuration value
- **GIVEN** a dot-notation path (e.g., "ai_settings.confidence_threshold")
- **WHEN** config.get(path, default) is called
- **THEN** the configuration value or default is returned

#### Scenario: Get entire configuration section
- **GIVEN** a section path
- **WHEN** config.get_section(path) is called
- **THEN** a dictionary of that section is returned

### Requirement: IBookmarkLoader Protocol
定义书签加载器接口。

#### Scenario: Load bookmarks from file
- **GIVEN** a file path to bookmark HTML
- **WHEN** loader.load(path) is called
- **THEN** a list of bookmark dictionaries is returned

### Requirement: IFusionEngine Protocol
定义融合引擎接口。

#### Scenario: Fuse multiple classification results
- **GIVEN** a list of ClassificationResult from multiple classifiers
- **WHEN** fusion.fuse(results, features) is called
- **THEN** a single fused ClassificationResult is returned

## Correctness Properties

1. **Protocol Compatibility**: Existing classes implicitly satisfy protocols without modification
2. **Type Safety**: All protocol methods have complete type hints
3. **No Runtime Overhead**: Protocols use structural subtyping, no inheritance required
4. **Testability**: Protocols enable easy mock injection for testing
