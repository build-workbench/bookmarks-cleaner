# Configuration

CleanBook uses `config.json` as the core configuration file.

## Config File Location

The maintained closeout build supports two modes:

1. Pass an explicit path with `-c / --config`
2. Omit `-c` and use the built-in default config

```bash
# Use the packaged default config
cleanbook -i bookmarks.html -o output/

# Use an explicit config file
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## Core Settings

```bash
# Run a health check before editing rules
cleanbook --health-check
```

### ai_settings

```json
{
  "ai_settings": {
    "confidence_threshold": 0.4,
    "use_semantic_analysis": true,
    "use_user_profiling": true,
    "cache_size": 10000,
    "max_workers": 4,
    "enable_learning": true
  }
}
```

### category_rules

`category_rules` is the main customization surface. Each category contains one or more rules with a `match`, a list of `keywords`, and an optional `weight`.

```json
{
  "category_rules": {
    "💻 Programming/Python": {
      "rules": [
        { "match": "domain", "keywords": ["python.org", "pypi.org"], "weight": 15 },
        { "match": "title", "keywords": ["django", "flask", "fastapi"], "weight": 10 }
      ]
    }
  }
}
```

Supported match styles in the maintained config are:

- `domain`
- `title`
- `url_ends_with`
- `match_all_keywords_in`

### taxonomy

```json
{
  "taxonomy": {
    "subjects_file": "taxonomy/subjects.yaml",
    "resource_types_file": "taxonomy/resource_types.yaml"
  }
}
```

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

`llm.enable` defaults to `false`, so the repository works without any external LLM setup.
