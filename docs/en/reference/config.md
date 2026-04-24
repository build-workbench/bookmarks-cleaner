# Configuration Reference

<CbBadge text="Primary Config" type="tip" />

CleanBook uses a JSON configuration file (`config.json`) with full customization support.

## Configuration Structure

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

Core AI processing configuration.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `confidence_threshold` | float | 0.4 | Classification confidence threshold |
| `use_semantic_analysis` | boolean | true | Enable semantic analysis |
| `use_user_profiling` | boolean | true | Enable user profile analysis |
| `cache_size` | integer | 10000 | URL feature cache size |
| `max_workers` | integer | 4 | Number of parallel workers |
| `enable_learning` | boolean | true | Enable incremental learning |

## category_rules

Classification rules are the core of CleanBook. Each category can contain multiple matching rules.

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| `domain` | Match domain | `github.com`, `*.github.io` |
| `title` | Match title keywords | `python`, `tutorial` |
| `url_ends_with` | Match URL suffix | `.pdf`, `.md` |
| `match_all_keywords_in` | Require all keywords in title or URL | `["python", "asyncio"]` |

Category rules are the main customization surface. Each category contains one or more rules, usually based on domain, title keywords, or URL suffixes.

## title_cleaning_rules

This section normalizes noisy bookmark titles before classification.

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

```json
{
  "taxonomy": {
    "subjects_file": "taxonomy/subjects.yaml",
    "resource_types_file": "taxonomy/resource_types.yaml"
  }
}
```

## llm

LLM configuration (optional).

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

## How to use a config file

```bash
# Use built-in defaults
cleanbook -i bookmarks.html -o output/

# Use an explicit config file
cleanbook -i bookmarks.html -o output/ -c ./config.json
```
