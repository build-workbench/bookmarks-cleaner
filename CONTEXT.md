# CONTEXT.md - 领域语言与概念模型

本文档定义了 CleanBook 书签清理工具的核心领域概念。

## 核心领域概念

### 书签处理 (Bookmark Processing)

**书签 (Bookmark)** - 用户保存的网页链接，包含URL、标题、添加时间等元数据，来源为浏览器导出的HTML文件。

**书签处理器 (BookmarkProcessor)** - 协调书签处理全流程的主模块，职责包括HTML解析、分类、去重、健康检查、导出。

### 分类体系 (Classification)

**分类法 (Taxonomy)** - 书签的分类层次结构，由主题分类（subjects）和资源类型（resource_types）组成，位于`taxonomy/`目录。

**分类器 (Classifier)** - 将书签映射到分类的模块，采用规则优先 → ML辅助 → LLM可选的层次结构。

**规则引擎 (RuleEngine)** - 基于模式的快速分类器，具有确定性、可解释、离线运行的优势。

**ML分类器 (MLClassifier)** - 基于机器学习的分类器，使用URL特征、标题特征、域名特征进行分类。

**LLM分类器 (LLMClassifier)** - 可选的大语言模型分类器，高质量但依赖API。

### 数据处理管道 (Data Pipeline)

**特征提取 (Feature Extraction)** - 提取URL特征（长度、路径段、查询参数）、标题特征（TF-IDF向量、语言检测）、域名特征（TLD、子域名）。

**特征存储 (FeatureStore)** - 缓存和管理书签特征的服务，使用TTL过期、LRU淘汰策略。

**去重器 (Deduplicator)** - 识别和合并重复书签，使用URL规范化、内容相似度策略。

**健康检查器 (HealthChecker)** - 检测书签链接的可用性，使用并发HTTP请求。

### 服务层 (Services)

**嵌入服务 (EmbeddingService)** - 文本向量化和相似度计算，支持TF-IDF（默认）和Sentence Transformers（可选）后端。

**主动学习 (ActiveLearning)** - 人机协作的模型优化，使用不确定性采样、低置信度样本策略。

**增量训练 (IncrementalTrainer)** - 基于反馈的模型在线更新。

### 插件系统 (Plugin System)

**插件 (Plugin)** - 可扩展的分类器实现，提供`classify()`, `initialize()`, `shutdown()`接口。

**插件注册中心 (PluginRegistry)** - 插件的注册、发现和管理，支持优先级排序、依赖管理、生命周期。

**分类器管道 (ClassifierPipeline)** - 按优先级编排多个分类器，流程为Rule → ML → LLM → Embedding。

### 导出系统 (Export)

**数据导出器 (DataExporter)** - 将处理结果输出到多种格式（HTML、JSON、Markdown）。

**报告生成 (ReportGeneration)** - 生成分类报告（JSON格式）和统计摘要（Markdown格式）。

## 架构原则

1. **规则优先** - 稳定、可解释、离线可用
2. **ML辅助** - 提升准确率但不强制依赖
3. **LLM可选** - 高质量但非必需
4. **离线优先** - 默认不依赖外部服务
5. **插件化** - 可扩展的分类器架构

---

*本文档遵循领域驱动设计原则，为架构讨论提供统一语言。*
