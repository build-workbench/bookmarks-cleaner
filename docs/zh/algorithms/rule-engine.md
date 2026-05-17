# 规则引擎

规则引擎是 Bookmarks Cleaner 的 **第一道分类防线**，通过预定义的模式匹配规则实现快速、确定性的分类。

## 设计原理

```mermaid
flowchart LR
    B[书签] --> P{模式匹配}
    P -->|域名匹配| R1[规则1: github.com → 开发]
    P -->|标题匹配| R2[规则2: "教程" → 学习]
    P -->|URL正则| R3[规则3: /blog/ → 博客]
    P -->|无匹配| F[进入下一分类器]
    
    R1 --> C[分类结果]
    R2 --> C
    R3 --> C
```

## 规则类型

### 1. 域名规则

基于书签域名进行精确匹配：

```yaml
# config.json
category_rules:
  开发:
    domains:
      - "github.com"
      - "gitlab.com"
      - "bitbucket.org"
      - "stackoverflow.com"
      - "dev.to"
      
  设计:
    domains:
      - "dribbble.com"
      - "behance.net"
      - "figma.com"
      - "sketch.com"
```

**优先级**：最高，一旦匹配直接返回结果。

### 2. 标题规则

基于书签标题关键词匹配：

```yaml
category_rules:
  学习:
    title_keywords:
      - "教程"
      - "入门"
      - "指南"
      - "tutorial"
      - "guide"
      - "learn"
      
  文档:
    title_keywords:
      - "文档"
      - "API"
      - "reference"
      - "docs"
```

**匹配方式**：不区分大小写的子串匹配。

### 3. URL 正则规则

基于 URL 路径的正则匹配：

```yaml
category_rules:
  博客:
    url_patterns:
      - "/blog/"
      - "/posts/"
      - "/articles/"
      - "\\d{4}/\\d{2}/"  # 日期格式
      
  新闻:
    url_patterns:
      - "/news/"
      - "/article/"
```

**编译优化**：规则在加载时预编译为正则对象。

## 规则权重

不同规则类型具有不同的优先级权重：

| 规则类型 | 权重 | 置信度 | 说明 |
|----------|------|--------|------|
| 域名规则 | 1.0 | 1.0 | 最确定，直接匹配 |
| 标题规则 | 0.9 | 0.9 | 高确定性 |
| URL 正则 | 0.8 | 0.85 | 中高确定性 |

## 实现细节

```python
class RuleEngine:
    """规则引擎实现"""
    
    def __init__(self, rules: Dict):
        self.rules = rules
        self._domain_map = self._build_domain_map(rules)
        self._compiled_patterns = self._compile_patterns(rules)
    
    def _build_domain_map(self, rules: Dict) -> Dict[str, str]:
        """构建域名到分类的映射"""
        domain_map = {}
        for category, rule in rules.items():
            for domain in rule.get("domains", []):
                domain_map[domain.lower()] = category
        return domain_map
    
    def _compile_patterns(self, rules: Dict) -> List[Tuple[Pattern, str]]:
        """预编译正则表达式"""
        patterns = []
        for category, rule in rules.items():
            for pattern in rule.get("url_patterns", []):
                compiled = re.compile(pattern, re.IGNORECASE)
                patterns.append((compiled, category))
        return patterns
    
    def classify(self, bookmark: Bookmark) -> ClassificationResult:
        """执行规则分类"""
        url = bookmark.url
        domain = self._extract_domain(url)
        
        # 1. 域名匹配（最高优先级）
        if domain in self._domain_map:
            return ClassificationResult(
                category=self._domain_map[domain],
                confidence=1.0,
                source="rule:domain",
            )
        
        # 2. 标题关键词匹配
        if result := self._match_title(bookmark):
            return result
        
        # 3. URL 正则匹配
        if result := self._match_url_pattern(url):
            return result
        
        # 无匹配，返回低置信度
        return ClassificationResult(
            category="未分类",
            confidence=0.0,
            source="rule:none",
        )
```

## 性能优化

### 域名查找优化

使用字典实现 O(1) 查找：

```python
# ❌ 慢：线性扫描
for rule in rules:
    if domain in rule.domains:
        return rule.category

# ✅ 快：字典查找
domain_map = {"github.com": "开发", "figma.com": "设计"}
return domain_map.get(domain)
```

### 正则预编译

```python
# ❌ 慢：每次编译
re.match(r"/blog/", url)

# ✅ 快：预编译缓存
COMPILED = re.compile(r"/blog/", re.IGNORECASE)
COMPILED.search(url)
```

## 规则配置最佳实践

### 层级分类

```yaml
# 使用分类层级
category_rules:
  开发:
    domains:
      - "github.com"
    subcategories:
      Python:
        title_keywords:
          - "python"
          - "django"
          - "flask"
      JavaScript:
        title_keywords:
          - "javascript"
          - "react"
          - "vue"
```

### 排除规则

```yaml
category_rules:
  开发:
    domains:
      - "medium.com"
    exclude:
      title_keywords:
        - "设计"
        - "产品"
```

## 统计指标

| 指标 | 数值 |
|------|------|
| 规则匹配率 | 60-80% |
| 平均延迟 | < 1ms |
| 内存占用 | < 5MB |

## 相关文档

- [ML 分类器](/zh/algorithms/ml-classifier) - 机器学习分类
- [融合算法](/zh/algorithms/fusion) - 多分类器融合
- [配置参考](/zh/reference/config) - 完整配置说明
