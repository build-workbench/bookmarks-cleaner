# Pipeline 架构

Bookmarks Cleaner 采用 **5 阶段 Pipeline 架构**，通过 `BookmarkProcessorCoordinator` 协调各个 Pipeline 的执行顺序和数据流转。

## 架构概览

```mermaid
flowchart TB
    subgraph Input["📥 输入层"]
        HTML[bookmarks.html]
        JSON_IN[bookmarks.json]
    end
    
    subgraph Pipeline["⚙️ 处理管道"]
        L[BookmarkLoader<br/>加载器] --> D[DeduplicationPipeline<br/>去重]
        D --> C[ClassificationPipeline<br/>分类]
        C --> O[OrganizationPipeline<br/>组织]
        O --> E[ExportPipeline<br/>导出]
    end
    
    subgraph Classifiers["🤖 分类器层"]
        R[RuleEngine<br/>规则引擎] --> F[FusionEngine<br/>融合引擎]
        M[MLClassifier<br/>机器学习] --> F
        S[SemanticAnalyzer<br/>语义分析] --> F
        LLM[LLMClassifier<br/>大语言模型] --> F
    end
    
    subgraph Output["📤 输出层"]
        HTML_OUT[HTML 报告]
        JSON_OUT[JSON 数据]
        MD[Markdown]
    end
    
    HTML --> L
    JSON_IN --> L
    C --> Classifiers
    E --> Output
```

## 5 阶段详解

### 1. BookmarkLoader（加载阶段）

**职责**：解析浏览器导出的书签文件，转换为统一的内部数据结构。

```python
class BookmarkLoader:
    def load(self, file_path: str) -> List[Dict]:
        """加载书签文件，支持 HTML/JSON 格式"""
        
    def _parse_html(self, content: str) -> List[Dict]:
        """解析 Netscape Bookmark 格式"""
        
    def _normalize(self, bookmarks: List[Dict]) -> List[Bookmark]:
        """标准化书签数据"""
```

**支持的格式**：
- Chrome/Edge HTML 导出
- Firefox JSON 备份
- Safari HTML 书签

### 2. DeduplicationPipeline（去重阶段）

**职责**：识别并处理重复书签，减少数据冗余。

```python
class DeduplicationPipeline:
    def process(self, bookmarks: List[Bookmark]) -> List[Bookmark]:
        """执行去重流程"""
        
    def _by_url(self, bookmarks: List[Bookmark]) -> List[Bookmark]:
        """URL 完全匹配去重"""
        
    def _by_similarity(self, bookmarks: List[Bookmark]) -> List[Bookmark]:
        """相似度去重（可选）"""
```

**去重策略**：
| 策略 | 描述 | 性能 |
|------|------|------|
| URL 精确匹配 | 比较规范化后的 URL | O(n) |
| 域名+路径匹配 | 忽略查询参数差异 | O(n) |
| 语义相似度 | 计算标题/描述相似度 | O(n²) |

### 3. ClassificationPipeline（分类阶段）

**职责**：为每个书签分配一个或多个分类标签。

```python
class ClassificationPipeline:
    def __init__(self, classifier: AIBookmarkClassifier):
        self.classifier = classifier
        
    def process(self, bookmarks: List[Bookmark]) -> List[ClassifiedBookmark]:
        """执行分类流程"""
        
    def _batch_classify(self, bookmarks: List[Bookmark]) -> List[Result]:
        """批量分类，利用并发加速"""
```

**分类流程**：
```mermaid
flowchart LR
    B[书签] --> R{规则匹配?}
    R -->|是| RC[规则分类]
    R -->|否| M{ML 可用?}
    M -->|是| MC[ML 分类]
    M -->|否| S[语义分析]
    RC --> F[融合结果]
    MC --> F
    S --> F
    F --> O[输出分类]
```

### 4. OrganizationPipeline（组织阶段）

**职责**：根据分类结果组织书签层级结构。

```python
class OrganizationPipeline:
    def process(self, bookmarks: List[ClassifiedBookmark]) -> Dict:
        """组织书签层级结构"""
        
    def _build_tree(self, bookmarks: List[Bookmark]) -> CategoryTree:
        """构建分类树"""
```

**输出结构**：
```
分类树/
├── 技术/
│   ├── 编程语言/
│   │   ├── Python/
│   │   └── JavaScript/
│   └── 框架/
├── 设计/
│   ├── UI/UX/
│   └── 图形设计/
└── 工具/
```

### 5. ExportPipeline（导出阶段）

**职责**：将处理结果导出为多种格式。

```python
class ExportPipeline:
    def export(self, organized: Dict, output_dir: str) -> Dict[str, str]:
        """导出处理结果"""
        
    def _to_html(self, data: Dict) -> str:
        """生成 HTML 报告"""
        
    def _to_json(self, data: Dict) -> str:
        """生成 JSON 数据"""
        
    def _to_markdown(self, data: Dict) -> str:
        """生成 Markdown 文档"""
```

## 数据流转

```mermaid
sequenceDiagram
    participant User
    participant Coordinator
    participant Loader
    participant Dedup
    participant Class
    participant Org
    participant Export
    
    User->>Coordinator: process_files(["bookmarks.html"])
    Coordinator->>Loader: load("bookmarks.html")
    Loader-->>Coordinator: List[Bookmark] (1247 items)
    
    Coordinator->>Dedup: process(bookmarks)
    Dedup-->>Coordinator: List[Bookmark] (1158 items, 89 removed)
    
    Coordinator->>Class: process(bookmarks)
    Note over Class: 并发分类<br/>ThreadPoolExecutor
    Class-->>Coordinator: List[ClassifiedBookmark]
    
    Coordinator->>Org: process(classified)
    Org-->>Coordinator: CategoryTree
    
    Coordinator->>Export: export(tree, "output/")
    Export-->>Coordinator: {html, json, md}
    
    Coordinator-->>User: Statistics
```

## 性能特性

| 指标 | 数值 | 说明 |
|------|------|------|
| 处理速度 | 500+ 书签/秒 | 单线程基准 |
| 并发加速 | 4x | 4 线程并发 |
| 内存占用 | < 100MB | 10,000 书签 |
| 启动时间 | < 100ms | 延迟初始化 |

## 扩展点

Pipeline 架构支持灵活扩展：

1. **自定义 Pipeline**：实现 `IPipeline` 接口
2. **中间件模式**：在 Pipeline 之间插入处理逻辑
3. **事件钩子**：`on_before_process`、`on_after_process`

```python
# 自定义 Pipeline 示例
class CustomPipeline(IPipeline):
    def process(self, bookmarks: List[Bookmark]) -> List[Bookmark]:
        # 自定义处理逻辑
        return processed_bookmarks
```

## 相关文档

- [依赖注入容器](/zh/architecture/container) - 组件管理和依赖注入
- [Protocol 接口](/zh/architecture/protocols) - 接口定义和契约
- [融合算法](/zh/algorithms/fusion) - 分类器融合机制
