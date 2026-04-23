# 配置参考

<CbBadge text="主要配置" type="tip" />

CleanBook 的配置文件 `config.json` 采用 JSON 格式，支持完整的自定义。

## 配置结构概览

```json
{
  "ai_settings": { ... },      // AI 处理设置
  "category_rules": { ... },   // 分类规则
  "taxonomy": { ... },         // 词表配置
  "llm": { ... },              // LLM 设置
  "output": { ... },           // 输出设置
  "deduplication": { ... },    // 去重设置
  "logging": { ... }           // 日志设置
}
```

## ai_settings

AI 处理相关的核心配置。

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `confidence_threshold` | float | 0.7 | 分类置信度阈值，低于此值视为"未分类" |
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
| `url_pattern` | 匹配 URL 正则 | `^https://docs\..*\.com` |
| `url_ends_with` | 匹配 URL 后缀 | `.pdf`, `.md` |

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

## taxonomy

词表配置用于管理分类体系和同义词。

```json
{
  "taxonomy": {
    "subjects_file": "config/taxonomy/subjects.yaml",
    "resource_types_file": "config/taxonomy/resource_types.yaml",
    "enable_auto_taxonomy": true
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
    "max_requests_per_minute": 20,
    "timeout": 30,
    "max_retries": 3,
    "prompt_template": "default"
  }
}
```

| 字段 | 说明 |
|------|------|
| `enable` | 是否启用 LLM 分类 |
| `provider` | 提供商: `openai`, `anthropic`, `local` |
| `model` | 模型名称 |
| `api_key_env` | 存储 API Key 的环境变量名 |
| `max_requests_per_minute` | 每分钟最大请求数（限流） |

## output

输出格式配置。

```json
{
  "output": {
    "formats": ["html", "json", "markdown"],
    "html": {
      "template": "default",
      "include_favicons": false,
      "group_by_category": true
    },
    "json": {
      "pretty": true,
      "include_metadata": true
    },
    "markdown": {
      "include_toc": true,
      "max_depth": 3
    }
  }
}
```

## deduplication

去重算法配置。

```json
{
  "deduplication": {
    "enabled": true,
    "url_normalization": true,
    "similarity_threshold": 0.85,
    "methods": ["exact", "fuzzy"]
  }
}
```

| 字段 | 说明 |
|------|------|
| `url_normalization` | URL 规范化（HTTP→HTTPS, www 移除等） |
| `similarity_threshold` | 模糊匹配相似度阈值 |
| `methods` | 去重方法: `exact`, `fuzzy`, `semantic` |

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
  "output": {
    "formats": ["html", "json"]
  },
  "deduplication": {
    "enabled": true,
    "similarity_threshold": 0.85
  },
  "logging": {
    "level": "INFO",
    "file": null
  }
}
```

## 配置验证

```bash
# 验证配置文件格式
cleanbook --validate-config

# 检查配置是否正确加载
cleanbook --show-config
```

## 配置热重载

开发模式下支持配置热重载：

```bash
cleanbook -i bookmarks.html --watch
```

修改 `config.json` 后会自动重新处理。

## 环境变量覆盖

部分配置可通过环境变量覆盖：

| 环境变量 | 对应配置 |
|----------|----------|
| `CLEANBOOK_CONFIG` | 配置文件路径 |
| `CLEANBOOK_LOG_LEVEL` | 日志级别 |
| `CLEANBOOK_CACHE_DIR` | 缓存目录 |
| `OPENAI_API_KEY` | LLM API Key |

## 下一步

- [词表格式](./taxonomy) — 了解 YAML 词表配置
- [架构设计](../design/architecture) — 理解配置系统的设计
