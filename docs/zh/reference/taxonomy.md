# 词表格式

CleanBook 使用 YAML 格式的词表文件来定义受控词表和分类体系。

## 词表文件位置

```
config/
└── taxonomy/
    ├── subjects.yaml         # 主题词表
    └── resource_types.yaml   # 资源类型词表
```

## subjects.yaml

定义书签的主题分类体系。

### 基本结构

```yaml
subjects:
  - preferred: "人工智能"
    variants:
      - "AI"
      - "机器学习"
      - "深度学习"
      - "神经网络"
    icon: "🤖"
    description: "人工智能相关的工具、平台和资源"
    
  - preferred: "编程"
    variants:
      - "开发"
      - "软件工程"
      - "代码"
    icon: "💻"
    description: "软件开发、编程语言和框架"
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `preferred` | string | 是 | 首选词（规范名称） |
| `variants` | array | 否 | 同义变体列表 |
| `icon` | string | 否 | 分类图标（Emoji） |
| `description` | string | 否 | 分类描述 |
| `parent` | string | 否 | 父分类（用于层级） |

### 层级分类

```yaml
subjects:
  - preferred: "编程"
    icon: "💻"
    
  - preferred: "编程/Python"
    parent: "编程"
    variants: ["Python 开发", "Py"]
    icon: "🐍"
    
  - preferred: "编程/JavaScript"
    parent: "编程"
    variants: ["JS", "JS 开发"]
    icon: "📜"
```

## resource_types.yaml

定义资源类型分面。

```yaml
resource_types:
  - name: "documentation"
    label: "文档"
    icon: "📚"
    description: "官方文档、API 参考等技术文档"
    
  - name: "code_repository"
    label: "代码仓库"
    icon: "📦"
    description: "GitHub、GitLab 等代码仓库"
    
  - name: "tutorial"
    label: "教程"
    icon: "📖"
    description: "学习教程、入门指南"
    
  - name: "tool"
    label: "工具"
    icon: "🛠️"
    description: "在线工具、软件、服务"
    
  - name: "article"
    label: "文章"
    icon: "📝"
    description: "博客文章、技术文章"
    
  - name: "video"
    label: "视频"
    icon: "▶️"
    description: "视频教程、讲座"
    
  - name: "community"
    label: "社区"
    icon: "👥"
    description: "论坛、社区、问答网站"
    
  - name: "news"
    label: "资讯"
    icon: "📰"
    description: "新闻、周刊、资讯聚合"
```

## 词表标准化

CleanBook 使用词表将任意文本映射到规范分类：

```python
from src.utils.taxonomy import TaxonomyStandardizer

standardizer = TaxonomyStandardizer()

# 标准化主题
standardizer.normalize_subject("机器学习")  # → "人工智能"
standardizer.normalize_subject("ML")        # → "人工智能"
standardizer.normalize_subject("AI")        # → "人工智能"

# 标准化资源类型
standardizer.normalize_resource_type("api-docs")  # → "documentation"
```

## 词表优先级

当出现歧义时，标准化器会：

1. 优先匹配完整词（如 "机器学习" > "学习"）
2. 优先匹配首选词
3. 按词表顺序匹配（靠前的优先）

## 最佳实践

1. **保持简洁**: 不要创建过多分类，建议 10-15 个主分类
2. **命名清晰**: 使用简洁、无歧义的名称
3. **添加变体**: 为每个分类添加常见同义词
4. **定期维护**: 根据实际使用情况调整词表
5. **版本控制**: 将词表文件纳入版本控制

## 完整示例

```yaml
# subjects.yaml
subjects:
  - preferred: "人工智能"
    variants: ["AI", "机器学习", "深度学习", "ML"]
    icon: "🤖"
    
  - preferred: "编程开发"
    variants: ["编程", "开发", "coding", "software engineering"]
    icon: "💻"
    
  - preferred: "数据结构算法"
    variants: ["算法", "数据结构", "DSA"]
    parent: "编程开发"
    icon: "🔢"
    
  - preferred: "前端开发"
    variants: ["前端", "Web 前端", "FE"]
    parent: "编程开发"
    icon: "🎨"
    
  - preferred: "后端开发"
    variants: ["后端", "服务端", "BE", "Server-side"]
    parent: "编程开发"
    icon: "⚙️"
    
  - preferred: "开发工具"
    variants: ["工具", "DevTools"]
    icon: "🛠️"
    
  - preferred: "技术文档"
    variants: ["文档", "Documentation"]
    icon: "📚"
    
  - preferred: "技术社区"
    variants: ["社区", "论坛", "Community"]
    icon: "👥"
    
  - preferred: "新闻资讯"
    variants: ["新闻", "资讯", "News"]
    icon: "📰"
```

## 与分类规则的关系

词表（Taxonomy）和分类规则（category_rules）是互补的：

- **词表**: 定义"有哪些分类"
- **分类规则**: 定义"如何识别这些分类"

```
词表:
  - 人工智能
  
规则:
  - 如果域名包含 "openai.com" → 人工智能
  - 如果标题包含 "GPT" → 人工智能
```
