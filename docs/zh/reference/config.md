# 配置参考

<CbBadge text="主要配置" type="tip" />

CleanBook 的配置文件 `config.json` 采用 JSON 格式，支持完整的自定义。

## 配置结构概览

```json
{
  "show_confidence_indicator": false,
  "ai_settings": { ... },
  "llm": { ... },
  "title_cleaning_rules": { ... },
  "taxonomy": { ... },
  "processing_order": [ ... ],
  "category_order": [ ... ],
  "domain_grouping_rules": { ... },
  "priority_rules": { ... },
  "category_rules": { ... }
}
```

## ai_settings

AI 处理相关的核心配置。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `confidence_threshold` | float | 0.4 | 分类置信度阈值，低于此值视为"未分类" |
| `use_semantic_analysis` | boolean | true | 是否启用语义分析 |
| `use_user_profiling` | boolean | true | 是否启用用户画像分析 |
| `cache_size` | integer | 10000 | URL 特征缓存大小 |
| `max_workers` | integer | 4 | 并行处理数 |
| `enable_learning` | boolean | true | 是否启用增量学习 |

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,
    "use_semantic_analysis": true,
    "use_user_profiling": true,
    "cache_size": 10000,
    "max_workers": 4,
    "enable_learning": true
  }
}
```

## category_rules

分类规则是 CleanBook 的核心功能。每个分类可以包含多个匹配规则。

### 规则类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `domain` | 匹配域名 | `github.com`, `*.github.io` |
| `title` | 匹配标题关键词 | `python`, `tutorial` |
| `url_ends_with` | 匹配 URL 后缀 | `.pdf`, `.md` |
| `match_all_keywords_in` | 所有关键词都必须命中 | `["python", "asyncio"]` |

### 规则配置示例

```json
{
  "category_rules": {
    "💻 编程/Python": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["python.org", "pypi.org", "readthedocs.io"],
          "weight": 15
        },
        {
          "match": "title",
          "keywords": ["python", "django", "flask", "fastapi", "pip"],
          "weight": 10,
          "require_all": false
        }
      ],
      "description": "Python 相关资源"
    },
    "🤖 AI/ML": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["huggingface.co", "pytorch.org", "tensorflow.org"],
          "weight": 20
        },
        {
          "match": "title",
          "keywords": ["machine learning", "deep learning", "neural network", "LLM"],
          "weight": 12
        }
      ]
    },
    "📚 文档": {
      "rules": [
        {
          "match": "url_ends_with",
          "patterns": ["/docs", "/documentation", ".pdf"],
          "weight": 8
        }
      ]
    }
  }
}
```

### 权重系统

- 每条规则可以设置 `weight`（1-100）
- 多个规则的权重累加
- 超过 `confidence_threshold` 才分配分类
- 权重最高的分类胜出

## title_cleaning_rules

这个配置段用于在分类前清洗标题噪声。

```json
{
  "title_cleaning_rules": {
    "prefixes": ["Sign in ·"],
    "suffixes": ["· GitHub"],
    "replacements": {
      "(7条消息)": ""
    }
  }
}
```

## taxonomy

词表配置用于管理分类体系和同义词。

```json
{
  "taxonomy": {
    "subjects_file": "taxonomy/subjects.yaml",
    "resource_types_file": "taxonomy/resource_types.yaml"
  }
}
```

## llm

LLM 相关配置（可选）。

```json
{
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.0,
    "top_p": 1.0,
    "timeout_seconds": 25,
    "max_retries": 1
  }
}
```

| 字段 | 说明 |
|------|------|
| `enable` | 是否启用 LLM 分类 |
| `provider` | 提供商，例如 `openai` |
| `model` | 模型名称 |
| `api_key_env` | 存储 API Key 的环境变量名 |

## 使用方式

```bash
# 使用默认配置
cleanbook -i bookmarks.html -o output/

# 显式指定配置
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## 完整示例

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,
    "use_semantic_analysis": true,
    "use_user_profiling": true,
    "cache_size": 10000,
    "max_workers": 4,
    "enable_learning": true
  },
  "category_rules": {
    "💻 编程": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["github.com", "stackoverflow.com", "gitlab.com"],
          "weight": 20
        },
        {
          "match": "title",
          "keywords": ["programming", "developer", "code", "github"],
          "weight": 8
        }
      ]
    },
    "🎨 设计": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["figma.com", "dribbble.com", "behance.net"],
          "weight": 20
        }
      ]
    }
  },
  "taxonomy": {
    "subjects_file": "taxonomy/subjects.yaml",
    "resource_types_file": "taxonomy/resource_types.yaml"
  },
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY"
  },
  "show_confidence_indicator": false
}
```

## 下一步

- [词表格式](./taxonomy) — 了解 YAML 词表配置
- [配置指南](/zh/guide/configuration) — 理解配置覆盖方式与常用字段
