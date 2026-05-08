# CONTEXT.md - 领域语言与概念模型

本文档定义了 CleanBook 书签清理工具的核心领域概念，为架构讨论提供统一语言。

## 核心领域概念

### 书签处理 (Bookmark Processing)

**书签 (Bookmark)**
- 定义：用户保存的网页链接，包含 URL、标题、添加时间等元数据
- 来源：浏览器导出的 HTML 文件
- 特征：URL、域名、标题、路径段、查询参数

**书签处理器 (BookmarkProcessor)**
- 定义：协调书签处理全流程的主模块
- 职责：HTML解析、分类、去重、健康检查、导出
- 深度：高杠杆模块，接口简单（输入文件，输出结果）

### 分类体系 (Classification)

**分类法 (Taxonomy)**
- 定义：书签的分类层次结构
- 组成：主题分类（subjects）、资源类型（resource_types）
- 位置：`taxonomy/` 目录下的 YAML 文件

**分类器 (Classifier)**
- 定义：将书签映射到分类的模块
- 层次：规则优先 → ML辅助 → LLM可选
- 深度：规则引擎深度高（简单规则，大量匹配），ML分类器中等深度

**规则引擎 (RuleEngine)**
- 定义：基于模式的快速分类器
- 优势：确定性、可解释、离线运行
- 深度：高（简单接口，大量内部规则）

**ML分类器 (MLClassifier)**
- 定义：基于机器学习的分类器
- 特征：URL特征、标题特征、域名特征
- 模型：RandomForest、SGDClassifier
- 深度：中等（接口简单，但训练/预测逻辑复杂）

**LLM分类器 (LLMClassifier)**
- 定义：可选的大语言模型分类器
- 特点：高质量但依赖API、成本高
- 深度：浅（主要是API调用封装）

### 数据处理管道 (Data Pipeline)

**特征提取 (Feature Extraction)**
- URL特征：长度、路径段、查询参数
- 标题特征：TF-IDF向量、语言检测
- 域名特征：TLD、子域名

**特征存储 (FeatureStore)**
- 定义：缓存和管理书签特征的服务
- 策略：TTL过期、LRU淘汰
- 深度：中等（接口简单，缓存逻辑复杂）

**去重器 (Deduplicator)**
- 定义：识别和合并重复书签
- 策略：URL规范化、内容相似度
- 深度：高（简单接口，复杂的去重算法）

**健康检查器 (HealthChecker)**
- 定义：检测书签链接的可用性
- 异步：并发HTTP请求
- 深度：中等（接口简单，但网络IO复杂）

### 服务层 (Services)

**嵌入服务 (EmbeddingService)**
- 定义：文本向量化和相似度计算
- 后端：TF-IDF（默认）、Sentence Transformers（可选）
- 深度：高（统一接口，多种后端实现）

**主动学习 (ActiveLearning)**
- 定义：人机协作的模型优化
- 策略：不确定性采样、低置信度样本
- 深度：中等（接口清晰，采样策略可扩展）

**增量训练 (IncrementalTrainer)**
- 定义：基于反馈的模型在线更新
- 场景：用户纠正分类后改进模型
- 深度：中等（接口简单，训练逻辑复杂）

### 插件系统 (Plugin System)

**插件 (Plugin)**
- 定义：可扩展的分类器实现
- 接口：`classify()`, `initialize()`, `shutdown()`
- 深度：高（统一接口，多样实现）

**插件注册中心 (PluginRegistry)**
- 定义：插件的注册、发现和管理
- 功能：优先级排序、依赖管理、生命周期
- 深度：高（简单注册接口，复杂的管理逻辑）

**分类器管道 (ClassifierPipeline)**
- 定义：按优先级编排多个分类器
- 流程：Rule → ML → LLM → Embedding
- 深度：高（简单执行接口，复杂的编排逻辑）

### 导出系统 (Export)

**数据导出器 (DataExporter)**
- 定义：将处理结果输出到多种格式
- 格式：HTML、JSON、Markdown
- 深度：中等（统一接口，多种格式实现）

**报告生成 (ReportGeneration)**
- 分类报告：JSON格式的分类结果
- Markdown报告：人类可读的统计摘要

## 架构概念

### 模块深度 (Module Depth)

**深层模块 (Deep Module)**
- 特征：简单接口 + 复杂实现 = 高杠杆
- 例子：RuleEngine（简单规则接口，大量匹配逻辑）

**浅层模块 (Shallow Module)**
- 特征：接口复杂度 ≈ 实现复杂度
- 例子：转发模块、薄封装层

### 接缝 (Seam)

**定义**：可以改变行为而无需编辑的地方

**真实缝**：有多个适配器的接口
- 插件系统：RulePlugin, MLPlugin, LLMPlugin
- 嵌入后端：TFIDFBackend, SentenceTransformerBackend

**假设缝**：只有一个实现的接口
- 健康检查器：只有HTTP实现

### 适配器 (Adapter)

**定义**：满足特定接口的具体实现

**示例**：
- 分类器插件：RuleClassifierPlugin, MLClassifierPlugin
- 嵌入后端：TFIDFEmbedding, SentenceTransformerEmbedding

## 项目阶段

**当前阶段**：Beta - 最终清理阶段
**维护模式**：单一维护者、OpenSpec驱动
**工作流**：explore → propose → apply → archive

## 架构原则

1. **规则优先**：稳定、可解释、离线可用
2. **ML辅助**：提升准确率但不强制依赖
3. **LLM可选**：高质量但非必需
4. **离线优先**：默认不依赖外部服务
5. **插件化**：可扩展的分类器架构
6. **深层模块**：追求高杠杆的接口设计

---

*本文档使用 `/grill-with-docs` 技能维护，遵循领域驱动设计原则。*
