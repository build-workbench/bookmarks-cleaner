# CleanBook 设计说明

> 目标：以 KISS 原则实现"受控词表 + 分面分类 + 权威控制"的现代化书签分类系统，默认离线可用，可选接入 LLM。

## 架构概览

```
输入层          处理层              分类层              输出层
┌────────┐    ┌──────────┐      ┌──────────┐      ┌──────────┐
│ HTML   │───▶│ 解析/    │─────▶│ 多方法   │─────▶│ HTML/    │
│ Bookmarks│    │ 去重     │      │ 融合分类 │      │ Markdown/│
└────────┘    └──────────┘      └──────────┘      │ JSON     │
                      │                  │        └──────────┘
                      ▼                  ▼
               ┌──────────┐      ┌──────────┐
               │ YAML词表 │      │ 规则/ML/ │
               │ 配置驱动 │      │ LLM      │
               └──────────┘      └──────────┘
```

核心流程：`BookmarkProcessor` → 批量加载/去重 → `AIBookmarkClassifier.classify()` → 多方法融合 → 标准化/组织 → 导出

## 分类原则

### 受控词表（Controlled Vocabulary）

`taxonomy/subjects.yaml` 定义主题首选词与同义变体，避免同义项四散。

```yaml
subjects:
  - preferred: "人工智能"
    variants: ["AI", "机器学习", "深度学习"]
    icon: "🤖"
```

### 分面分类（Faceted Classification）

- **主维度**: `subject`（主题）
- **资源类型分面**: `resource_type`（如 `code_repository`、`documentation`、`video`）
- 最终输出层级：`subject -> resource_type -> items`

### 权威控制（Authority Control）

- 通过 YAML 形式集中维护可扩展的权威表
- 版本化、审阅友好
- 配置优先，无需改代码即可调整分类逻辑

### KISS 原则

- 实现保持简洁
- YAML 可读、默认离线
- 组件可插拔

## 核心组件

### 1. BookmarkProcessor 书签处理器

协调整个处理流程：

| 阶段 | 功能 | 说明 |
|------|------|------|
| 加载 | 解析 HTML 书签文件 | 使用 BeautifulSoup |
| 去重 | 基于 URL 相似度去重 | 多维度相似度计算 |
| 分类 | 调用 AIBookmarkClassifier | 批量并行处理 |
| 组织 | 按 subject/resource_type 组织 | 标准化输出结构 |
| 导出 | 多格式导出 | HTML/JSON/Markdown |

### 2. AIBookmarkClassifier 分类器

统一的分类入口：

```python
class AIBookmarkClassifier:
    def classify(self, url: str, title: str) -> ClassificationResult:
        """
        融合多种分类方法的结果
        - 规则引擎 (最高优先级)
        - ML 分类器 (中等优先级)
        - 语义分析 (辅助)
        - LLM 分类 (可选，最低优先级)
        """
```

### 3. 规则引擎

预编译基于 `config.json` 的规则：

```json
{
  "category_rules": {
    "技术/编程": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["github.com", "stackoverflow.com"],
          "weight": 15
        }
      ]
    }
  }
}
```

匹配类型支持：`domain`、`title`、`url`、`url_starts_with`、`url_ends_with`、`url_matches_regex`

### 4. TaxonomyStandardizer 标准化层

基于 `taxonomy/*.yaml` 做受控词表与分面标准化：

- `normalize_subject(text)`: 将任意文本映射到规范主题
- `normalize_resource_type(text)`: 将任意文本映射到规范资源类型

## 数据流

```
┌─────────────────────────────────────────────────────────────┐
│  HTML 书签文件                                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ parse_bookmarks()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[Bookmark]                                             │
│  - url                                                      │
│  - title                                                    │
│  - add_date                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ deduplicate()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[Bookmark] (去重后)                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ extract_features() 并行处理
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[(Bookmark, BookmarkFeatures)]                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ classify_batch()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[(Bookmark, ClassificationResult)]                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ organize_bookmarks()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Dict[subject, Dict[resource_type, List[Bookmark]]]          │
└──────────────────────┬──────────────────────────────────────┘
                       │ export()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  HTML / Markdown / JSON 文件                                │
└─────────────────────────────────────────────────────────────┘
```

## 缓存策略

所有缓存使用 `OrderedDict` 实现 LRU 淘汰：

| 缓存 | 位置 | 容量 | 说明 |
|------|------|------|------|
| feature_cache | AIBookmarkClassifier | 10,000 | 书签特征缓存 |
| classification_cache | AIBookmarkClassifier | 5,000 | 分类结果缓存 |
| _classification_cache | BookmarkProcessor | 10,000 | 处理结果缓存 |

## 术语速览

| 术语 | 说明 | 示例 |
|------|------|------|
| subject | 主题（主维度） | AI、Python、Productivity |
| resource_type | 资源类型（分面） | documentation、code_repository、video |
| facets | 分面属性字典 | `{"resource_type_hint": "documentation"}` |
| confidence | 置信度 (0.0-1.0) | 0.95 表示高置信度 |
| method | 使用的方法 | rule_engine、ml_classifier、llm_classifier |

## 5 分钟上手

1. **准备输入**: 导出浏览器书签 HTML
2. **最小执行**:
   ```bash
   cleanbook -i bookmarks.html -o output
   ```
3. **查看产出**: 在 `output/` 下检查 Markdown 报告
4. **调优配置**: 根据结果调整 `config.json` 规则

## 扩展点

- **分类器插件**: `src/plugins/classifiers/`
- **导出格式**: 扩展 `DataExporter`
- **规则类型**: 在 `rule_engine.py` 添加新匹配模式
- **LLM 提示词**: 自定义 `llm_prompt_builder.py`

## 设计取舍

| 方案 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| 纯规则 | 确定性高、可解释 | 维护成本高、泛化弱 | ✅ 保留作为优先路径 |
| 纯 ML | 泛化能力强 | 需要训练数据、冷启动问题 | ✅ 作为增强 |
| 纯 LLM | 理解能力强 | 成本高、延迟大 | ✅ 可选 fallback |
| 混合融合 | 兼顾各方面 | 复杂度较高 | ✅ 当前方案 |
