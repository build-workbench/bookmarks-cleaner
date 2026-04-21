# AGENTS.md - AI Agent Workflow Instructions

> This file is intended for AI coding agents. It contains technical details about project architecture, development workflow, and coding conventions.

## Project Overview

**CleanBook** (package name: `cleanbook`) is an open-source, offline-first bookmark cleaning and classification tool. It transforms chaotic browser bookmark collections into well-organized, categorized libraries using a hybrid AI approach.

### Key Characteristics

- **Architecture**: Plugin-based modular architecture with pipeline pattern
- **Classification Strategy**: Multi-layer fusion (Rule 30% + ML 25% + Semantic 20% + User Profile 10% + Optional LLM 15%)
- **Accuracy**: 91.4% classification accuracy through ensemble methods
- **Processing Speed**: ~50+ bookmarks/second
- **Privacy**: 100% offline processing, no cloud uploads required
- **Codebase Size**: ~31,000 lines of Python across 91 source files
- **License**: MIT
- **Maintainer**: LessUp (github@lessup.dev)

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **ML Framework** | scikit-learn, numpy, pandas |
| **CLI/UI** | click, rich (terminal formatting), tqdm |
| **Web Parsing** | beautifulsoup4, lxml |
| **Chinese NLP** | jieba |
| **Testing** | pytest, pytest-cov, hypothesis (property-based) |
| **Code Quality** | black, isort, flake8, mypy, pre-commit |

## Project Structure

```
bookmarks-cleaner/
├── main.py                          # Main CLI entry point (legacy)
├── pyproject.toml                   # Project metadata, dependencies, tool configs
├── config.json                      # Main configuration (rules, categories, AI settings)
├── requirements.txt                 # Runtime dependencies
├── requirements-dev.txt             # Development dependencies
│
├── src/                             # Source code (~91 Python files)
│   ├── __init__.py                  # Package root with lazy imports
│   ├── ai_classifier.py             # Central orchestrator (647 lines)
│   ├── bookmark_processor.py        # Batch processing coordinator (741 lines)
│   ├── cli_interface.py             # Interactive CLI interface
│   │
│   ├── cleanbook/                   # Modern CLI package
│   │   └── cli.py                   # Thin wrapper to main.py
│   │
│   ├── classifiers/                 # Legacy classifier modules
│   │   ├── ai.py
│   │   ├── enhanced.py
│   │   ├── llm.py
│   │   └── ml.py
│   │
│   ├── cli/                         # CLI implementations
│   │   ├── cleanbook.py
│   │   ├── enhanced.py
│   │   └── interface.py
│   │
│   ├── core/                        # Core processing logic
│   │   ├── deduplicator.py
│   │   ├── exporter.py
│   │   └── processor.py
│   │
│   ├── data/                        # Data handling
│   │   ├── deduplicator.py
│   │   └── exporter.py
│   │
│   ├── engines/                     # Processing engines
│   │   ├── rules.py                 # Rule engine (512 lines)
│   │   ├── semantic.py              # Semantic analyzer
│   │   ├── smart_loader.py          # Smart rule loader
│   │   └── url.py                   # URL analyzer
│   │
│   ├── health/                      # Health checking
│   │   ├── bookmark_checker.py
│   │   └── checker.py
│   │
│   ├── llm/                         # LLM integration
│   │   ├── exporter.py
│   │   ├── organizer.py
│   │   ├── prompt_builder.py
│   │   └── second_pass.py
│   │
│   ├── plugins/                     # Plugin system
│   │   ├── base.py                  # Plugin base classes and interfaces
│   │   ├── pipeline.py              # Execution pipeline
│   │   ├── registry.py              # Plugin registry
│   │   └── classifiers/             # Classifier plugins
│   │       ├── embedding_classifier.py
│   │       ├── llm_classifier.py
│   │       ├── ml_classifier.py
│   │       └── rule_classifier.py
│   │
│   ├── services/                    # Cross-cutting services
│   │   ├── active_learning.py       # Active learning engine
│   │   ├── confidence_calibrator.py
│   │   ├── embedding_service.py     # Transformer embeddings
│   │   ├── feature_store.py         # Feature caching
│   │   ├── incremental_trainer.py   # Online learning
│   │   ├── performance_monitor.py   # Metrics tracking
│   │   └── taxonomy_service.py      # Category management
│   │
│   └── utils/                       # Utility modules
│       ├── category.py
│       ├── clean_tidy.py
│       ├── config.py
│       ├── emoji_cleaner.py
│       ├── optimizer.py
│       ├── profiler.py
│       ├── resource_loader.py
│       ├── standardizer.py
│       └── url.py
│
├── specs/                           # Specification documents (SDD)
│   ├── product/
│   │   └── bookmark-classifier-system.md    # Product requirements
│   ├── rfc/
│   │   └── 0001-architecture-algorithm-upgrade.md  # Architecture RFC
│   ├── api/
│   ├── db/
│   └── testing/
│       └── classification-tests.md
│
├── tests/                           # Test suite (18 test files)
│   ├── test_*.py                    # Property-based and unit tests
│   ├── bookmarks/                   # Test data
│   ├── output-round-1/              # Test outputs
│   └── output-round-2/
│
├── taxonomy/                        # Taxonomy definitions
│   ├── resource_types.yaml
│   └── subjects.yaml                # Subject categories
│
├── config/                          # Configuration templates
│   ├── agent/
│   └── taxonomy/
│
├── docs/                            # VitePress documentation
│   ├── en/
│   ├── zh/
│   ├── .vitepress/
│   └── node_modules/
│
├── examples/                        # Example files
│   └── demo_bookmarks.html
│
└── models/                          # ML model storage
    └── recommendation.pkl
```

