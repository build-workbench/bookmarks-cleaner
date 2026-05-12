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
| `confidence_threshold` | float | 0.4 | Classification confidence threshold; below this = "unclassified" |
| `use_semantic_analysis` | boolean | true | Enable semantic analysis |
| `use_user_profiling` | boolean | true | Enable user profile analysis |
| `cache_size` | integer | 10000 | URL feature cache size |
| `max_workers` | integer | 4 | Number of parallel workers |
| `enable_learning` | boolean | true | Enable incremental learning |

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

Classification rules are the core of CleanBook. Each category can contain multiple matching rules.

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| `domain` | Match domain | `github.com`, `*.github.io` |
| `title` | Match title keywords | `python`, `tutorial` |
| `url_ends_with` | Match URL suffix | `.pdf`, `.md` |
| `match_all_keywords_in` | Require all keywords in title or URL | `["python", "asyncio"]` |

### Rule Configuration Example

```json
{
  "category_rules": {
    "💻 Programming/Python": {
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
      "description": "Python related resources"
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
    "📚 Documentation": {
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

### Weight System

- Each rule can have a `weight` (1-100)
- Multiple rules' weights accumulate
- Must exceed `confidence_threshold` to be assigned
- Category with highest weight wins

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

Configuration for classification vocabulary and synonyms.

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

| Field | Description |
|-------|-------------|
| `enable` | Enable LLM classification |
| `provider` | Provider name, e.g. `openai` |
| `model` | Model name |
| `api_key_env` | Environment variable name for API key |

## Usage

```bash
# Use built-in defaults
cleanbook -i bookmarks.html -o output/

# Use explicit config file
cleanbook -i bookmarks.html -o output/ -c ./config.json
```

## Complete Example

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
    "💻 Programming": {
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
    "🎨 Design": {
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

## Next Steps

- [Taxonomy Format](./taxonomy) — Learn about YAML vocabulary configuration
- [Configuration Guide](/en/guide/configuration) — Understand config override and common fields
