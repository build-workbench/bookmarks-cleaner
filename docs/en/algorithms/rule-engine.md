# Rule Engine

The Rule Engine is Bookmarks Cleaner's **first line of classification**, using predefined pattern matching rules for fast, deterministic classification.

## Rule Types

### 1. Domain Rules

Based on bookmark domain exact matching:

```yaml
category_rules:
  Development:
    domains:
      - "github.com"
      - "stackoverflow.com"
      
  Design:
    domains:
      - "dribbble.com"
      - "figma.com"
```

**Priority**: Highest - returns immediately upon match.

### 2. Title Rules

Based on bookmark title keyword matching:

```yaml
category_rules:
  Learning:
    title_keywords:
      - "tutorial"
      - "guide"
      - "learn"
```

### 3. URL Regex Rules

Based on URL path regex matching:

```yaml
category_rules:
  Blog:
    url_patterns:
      - "/blog/"
      - "/posts/"
```

## Rule Weights

| Rule Type | Weight | Confidence | Description |
|-----------|--------|------------|-------------|
| Domain | 1.0 | 1.0 | Most certain |
| Title | 0.9 | 0.9 | High certainty |
| URL Regex | 0.8 | 0.85 | Medium-high certainty |

## Statistics

| Metric | Value |
|--------|-------|
| Rule match rate | 60-80% |
| Average latency | < 1ms |
| Memory usage | < 5MB |

## Related Docs

- [ML Classifier](/en/algorithms/ml-classifier) - ML classification
- [Fusion Algorithm](/en/algorithms/fusion) - Multi-classifier fusion
