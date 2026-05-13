## Why

当前代码库存在明显的架构债务：`BookmarkProcessor` (1149行) 是一个承担 8+ 种职责的上帝类，所有组件直接实例化无法独立测试。融合逻辑在 3 处重复实现（`AIBookmarkClassifier._ensemble_classification()`、`ClassifierOrchestrator._ensemble()`、`ClassifierPipeline._weighted_voting()`）。配置加载存在两个入口，职责不清。这些浅模块导致变更成本高、测试困难、AI 导航性差。

## What Changes

- 提取 `IClassifier`、`IDeduplicator`、`IExporter`、`IConfigProvider` 接口（使用 Protocol）
- 提取统一的 `FusionEngine` 类，消除三处重复实现
- 解构 `BookmarkProcessor` 为 `BookmarkLoader`、`ClassificationCoordinator`、`FeedbackService`
- 统一配置加载入口，`ConfigProvider` 成为唯一实现
- 合并 `TaxonomyService` 与 `TaxonomyStandardizer` 职责
- **BREAKING**: `BookmarkProcessor` 构造器签名变更，需要依赖注入

## Capabilities

### New Capabilities

- `classifier-interfaces`: 核心分类器接口定义（IClassifier, IDeduplicator, IExporter, IConfigProvider）
- `fusion-engine`: 统一的分类结果融合引擎
- `config-provider`: 单一配置加载入口
- `taxonomy-unified`: 统一的分类体系服务（CRUD + 标准化）

### Modified Capabilities

- `bookmark-classifier`: 解构后的 BookmarkProcessor 协调器，依赖注入接口

## Impact

- `src/bookmark_processor.py`: 从 1149 行降至 ~200 行
- `src/classifiers/ai.py`: 移除 `_ensemble_classification()`，委托给 FusionEngine
- `src/classifiers/orchestrator.py`: 委托给 FusionEngine
- `src/plugins/pipeline.py`: 委托给 FusionEngine
- `src/config_manager.py`: 成为 ConfigProvider 唯一实现
- `src/utils/standardizer.py`: 合并到 TaxonomyService
- `tests/`: 新增接口 mock 测试，移除大量 skip 标记

## Non-goals

- 不改变外部 CLI 接口（`main.py` 入口点保持不变）
- 不改变分类结果格式（`ClassificationResult` 数据结构不变）
- 不引入新的外部依赖
- 不改变插件系统核心设计（PluginRegistry、ClassifierPlugin 保留）
