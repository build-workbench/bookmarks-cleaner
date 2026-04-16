# CleanBook Design Overview

> Goal: Implement a modern bookmark classification system based on "Controlled Vocabulary + Faceted Classification + Authority Control", following KISS principles, offline-first by default, with optional LLM integration.

## Architecture Overview

```
Input Layer    Processing Layer    Classification Layer    Output Layer
┌────────┐    ┌──────────┐        ┌──────────┐          ┌──────────┐
│ HTML   │───▶│ Parse/   │───────▶│ Multi-   │─────────▶│ HTML/    │
│ Bookmarks│    │ Dedupe   │        │ Method   │          │ Markdown/│
└────────┘    └──────────┘        │ Fusion   │          │ JSON     │
                      │                  │          └──────────┘
                      ▼                  ▼
               ┌──────────┐        ┌──────────┐
               │ YAML     │        │ Rules/ML/│
               │ Config   │        │ LLM      │
               └──────────┘        └──────────┘
```

Core flow: `BookmarkProcessor` → Batch load/dedupe → `AIBookmarkClassifier.classify()`
→ Multi-method fusion → Standardization/Organization → Export

## Classification Principles

### Controlled Vocabulary

`taxonomy/subjects.yaml` defines preferred terms and variants to avoid scattered synonyms.

```yaml
subjects:
  - preferred: "Artificial Intelligence"
    variants: ["AI", "Machine Learning", "Deep Learning"]
    icon: "🤖"
```

### Faceted Classification

- **Primary dimension**: `subject` (topic)
- **Resource type facet**: `resource_type` (e.g., `code_repository`, `documentation`, `video`)
- Final output hierarchy: `subject -> resource_type -> items`

### Authority Control

- Maintains authoritative tables in YAML format
- Version-controlled and review-friendly
- Configuration-driven, adjust classification logic without code changes

### KISS Principle

- Keep implementation simple
- YAML readable, offline by default
- Pluggable components

## Core Components

### 1. BookmarkProcessor

Coordinates the entire processing pipeline:

| Stage | Function | Description |
|-------|----------|-------------|
| Load | Parse HTML bookmark file | Uses BeautifulSoup |
| Deduplicate | URL similarity-based deduplication | Multi-dimensional similarity |
| Classify | Call AIBookmarkClassifier | Batch parallel processing |
| Organize | Organize by subject/resource_type | Standardized output structure |
| Export | Multi-format export | HTML/JSON/Markdown |

### 2. AIBookmarkClassifier

Unified classification entry point:

```python
class AIBookmarkClassifier:
    def classify(self, url: str, title: str) -> ClassificationResult:
        """
        Fuses results from multiple classification methods:
        - Rule Engine (highest priority)
        - ML Classifier (medium priority)
        - Semantic Analysis (auxiliary)
        - LLM Classification (optional, lowest priority)
        """
```

### 3. Rule Engine

Pre-compiles rules based on `config.json`:

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
  }
}
```

Supported match types: `domain`, `title`, `url`, `url_starts_with`, `url_ends_with`, `url_matches_regex`

### 4. TaxonomyStandardizer

Standardizes controlled vocabularies and facets based on `taxonomy/*.yaml`:

- `normalize_subject(text)`: Maps arbitrary text to standardized subject
- `normalize_resource_type(text)`: Maps arbitrary text to standardized resource type

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│  HTML Bookmark File                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ parse_bookmarks()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[Bookmark]                                             │
│  - url                                                      │
│  - title                                                    │
│  - add_date                                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ deduplicate()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[Bookmark] (deduplicated)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ extract_features() (parallel)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[(Bookmark, BookmarkFeatures)]                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ classify_batch()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  List[(Bookmark, ClassificationResult)]                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ organize_bookmarks()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Dict[subject, Dict[resource_type, List[Bookmark]]]          │
└──────────────────────┬──────────────────────────────────────┘
                       │ export()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  HTML / Markdown / JSON files                               │
└─────────────────────────────────────────────────────────────┘
```

## Caching Strategy

All caches use `OrderedDict` for LRU eviction:

| Cache | Location | Capacity | Description |
|-------|----------|----------|-------------|
| feature_cache | AIBookmarkClassifier | 10,000 | Bookmark feature cache |
| classification_cache | AIBookmarkClassifier | 5,000 | Classification result cache |
| _classification_cache | BookmarkProcessor | 10,000 | Processing result cache |

## Terminology

| Term | Description | Example |
|------|-------------|---------|
| subject | Primary classification dimension | AI, Python, Productivity |
| resource_type | Resource type facet | documentation, code_repository, video |
| facets | Dictionary of facet attributes | `{"resource_type_hint": "documentation"}` |
| confidence | Confidence score (0.0-1.0) | 0.95 indicates high confidence |
| method | Classification method used | rule_engine, ml_classifier, llm_classifier |

## 5-Minute Quick Start

1. **Prepare input**: Export browser bookmarks to HTML
2. **Minimal execution**:
   ```bash
   cleanbook -i bookmarks.html -o output
   ```
3. **Review output**: Check the Markdown report in `output/`
4. **Tune config**: Adjust rules in `config.json` based on results

## Extension Points

- **Classifier plugins**: `src/plugins/classifiers/`
- **Export formats**: Extend `DataExporter`
- **Rule types**: Add new match patterns in `rule_engine.py`
- **LLM prompts**: Customize `llm_prompt_builder.py`

## Design Trade-offs

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Pure Rules | High certainty, explainable | High maintenance, weak generalization | ✅ Keep as priority path |
| Pure ML | Strong generalization | Requires training data, cold start | ✅ As enhancement |
| Pure LLM | Strong understanding | High cost, latency | ✅ Optional fallback |
| Hybrid Fusion | Balances all aspects | Higher complexity | ✅ Current approach |
