# 系统架构

> 最后更新: 2026-04-16

## 架构概述

CleanBook 采用分层架构设计，实现离线优先的书签清理与分类系统。

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                              │
│         CLI (cleanbook / cleanbook-wizard)                  │
├─────────────────────────────────────────────────────────────┤
│                      业务逻辑层                              │
│      BookmarkProcessor / DataExporter / Deduplicator        │
├─────────────────────────────────────────────────────────────┤
│                      分类引擎层                              │
│   AIBookmarkClassifier + Plugin Pipeline (规则/ML/LLM)      │
├─────────────────────────────────────────────────────────────┤
│                      服务层                                  │
│   TaxonomyService / EmbeddingService / FeatureStore         │
├─────────────────────────────────────────────────────────────┤
│                      基础设施层                              │
│   ConfigManager / ResourceLoader / PerformanceMonitor       │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 分类系统

#### AIBookmarkClassifier (`src/ai_classifier.py`)

统一的分类入口，集成多种分类策略：

- **输入**: URL + 标题
- **输出**: ClassificationResult (分类、置信度、推理过程)
- **特性**:
  - 多方法融合（规则引擎、ML、语义分析、用户画像、LLM）
  - LRU 缓存优化（feature_cache、classification_cache）
  - 支持在线学习（learn_from_feedback）

**核心方法**:

```python
class AIBookmarkClassifier:
    def classify(self, url: str, title: str) -> ClassificationResult:
        """主分类入口"""
        
    def _ensemble_classification(self, results: List[ClassificationResult]) -> ClassificationResult:
        """加权投票融合多方法结果"""
```

#### 插件管道系统 (`src/plugins/`)

模块化的分类器架构：

| 插件 | 文件 | 优先级 | 说明 |
|------|------|--------|------|
| RuleClassifier | `classifiers/rule_classifier.py` | 10 (最高) | 基于规则的快速分类 |
| MLClassifier | `classifiers/ml_classifier.py` | 50 | 机器学习分类 |
| EmbeddingClassifier | `classifiers/embedding_classifier.py` | 50 | 语义嵌入分类 |
| LLMClassifier | `classifiers/llm_classifier.py` | 90 (最低) | 大模型分类（可选） |

### 数据结构

#### BookmarkFeatures

```python
@dataclass
class BookmarkFeatures:
    url: str
    title: str
    domain: str
    path_segments: List[str]
    query_params: Dict[str, str]
    content_type: str
    language: str
    timestamp: datetime
```

#### ClassificationResult（统一定义）

```python
@dataclass
class ClassificationResult:
    category: str                           # 主分类
    confidence: float                       # 置信度 (0.0-1.0)
    subcategory: Optional[str] = None       # 子分类
    reasoning: List[str] = field(default_factory=list)
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "unknown"
    facets: Dict[str, str] = field(default_factory=dict)
```

> **重要**: ClassificationResult 在 `src/ai_classifier.py` 中定义，其他模块应从此处导入。

### 处理流程

```
HTML书签文件 → 解析 → 特征提取 → 去重 → 分类 → 组织 → 导出
                ↓           ↓        ↓      ↓
            BeautifulSoup  URL/标题  域名分组 插件管道
```

#### 详细流程

1. **解析阶段**: `BeautifulSoup` 解析 HTML，提取 `<a>` 标签
2. **特征提取**: 解析 URL 组件，检测语言和内容类型
3. **去重**: 基于 URL 标准化和相似度计算去重
4. **分类**: 通过插件管道依次尝试各分类器
5. **组织**: 按 `subject -> resource_type` 两级组织
6. **导出**: 生成 HTML/Markdown/JSON 输出

## 性能优化

### 缓存策略

所有缓存使用 OrderedDict 实现 LRU 淘汰：

| 缓存 | 位置 | 最大容量 | 说明 |
|------|------|----------|------|
| feature_cache | AIBookmarkClassifier | 10,000 | 书签特征 |
| classification_cache | AIBookmarkClassifier | 5,000 | 分类结果 |
| _classification_cache | BookmarkProcessor | 10,000 | 处理结果 |

### 预编译正则

常用正则表达式在模块级别预编译：

```python
# src/ai_classifier.py, src/llm_classifier.py, src/ml_classifier.py
_CHINESE_REGEX = re.compile(r'[\u4e00-\u9fff]')
_ENGLISH_REGEX = re.compile(r'[a-zA-Z]')
_DIGIT_REGEX = re.compile(r'\d')
```

### 并行处理

- 使用 ThreadPoolExecutor 并行处理书签
- 文件加载与分类处理分离
- 批量导出并行化

## 配置系统

### 配置加载优先级

1. 显式指定的配置路径 (`--config`)
2. 当前目录的 `config.json`
3. 内置默认配置

### 配置结构

```json
{
  "category_rules": { ... },      // 分类规则
  "priority_rules": { ... },      // 优先级规则
  "category_order": [ ... ],      // 分类顺序
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000,
    "max_workers": 4
  },
  "llm": {                        // LLM 配置（可选）
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

## 插件开发

### 创建新分类器

1. 继承 `ClassifierPlugin` 基类
2. 实现必需方法：`classify()`, `initialize()`, `shutdown()`
3. 在 `src/plugins/classifiers/` 创建文件
4. 在 `registry.py` 注册

### 示例

```python
from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures

class MyClassifier(ClassifierPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_classifier",
            version="1.0.0",
            capabilities=["custom"],
            priority=50
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        # 实现分类逻辑
        return ClassificationResult(
            category="分类结果",
            confidence=0.9,
            method="my_classifier"
        )
```

## 错误处理

- 分类失败自动降级到下一优先级分类器
- 所有分类器失败时返回默认分类结果
- 配置错误时使用内置默认配置

## 扩展点

- **分类器插件**: 添加新的分类策略
- **导出格式**: 扩展 DataExporter
- **规则类型**: 在 rule_engine.py 添加新匹配模式
- **LLM 提示词**: 自定义 llm_prompt_builder.py
