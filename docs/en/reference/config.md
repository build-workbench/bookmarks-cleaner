# Configuration Reference

<CbBadge text="Primary Config" type="tip" />

CleanBook uses a JSON configuration file (`config.json`) with full customization support.

## Configuration Structure

```json
{
  "ai_settings": { ... },      // AI processing settings
  "category_rules": { ... },   // Classification rules
  "taxonomy": { ... },         // Taxonomy configuration
  "llm": { ... },              // LLM settings
  "output": { ... },           // Output settings
  "deduplication": { ... },    // Deduplication settings
  "logging": { ... }           // Logging settings
}
```

## ai_settings

Core AI processing configuration.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `confidence_threshold` | float | 0.7 | Classification confidence threshold |
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
| `url_pattern` | Match URL regex | `^https://docs\..*\.com` |
| `url_ends_with` | Match URL suffix | `.pdf`, `.md` |

See [Custom Rules Examples](../examples/custom-rules) for detailed rule examples.

## llm

LLM configuration (optional).

```json
{
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY",
    "max_requests_per_minute": 20,
    "timeout": 30,
    "max_retries": 3
  }
}
```

## Configuration Validation

```bash
# Validate configuration file format
cleanbook --validate-config

# Show loaded configuration
cleanbook --show-config
```