## Development Workflow

### Spec-Driven Development (SDD)

This project follows **Spec-Driven Development (SDD)** strictly. Read specs in `/specs` before writing any code:

1. **`/specs/product/`** - Product requirements and user stories
2. **`/specs/rfc/`** - Technical design documents and RFCs
3. **`/specs/api/`** - API specifications
4. **`/specs/db/`** - Database schemas
5. **`/specs/testing/`** - Test specifications

**Workflow**:
1. Review relevant specs before coding
2. For new features: Update/create specs first, wait for confirmation
3. Implement exactly to spec (no gold-plating)
4. Write tests based on spec acceptance criteria

### Build and Test Commands

```bash
# ==================== Setup ====================
# Install dependencies
pip install -r requirements.txt

# Install in development mode (creates CLI commands: cleanbook, cleanbook-wizard)
pip install -e .

# Setup pre-commit hooks
pre-commit install

# ==================== Running ====================
# Process bookmarks (CLI mode)
python main.py -i examples/demo_bookmarks.html -o output/

# Interactive mode
python main.py --interactive

# With ML training
python main.py -i bookmarks.html --train

# Batch processing with custom settings
python main.py -i file1.html file2.html -o results/ --workers 8 --threshold 0.8

# Health check
python main.py --health-check

# Debug mode (with limit)
python main.py -i bookmarks.html --log-level DEBUG --limit 100

# Disable ML to save memory
python main.py -i bookmarks.html --no-ml

# ==================== Testing ====================
# Run full test suite
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test with verbose output
pytest -v tests/test_rule_engine.py

# Run property-based tests only
pytest -m property

# ==================== Code Quality ====================
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```

### CLI Entry Points

| Command | Source | Description |
|---------|--------|-------------|
| `cleanbook` | `src.cleanbook.cli:main` | Main CLI (pipx installable) |
| `cleanbook-wizard` | `src.enhanced_cli:main` | Interactive wizard mode |
| `python main.py` | `main.py` | Development entry point |

## Code Style Guidelines

