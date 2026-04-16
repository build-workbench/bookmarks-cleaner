# Quick Start

CleanBook is a command-line tool for cleaning and classifying browser bookmarks.
It supports rules + machine learning + optional LLM classification,
working offline by default.

## Installation

### Recommended: pipx (Isolated Environment)

```bash
# Install pipx (if not already installed)
python -m pip install --user pipx
python -m pipx ensurepath

# Install CleanBook
pipx install cleanbook
```

### Alternative: pip

```bash
pip install cleanbook
```

### From Source

```bash
# Clone and run directly
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
python main.py --help
```

## Command Entry Points

| Command | Description |
|---------|-------------|
| `cleanbook` | Command-line processing (equivalent to `python main.py`) |
| `cleanbook-wizard` | Interactive wizard (Rich-based menu interface) |

## Minimal Example

```bash
# Process a single bookmark HTML file
cleanbook -i examples/demo_bookmarks.html -o output

# Process and train ML model
cleanbook -i examples/demo_bookmarks.html --train

# Interactive wizard mode
cleanbook-wizard

# Health check
cleanbook --health-check
```

## Common Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-i, --input` | Input file or glob pattern | Required |
| `-o, --output` | Output directory | `output` |
| `--workers` | Number of parallel threads | 4 |
| `--threshold` | Classification confidence threshold | 0.7 |
| `--train` | Enable ML training | Off |
| `--no-ml` | Disable ML classification | Off |
| `--limit N` | Limit processing count (debug) | Unlimited |
| `--health-check` | System health check | - |
| `--log-level` | Log level | INFO |

## Output Formats

| Format | Filename | Purpose |
|--------|----------|---------|
| HTML | `bookmarks_*.html` | Import to browser (Netscape format) |
| JSON | `bookmarks_*.json` | Further processing, data analysis |
| Markdown | `report_*.md` | Knowledge base archiving, documentation |

## LLM Classification (Optional)

Disabled by default. Follows the "use if available, fallback automatically" principle.

### Configuration Steps

1. Edit `config.json`:

```json
{
  "llm": {
    "enable": true,
    "provider": "openai",
    "base_url": "https://api.openai.com",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.0,
    "timeout_seconds": 25
  }
}
```

2. Set environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"

# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"

# Windows CMD
set OPENAI_API_KEY=your-api-key
```

> **Note**: If API key is not set or call fails, the system automatically
> falls back to offline classification without interrupting processing.

## Classification Strategy

CleanBook adopts a multi-level classification strategy:

```
┌─────────────────────────────────────────┐
│  1. Rule Engine (Highest Priority)      │
│     - Domain matching, keywords, paths  │
├─────────────────────────────────────────┤
│  2. Machine Learning (Medium Priority)  │
│     - Random Forest, SVM, Naive Bayes   │
├─────────────────────────────────────────┤
│  3. Semantic Analysis (Auxiliary)       │
│     - Word vector similarity, TF-IDF    │
├─────────────────────────────────────────┤
│  4. LLM Classification (Optional)       │
│     - OpenAI-compatible API             │
└─────────────────────────────────────────┘
```

### Classification Fusion Mechanism

The system uses weighted voting to fuse results from multiple classification methods:

```
Rule Engine × 0.3 + ML Classifier × 0.25 + Semantic × 0.2 + User Profile × 0.1 + LLM × 0.15
```

Each method's confidence is calibrated by historical accuracy, producing the final classification result.

## Configuration Guide

### config.json Core Structure

```json
{
  "category_rules": {
    "Technology/Programming": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["github.com", "stackoverflow.com"],
          "weight": 15
        }
      ]
    }
  },
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000,
    "max_workers": 4
  },
  "llm": {
    "enable": false
  }
}
```

### Custom Vocabularies

Maintain YAML format controlled vocabularies in `taxonomy/` directory:

- `subjects.yaml` - Subject vocabulary (e.g., AI, Python, Productivity)
- `resource_types.yaml` - Resource type vocabulary (e.g., documentation, video)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Emoji overlay in output titles | Use latest version, check `show_confidence_indicator` config |
| LLM calls not working | Check `llm.enable` and environment variables, fallback is automatic |
| Package installation errors | Use `pipx install .` or `python -m pip install .` |
| Out of memory | Use `--no-ml` to disable ML, or reduce `--workers` |
| Classification results unsatisfactory | Adjust `--threshold` parameter, or customize rules |

## Next Steps

- [Best Practices](/en/guide/best-practices) - Learn how to build an efficient bookmark classification system
- [System Architecture](/en/design/architecture) - Understand CleanBook's internal workings
- [Development Guide](/en/guide/development) - Learn how to extend and contribute
