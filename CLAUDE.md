# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode (creates CLI commands: cleanbook, cleanbook-wizard)
pip install -e .

# Run interactive mode
python main.py --interactive
python main.py -i examples/demo_bookmarks.html

# Health check
python main.py --health-check
```

### Testing
```bash
# Run focused runtime tests
pytest -q tests/test_runtime_paths.py

# Run broader test suite
pytest -q

# Test with sample data
python main.py -i examples/demo_bookmarks.html -o output/
python main.py -i examples/demo_bookmarks.html --train
```

### Development Workflow
```bash
# Process bookmarks with ML training
python main.py -i bookmarks.html --train

# Batch process with custom settings
python main.py -i file1.html file2.html -o results/ --workers 8 --threshold 0.8

# Debug mode
python main.py -i bookmarks.html --log-level DEBUG --limit 100

# Disable ML to save memory
python main.py -i bookmarks.html --no-ml
```

## Architecture Overview

This is an AI-powered bookmark classification system with a plugin-based architecture. The system uses a **pipeline pattern** where multiple classifiers process bookmarks and results are fused.

### Core Components

1. **Main Entry**: `main.py` - Handles CLI parsing and delegates to components
2. **AI Classifier**: `src/ai_classifier.py` - Central orchestrator that manages multiple classification strategies
3. **Bookmark Processor**: `src/bookmark_processor.py` - Coordinates batch processing, parallelization, and I/O
4. **Plugin System**: `src/plugins/` - Modular classifiers with registry pattern
   - `rule_classifier.py` - Fast pattern matching (domain, title, URL)
   - `ml_classifier.py` - scikit-learn based ML classification
   - `embedding_classifier.py` - Semantic similarity using embeddings
   - `llm_classifier.py` - Optional LLM integration (OpenAI-compatible)
5. **Services Layer**: `src/services/` - Cross-cutting concerns
   - Active learning, taxonomy standardization, embedding service, performance monitoring

### Data Flow Pattern

```
HTML Bookmark → BookmarkFeatures (dataclass) → Plugin Pipeline → ClassificationResult (dataclass) → Exporter
                    ↓
              Parallel Processing (ThreadPoolExecutor)
                    ↓
              Result Fusion (weighted voting by confidence)
```

### Key Design Patterns

- **Plugin Registry**: Classifiers are registered in `src/plugins/registry.py` and discovered dynamically
- **Lazy Loading**: Components are initialized on first use to minimize startup time
- **Fallback Chain**: If ML fails, system falls back to rule-based classification
- **Confidence Scoring**: All classifiers return confidence scores (0.0-1.0) for result fusion
- **Caching**: LRU cache for repeated classifications and URL validation

## Project Structure

```
├── main.py                    # CLI entry point
├── pyproject.toml             # Project metadata, CLI scripts
├── config.json                # Main configuration (rules, categories, ML settings)
├── src/
│   ├── ai_classifier.py      # Orchestrates classification pipeline
│   ├── bookmark_processor.py  # Batch processing coordinator
│   ├── plugins/
│   │   ├── pipeline.py        # Execution pipeline
│   │   ├── registry.py        # Plugin registration
│   │   └── classifiers/       # Individual classifier plugins
│   └── services/
│       ├── embedding_service.py
│       ├── taxonomy_service.py
│       └── performance_monitor.py
├── tests/                     # Property-based tests (Hypothesis)
└── examples/                  # Demo bookmark files
```

## Configuration System

The `config.json` file controls:
- **Classification Rules**: Domain patterns, keywords, priorities
- **AI Settings**: Confidence thresholds, cache sizes, worker counts
- **Category Taxonomy**: Ordered list of categories/subcategories
- **LLM Settings**: Optional OpenAI-compatible API integration

See existing `config.json` for examples. The `TaxonomyStandardizer` in `src/taxonomy_standardizer.py` enforces naming consistency.

## Testing Approach

The codebase uses property-based testing with Hypothesis:
- Test files follow `test_*.py` naming in `/tests`
- Property tests validate invariants (e.g., "confidence scores always 0.0-1.0")
- Mock external dependencies (LLM APIs, ML libraries)
- Test data generation in `tests/output-round-2/generate_bookmarks.py`

## Important Implementation Details

### Plugin System
To add a new classifier:
1. Create class in `src/plugins/classifiers/your_classifier.py`
2. Inherit from `src/plugins/base.py::BaseClassifier`
3. Implement `classify()` method returning `ClassificationResult`
4. Register in `src/plugins/registry.py::CLASSIFIER_REGISTRY`

### Performance Considerations
- Large datasets (>1000 bookmarks): Use `--workers 4-8` for parallelism
- Memory constraints: Use `--no-ml` to disable ML classification
- The system automatically caches repeated classifications

### LLM Integration (Optional)
LLM classification is optional and falls back to ML/rules if:
- API key not configured
- API request fails
- Response parsing fails

Configure in `config.json` under `llm` section.

## Development Notes

- **Language**: Mixed Chinese/English codebase (comments, variable names, docs)
- **Type Hints**: Widely used throughout for clarity
- **Error Handling**: Graceful degradation (e.g., ML fails → rules work)
- **Logging**: Centralized in `logs/ai_classifier.log` with configurable levels
- **Dependencies**: Heavy ML stack (scikit-learn, numpy, jieba for Chinese)

## Key Files to Understand First

1. `src/ai_classifier.py::AIBookmarkClassifier` - Central orchestrator
2. `src/bookmark_processor.py::BookmarkProcessor` - Batch processing
3. `src/plugins/pipeline.py` - Plugin execution flow
4. `src/config_manager.py` - Configuration loading
5. `docs/design/system_architecture.md` - Detailed architecture

## Common Development Tasks

### Adding Classification Rules
Edit `config.json` → `category_rules` mapping:
```json
{
  "💻 编程/代码仓库": {
    "rules": [
      {
        "match": "domain",
        "keywords": ["github.com"],
        "weight": 20
      }
    ]
  }
}
```

### Extending Export Formats
1. Add method to `src/bookmark_processor.py::BookmarkProcessor`
2. Update `supported_formats` list
3. Handle in CLI arguments parsing (`main.py`)

### Performance Tuning
- Adjust `max_workers` in config based on CPU cores
- Tune `cache_size` for memory/performance tradeoff
- Use `confidence_threshold` to control precision vs recall

## Dependencies

**Core ML Stack**: scikit-learn, numpy, pandas, jieba (Chinese text)
**CLI/UI**: rich (terminal formatting), click, tqdm
**Web/Parse**: beautifulsoup4, requests, lxml
**Testing**: pytest, pytest-cov, hypothesis (property-based)

See `requirements.txt` and `pyproject.toml` for exact versions.