### Python Style

- **Formatter**: black with line-length 88
- **Import Sorting**: isort with black profile
- **Linter**: flake8 (max-line 120, select E9,F63,F7,F82)
- **Type Checker**: mypy (Python 3.10 target, warn on any return)
- **Docstrings**: Required for all public functions and classes
- **Type Hints**: Use throughout codebase

### Code Structure

```python
# Example function following project conventions
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def process_bookmarks(
    bookmarks: List[dict],
    config: Dict,
    max_workers: int = 4,
) -> Dict[str, int]:
    """Process bookmarks with parallel execution.

    处理书签并执行并行分类。

    Args:
        bookmarks: List of bookmark dicts with 'url' and 'title'
        config: Configuration dictionary with category rules
        max_workers: Number of parallel workers (default: 4)

    Returns:
        Dict mapping category names to bookmark counts

    Raises:
        ValueError: If bookmarks is empty or config missing category_rules
    """
    if not bookmarks:
        raise ValueError("书签列表不能为空")

    # Implementation follows...
    pass
```

### Comments and Documentation

- Comments explain **why**, not **what**
- Docstrings required for all public APIs
- Mixed Chinese/English codebase (accept both in comments)
- Use `logger` for runtime info, not print statements

## Testing Strategy

### Test Organization

| Test Type | Location | Framework | Purpose |
|-----------|----------|-----------|---------|
| Unit Tests | `tests/test_*.py` | pytest | Component behavior |
| Property Tests | `tests/test_*_properties.py` | hypothesis | Invariant validation |
| Integration | `tests/test_suite.py` | pytest | End-to-end flows |

### Property-Based Testing

Tests verify universal properties using Hypothesis:

```python
from hypothesis import given, strategies as st

@given(confidence=st.floats(min_value=0.0, max_value=1.0))
def test_confidence_always_normalized(confidence):
    """Confidence scores must always be in [0, 1] range."""
    result = calibrator.calibrate(confidence)
    assert 0.0 <= result <= 1.0
```

### Running Tests

```bash
# Quick test (runtime paths)
pytest -q tests/test_runtime_paths.py

# Full test suite
pytest -q

# With coverage report
pytest --cov=src --cov-report=html

# Skip slow tests
pytest -m "not slow"

# Run only property tests
pytest -m property
```

## Configuration System

### Main Config (`config.json`)

```json
{
  "ai_settings": {
    "confidence_threshold": 0.4,
    "use_semantic_analysis": true,
    "use_user_profiling": true,
    "cache_size": 10000,
    "max_workers": 4,
    "enable_learning": true
  },
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key_env": "OPENAI_API_KEY"
  },
  "category_rules": {
    "💻 编程": {
      "rules": [
        {"match": "domain", "keywords": ["github.com"], "weight": 20},
        {"match": "title", "keywords": ["python", "rust"], "weight": 10}
      ]
    }
  },
  "taxonomy": {
    "subjects_file": "taxonomy/subjects.yaml",
    "resource_types_file": "taxonomy/resource_types.yaml"
  }
}
```

### Rule Types

- `match: domain` - Match URL domain patterns
- `match: title` - Match bookmark title keywords
- `match: url_ends_with` - Match URL suffixes (e.g., `.pdf`)
- `match_all_keywords_in` - Require all keywords to match

## Plugin Architecture

### Creating a New Classifier

1. Create file in `src/plugins/classifiers/your_classifier.py`
2. Inherit from `ClassifierPlugin` in `src/plugins/base.py`
3. Implement required methods:
   - `metadata` property (return `PluginMetadata`)
   - `classify(features)` (return `ClassificationResult` or `None`)
   - `initialize(config)` (return bool success)
   - `shutdown()`

