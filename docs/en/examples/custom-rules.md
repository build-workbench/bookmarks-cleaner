# Custom Rules Examples

Define your own classification logic in `config.json`.

## Basic Rule Structure

```json
{
  "category_rules": {
    "Category Name": {
      "rules": [
        {
          "match": "match_type",
          "keywords": ["keyword1", "keyword2"],
          "weight": weight_value
        }
      ]
    }
  }
}
```

## Example 1: Developer Documentation

```json
{
  "category_rules": {
    "📚 Documentation": {
      "rules": [
        {"match": "domain", "keywords": ["docs.python.org"], "weight": 20},
        {"match": "domain", "keywords": ["developer.mozilla.org"], "weight": 20},
        {"match": "title", "keywords": ["documentation", "docs", "API"], "weight": 12}
      ]
    }
  }
}
```

## Example 2: Tech Stack Categories

```json
{
  "category_rules": {
    "⚛️ React": {
      "rules": [
        {"match": "domain", "keywords": ["react.dev"], "weight": 20},
        {"match": "title", "keywords": ["react", "redux", "next.js"], "weight": 15}
      ]
    },
    "🐹 Go": {
      "rules": [
        {"match": "domain", "keywords": ["go.dev", "golang.org"], "weight": 20},
        {"match": "title", "keywords": ["golang", "go module"], "weight": 15}
      ]
    }
  }
}
```

## Weight Guidelines

| Weight | Description | Usage |
|--------|-------------|-------|
| 20 | Absolute match | Specific domains |
| 15 | Strong match | Official docs |
| 10 | Standard match | Keywords |
| 5 | Weak match | Auxiliary |

## Testing Rules

```bash
# Test mode with verbose output
cleanbook -i test-bookmarks.html -o output/ --dry-run --verbose
```
