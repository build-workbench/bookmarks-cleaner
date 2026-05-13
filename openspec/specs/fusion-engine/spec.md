# Capability: Fusion Engine

## Overview

统一的分类结果融合引擎，消除三处重复实现（AIBookmarkClassifier、ClassifierOrchestrator、ClassifierPipeline）。支持加权投票、置信度校准、备选分类生成。

## Requirements

### Requirement: Weighted voting fusion
融合多个分类器的结果，使用方法权重进行加权投票。

#### Scenario: Fuse results from multiple classifiers
- **GIVEN** results from rule_engine, ml_classifier, semantic_analyzer
- **WHEN** fusion.fuse(results, features) is called
- **THEN** category with highest weighted score is selected
- **AND** confidence is the raw confidence of winning category
- **AND** alternatives list contains other candidates sorted by score

### Requirement: Method weights configuration
支持配置各分类方法的权重。

#### Scenario: Default weights
- **GIVEN** no custom weights provided
- **WHEN** FusionEngine is initialized
- **THEN** default weights are: rule_engine=0.50, ml=0.15, semantic=0.10, user_profile=0.10, llm=0.50

#### Scenario: Custom weights override
- **GIVEN** custom weights dict
- **WHEN** FusionEngine(method_weights=custom) is initialized
- **THEN** custom weights override defaults

### Requirement: Confidence calibration
可选的置信度校准功能。

#### Scenario: Calibrate confidence
- **GIVEN** a ConfidenceCalibrator is configured
- **WHEN** fusion produces a result
- **THEN** confidence is calibrated before returning

#### Scenario: No calibration when not configured
- **GIVEN** no ConfidenceCalibrator configured
- **WHEN** fusion produces a result
- **THEN** raw confidence is returned unchanged

### Requirement: Facets merging
合并各分类器的分面信息（facets）。

#### Scenario: Merge facets from results
- **GIVEN** multiple results with different facets
- **WHEN** fusion.fuse() is called
- **THEN** facets are merged with first-writer-wins policy

### Requirement: Empty results handling
正确处理空结果列表。

#### Scenario: No results available
- **GIVEN** empty results list
- **WHEN** fusion.fuse([], features) is called
- **THEN** a fallback ClassificationResult is returned with category="未分类", confidence=0.0

## Correctness Properties

1. **Single Implementation**: All fusion logic in one place
2. **Confidence Range**: Output confidence always in [0.0, 1.0]
3. **Deterministic**: Same inputs produce same outputs
4. **No Side Effects**: Fusion does not modify input results
