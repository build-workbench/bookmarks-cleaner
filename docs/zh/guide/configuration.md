# 配置详解

CleanBook 使用 `config.json` 作为核心配置文件。

## 配置文件位置

当前维护版本只有两种方式：

1. 通过 `-c / --config` 显式指定配置文件
2. 不指定时使用内置默认配置

```bash
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## 核心配置项

### ai_settings

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,
    "use_semantic_analysis": true,
    "cache_size": 10000,
    "max_workers": 4
  }
}
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `confidence_threshold` | 分类置信度阈值 | 0.7 |
| `max_workers` | 并行处理数 | 4 |

### category_rules

分类规则是最重要的配置面。每个分类包含一组规则，支持基于域名、标题和 URL 后缀的匹配。

### llm

```json
{
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

## 配置使用方式

```bash
# 使用默认配置
cleanbook -i bookmarks.html -o output/

# 使用自定义配置
cleanbook -i bookmarks.html -o output/ -c ./config.json
```