```python
from src.plugins.base import ClassifierPlugin, PluginMetadata, ClassificationResult

class MyClassifier(ClassifierPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_classifier",
            version="1.0.0",
            capabilities=["fast", "rule-based"],
            priority=50  # Lower = higher priority
        )

    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        # Implementation
        return ClassificationResult(
            category="编程",
            confidence=0.95,
            method="my_classifier"
        )

    def initialize(self, config: Dict) -> bool:
        return True

    def shutdown(self) -> None:
        pass
```

### Data Types

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

@dataclass
class ClassificationResult:
    category: str
    confidence: float  # 0.0 - 1.0
    subcategory: Optional[str] = None
    method: str = "unknown"
    reasoning: List[str] = field(default_factory=list)
```

## Security Considerations

- **No secrets in code**: API keys from environment variables only
- **Input validation**: Validate all bookmark data before processing
- **URL sanitization**: Use `urllib.parse` for URL handling
- **File permissions**: Output files use 644 permissions
- **No network calls in core**: ML/models work offline by default

## Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `src/ai_classifier.py` | Central orchestrator | 647 |
| `src/bookmark_processor.py` | Batch processing coordinator | 741 |
| `src/engines/rules.py` | Rule engine | 512 |
| `src/plugins/base.py` | Plugin interfaces | 187 |
| `specs/rfc/0001-architecture-algorithm-upgrade.md` | Architecture RFC | 335 |

## Common Development Tasks

### Adding Classification Rules

Edit `config.json` → `category_rules` section. No code changes needed.

### Adding a New Export Format

1. Add method to `src/data/exporter.py`
2. Update `BookmarkProcessor.export_results()`
3. Handle in CLI arguments

### Debugging Classification Issues

```bash
# Run with debug logging
python main.py -i bookmarks.html --log-level DEBUG --limit 100

# Check health of all components
python main.py --health-check
```

## Pre-commit Hooks

Configured hooks (see `.pre-commit-config.yaml`):

1. **Basic checks**: trailing-whitespace, end-of-file-fixer, check-yaml, check-json
2. **Security**: detect-private-key, check-added-large-files
3. **Formatting**: black (88 char lines)
4. **Import sorting**: isort (black profile)
5. **Linting**: flake8
6. **Type checking**: mypy (optional, can be slow)

## Dependencies

### Runtime (requirements.txt)

- beautifulsoup4>=4.12.3 (HTML parsing)
- lxml>=5.2.2 (XML/HTML processing)
- numpy>=1.26.4 (numerical computing)
- scikit-learn>=1.4.2 (machine learning)
- jieba>=0.42.1 (Chinese text segmentation)
- langdetect>=1.0.9 (language detection)
- matplotlib>=3.9.0, seaborn>=0.13.2 (visualization)
- pandas>=2.2.2 (data processing)
- requests>=2.32.3 (HTTP requests)
- tqdm>=4.66.4 (progress bars)
- click>=8.1.7 (CLI framework)
- psutil>=6.0.0 (system monitoring)
- joblib>=1.4.2 (parallel processing)
- watchdog>=4.0.2 (file monitoring)
- pyyaml>=6.0.2 (YAML parsing)
- jsonschema>=4.23.0 (JSON validation)
- rich>=13.7.1 (terminal formatting)

### Development (requirements-dev.txt)

- black>=24.4.2 (formatting)
- flake8>=7.0.0 (linting)
- mypy>=1.10.0 (type checking)
- types-requests, types-PyYAML (type stubs)
- pytest>=8.2.2 (testing)
- pytest-cov>=5.0.0 (coverage)
- hypothesis>=6.0.0 (property-based testing)

## External Resources

- **Documentation**: https://lessup.github.io/bookmarks-cleaner/
- **Repository**: https://github.com/LessUp/bookmarks-cleaner
- **Issues**: https://github.com/LessUp/bookmarks-cleaner/issues
- **Changelog**: https://github.com/LessUp/bookmarks-cleaner/blob/master/CHANGELOG.md

---

*Last updated: 2026-04-17*
