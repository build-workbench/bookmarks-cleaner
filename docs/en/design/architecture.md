# System Architecture

> Last Updated: 2026-04-16

## Architecture Overview

CleanBook adopts a layered architecture design, implementing an offline-first bookmark cleaning and classification system.

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface Layer                   │
│         CLI (cleanbook / cleanbook-wizard)                  │
├─────────────────────────────────────────────────────────────┤
│                      Business Logic Layer                   │
│      BookmarkProcessor / DataExporter / Deduplicator        │
├─────────────────────────────────────────────────────────────┤
│                      Classification Engine Layer            │
│   AIBookmarkClassifier + Plugin Pipeline (Rules/ML/LLM)     │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                          │
│   TaxonomyService / EmbeddingService / FeatureStore         │
├─────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                   │
│   ConfigManager / ResourceLoader / PerformanceMonitor       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Classification System

#### AIBookmarkClassifier (`src/ai_classifier.py`)

Unified classification entry point, integrating multiple classification strategies:

- **Input**: URL + Title
- **Output**: ClassificationResult (category, confidence, reasoning)
- **Features**:
  - Multi-method fusion (Rule Engine, ML, Semantic Analysis, User Profile, LLM)
  - LRU cache optimization (feature_cache, classification_cache)
  - Supports online learning (learn_from_feedback)

**Core Methods**:

```python
class AIBookmarkClassifier:
    def classify(self, url: str, title: str) -> ClassificationResult:
        """Main classification entry"""
        
    def _ensemble_classification(self, results: List[ClassificationResult]) -> ClassificationResult:
        """Weighted voting fusion of multi-method results"""
```

#### Plugin Pipeline System (`src/plugins/`)

Modular classifier architecture:

| Plugin | File | Priority | Description |
|--------|------|----------|-------------|
| RuleClassifier | `classifiers/rule_classifier.py` | 10 (Highest) | Rule-based fast classification |
| MLClassifier | `classifiers/ml_classifier.py` | 50 | Machine learning classification |
| EmbeddingClassifier | `classifiers/embedding_classifier.py` | 50 | Semantic embedding classification |
| LLMClassifier | `classifiers/llm_classifier.py` | 90 (Lowest) | LLM classification (optional) |

### Data Structures

#### BookmarkFeatures

```python
@dataclass
class BookmarkFeatures:
    url: str
    title: str
    domain: str
    path_segments: List[str]
    query_params: Dict[str, str]
    content_type: str
    language: str
    timestamp: datetime
```

#### ClassificationResult (Unified Definition)

```python
@dataclass
class ClassificationResult:
    category: str                           # Main category
    confidence: float                       # Confidence (0.0-1.0)
    subcategory: Optional[str] = None       # Sub-category
    reasoning: List[str] = field(default_factory=list)
    alternatives: List[Tuple[str, float]] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "unknown"
    facets: Dict[str, str] = field(default_factory=dict)
```

> **Important**: ClassificationResult is defined in `src/ai_classifier.py`, other modules should import from there.

### Processing Flow

```
HTML Bookmarks → Parse → Extract Features → Deduplicate → Classify → Organize → Export
                   ↓            ↓               ↓           ↓
              BeautifulSoup  URL/Title     Domain Group  Plugin Pipeline
```

#### Detailed Flow

1. **Parsing**: `BeautifulSoup` parses HTML, extracts `<a>` tags
2. **Feature Extraction**: Parse URL components, detect language and content type
3. **Deduplication**: URL normalization and similarity-based deduplication
4. **Classification**: Try each classifier through plugin pipeline
5. **Organization**: Organize by `subject -> resource_type` two levels
6. **Export**: Generate HTML/Markdown/JSON output

## Performance Optimization

### Caching Strategy

All caches use OrderedDict for LRU eviction:

| Cache | Location | Max Capacity | Description |
|-------|----------|--------------|-------------|
| feature_cache | AIBookmarkClassifier | 10,000 | Bookmark features |
| classification_cache | AIBookmarkClassifier | 5,000 | Classification results |
| _classification_cache | BookmarkProcessor | 10,000 | Processing results |

### Pre-compiled Regex

Common regex patterns are pre-compiled at module level:

```python
# src/ai_classifier.py, src/llm_classifier.py, src/ml_classifier.py
_CHINESE_REGEX = re.compile(r'[\u4e00-\u9fff]')
_ENGLISH_REGEX = re.compile(r'[a-zA-Z]')
_DIGIT_REGEX = re.compile(r'\d')
```

### Parallel Processing

- Use ThreadPoolExecutor for parallel bookmark processing
- Separate file loading from classification
- Batch export parallelization

## Configuration System

### Configuration Loading Priority

1. Explicit config path (`--config`)
2. `config.json` in current directory
3. Built-in default configuration

### Configuration Structure

```json
{
  "category_rules": { ... },      // Classification rules
  "priority_rules": { ... },      // Priority rules
  "category_order": [ ... ],      // Category ordering
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000,
    "max_workers": 4
  },
  "llm": {                        // LLM configuration (optional)
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

## Plugin Development

### Creating a New Classifier

1. Inherit from `ClassifierPlugin` base class
2. Implement required methods: `classify()`, `initialize()`, `shutdown()`
3. Create file in `src/plugins/classifiers/`
4. Register in `registry.py`

### Example

```python
from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures

class MyClassifier(ClassifierPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_classifier",
            version="1.0.0",
            capabilities=["custom"],
            priority=50
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def shutdown(self) -> None:
        pass
    
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        # Implement classification logic
        return ClassificationResult(
            category="Result",
            confidence=0.9,
            method="my_classifier"
        )
```

## Error Handling

- Classification failures automatically fall back to next priority classifier
- Return default classification result when all classifiers fail
- Use built-in default configuration when config errors occur

## Extension Points

- **Classifier plugins**: Add new classification strategies
- **Export formats**: Extend DataExporter
- **Rule types**: Add new match patterns in rule_engine.py
- **LLM prompts**: Customize llm_prompt_builder.py
