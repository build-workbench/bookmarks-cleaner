# Requirements Document

## Introduction

本文档定义了 CleanBook 智能书签分类系统的架构设计升级和算法优化需求。目标是将现有系统从单体架构演进为更模块化、可扩展的插件式架构，同时引入更先进的分类算法（如 Transformer 嵌入、主动学习、增量学习）以提升分类准确率和系统性能。

## Glossary

- **Classifier_Pipeline**: 分类器管道，负责协调多个分类方法的执行顺序和结果融合
- **Plugin_Registry**: 插件注册中心，管理所有可插拔分类器、导出器和特征提取器的注册与发现
- **Embedding_Service**: 嵌入服务，提供基于 Transformer 模型的文本向量化能力
- **Active_Learning_Engine**: 主动学习引擎，识别低置信度样本并请求用户标注
- **Incremental_Trainer**: 增量训练器，支持在线学习和模型热更新
- **Feature_Store**: 特征存储，缓存和管理提取的书签特征向量
- **Confidence_Calibrator**: 置信度校准器，对多方法融合后的置信度进行校准
- **Taxonomy_Service**: 分类体系服务，管理受控词表和分面分类映射

## Requirements

### Requirement 1: 插件式分类器架构

**User Story:** As a developer, I want a plugin-based classifier architecture, so that I can easily add, remove, or replace classification methods without modifying core code.

#### Acceptance Criteria

1. THE Plugin_Registry SHALL provide a registration interface for classifier plugins with name, version, and capability metadata
2. WHEN a new classifier plugin is registered, THE Plugin_Registry SHALL validate the plugin implements the required interface
3. THE Classifier_Pipeline SHALL load enabled plugins from configuration at startup
4. WHEN classifying a bookmark, THE Classifier_Pipeline SHALL invoke all enabled plugins in configured priority order
5. IF a plugin fails during classification, THEN THE Classifier_Pipeline SHALL log the error and continue with remaining plugins
6. THE Plugin_Registry SHALL support runtime plugin enable/disable without system restart

### Requirement 2: Transformer 嵌入分类器

**User Story:** As a user, I want more accurate classification using modern NLP techniques, so that my bookmarks are categorized with higher precision.

#### Acceptance Criteria

1. THE Embedding_Service SHALL support loading pre-trained multilingual Transformer models (e.g., sentence-transformers)
2. WHEN extracting features, THE Embedding_Service SHALL generate dense vector embeddings for bookmark titles and URLs
3. THE Embedding_Service SHALL cache computed embeddings in Feature_Store to avoid redundant computation
4. WHEN classifying, THE Embedding_Classifier SHALL compute cosine similarity between bookmark embedding and category prototype embeddings
5. THE Embedding_Classifier SHALL return classification results with confidence scores based on similarity thresholds
6. IF the Transformer model is unavailable, THEN THE Embedding_Service SHALL gracefully degrade to TF-IDF vectorization

### Requirement 3: 主动学习机制

**User Story:** As a user, I want the system to ask me for feedback on uncertain classifications, so that the model can improve over time with minimal labeling effort.

#### Acceptance Criteria

1. THE Active_Learning_Engine SHALL identify bookmarks with classification confidence below a configurable threshold
2. WHEN low-confidence bookmarks are detected, THE Active_Learning_Engine SHALL queue them for user review
3. THE Active_Learning_Engine SHALL present queued bookmarks to users with suggested categories and alternatives
4. WHEN a user provides feedback, THE Active_Learning_Engine SHALL store the labeled sample for model retraining
5. THE Active_Learning_Engine SHALL prioritize samples that maximize information gain (uncertainty sampling)
6. THE Active_Learning_Engine SHALL limit the number of feedback requests per session to avoid user fatigue

### Requirement 4: 增量学习与模型热更新

**User Story:** As a system administrator, I want the ML models to update incrementally without full retraining, so that the system can adapt to new patterns quickly.

#### Acceptance Criteria

1. THE Incremental_Trainer SHALL support partial_fit for online learning on new labeled samples
2. WHEN new training samples exceed a configurable batch size, THE Incremental_Trainer SHALL trigger incremental model update
3. THE Incremental_Trainer SHALL maintain model version history for rollback capability
4. WHEN model performance degrades below threshold, THE Incremental_Trainer SHALL automatically rollback to previous version
5. THE Incremental_Trainer SHALL support scheduled full retraining with accumulated samples
6. THE Incremental_Trainer SHALL serialize updated models atomically to prevent corruption

### Requirement 5: 多方法融合优化

**User Story:** As a developer, I want an improved ensemble method for combining classifier outputs, so that the final classification is more robust and accurate.

#### Acceptance Criteria

1. THE Classifier_Pipeline SHALL support configurable fusion strategies (weighted voting, stacking, Bayesian combination)
2. WHEN fusing results, THE Confidence_Calibrator SHALL apply Platt scaling or isotonic regression to calibrate confidence scores
3. THE Classifier_Pipeline SHALL dynamically adjust method weights based on historical accuracy per category
4. WHEN multiple methods disagree, THE Classifier_Pipeline SHALL apply conflict resolution rules from configuration
5. THE Classifier_Pipeline SHALL track per-method accuracy statistics for weight optimization
6. THE Classifier_Pipeline SHALL support A/B testing of different fusion strategies

### Requirement 6: 特征存储与缓存优化

**User Story:** As a user, I want faster classification through intelligent caching, so that repeated or similar bookmarks are processed quickly.

#### Acceptance Criteria

1. THE Feature_Store SHALL persist computed feature vectors to disk with configurable TTL
2. WHEN a bookmark URL is seen before, THE Feature_Store SHALL return cached features without recomputation
3. THE Feature_Store SHALL support approximate nearest neighbor search for similar bookmark lookup
4. THE Feature_Store SHALL implement LRU eviction policy when cache size exceeds limit
5. WHEN cache hit rate drops below threshold, THE Feature_Store SHALL log warning and suggest cache size increase
6. THE Feature_Store SHALL support cache warming from historical classification data

### Requirement 7: 分类体系动态管理

**User Story:** As a power user, I want to customize the category taxonomy at runtime, so that I can adapt the classification to my personal organization style.

#### Acceptance Criteria

1. THE Taxonomy_Service SHALL load category hierarchy from YAML configuration files
2. WHEN a user adds a new category, THE Taxonomy_Service SHALL update the taxonomy without restart
3. THE Taxonomy_Service SHALL validate category names against naming conventions (no special characters, max length)
4. WHEN a category is renamed, THE Taxonomy_Service SHALL update all historical classifications accordingly
5. THE Taxonomy_Service SHALL support category merging with automatic bookmark reassignment
6. THE Taxonomy_Service SHALL export taxonomy changes as migration scripts for version control

### Requirement 8: 性能监控与可观测性

**User Story:** As a system administrator, I want comprehensive performance metrics, so that I can monitor system health and optimize resource usage.

#### Acceptance Criteria

1. THE Performance_Monitor SHALL track classification latency percentiles (p50, p95, p99)
2. THE Performance_Monitor SHALL record per-method accuracy and confidence distribution
3. WHEN classification latency exceeds threshold, THE Performance_Monitor SHALL emit warning alerts
4. THE Performance_Monitor SHALL expose metrics in Prometheus-compatible format
5. THE Performance_Monitor SHALL generate daily classification quality reports
6. THE Performance_Monitor SHALL track cache hit rates and memory usage trends

