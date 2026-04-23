# 配置详解

CleanBook 使用 `config.json` 作为核心配置文件。

## 配置文件位置

按以下顺序查找：
1. `--config` 指定的路径
2. 当前目录的 `config.json`
3. `~/.config/cleanbook/config.json`
4. 内置默认配置

## 快速生成配置

```bash
# 生成默认配置到当前目录
cleanbook --init-config

# 生成到指定目录
cleanbook --init-config -o ~/.config/cleanbook/
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

定义分类规则，见 [自定义规则示例](../examples/custom-rules)。

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

## 配置验证

```bash
cleanbook --validate-config
cleanbook --show-config
```
