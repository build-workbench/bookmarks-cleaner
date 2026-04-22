# AGENTS.md

## Spec-Driven Development

**Read `/specs` before writing code.** This project follows SDD strictly:
- `/specs/product/` - Product requirements
- `/specs/rfc/` - Technical design RFCs
- `/specs/testing/` - Test specifications

For new features: update specs first, implement exactly to spec (no gold-plating).

## Commands

```bash
# Setup
pip install -e .                    # Creates CLI commands: cleanbook, cleanbook-wizard
pre-commit install                  # Required for dev workflow

# Test
pytest                              # Full suite
pytest -m "not slow"                # Skip slow tests
pytest -m property                  # Property-based tests only

# Quality (run before committing)
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/ && mypy src/

# Run
python main.py -i bookmarks.html -o output/
python main.py --health-check       # Debug component status
python main.py --no-ml ...          # Disable ML to save ~80MB memory
```

## Architecture

- **Entry points**: `cleanbook` → `src.cleanbook.cli:main`, `cleanbook-wizard` → `src.enhanced_cli:main`
- **Core orchestrator**: `src/ai_classifier.py`
- **Rule engine**: `src/engines/rules.py`
- **Plugin base**: `src/plugins/base.py`

### Adding a Classifier Plugin

1. Create `src/plugins/classifiers/your_classifier.py`
2. Inherit from `ClassifierPlugin` in `src/plugins/base.py`
3. Implement: `metadata`, `classify(features)`, `initialize(config)`, `shutdown()`

## Config Rules (`config.json`)

Rule types in `category_rules`:
- `match: domain` - URL domain patterns
- `match: title` - Bookmark title keywords
- `match: url_ends_with` - URL suffixes (e.g., `.pdf`)
- `match_all_keywords_in` - Require all keywords

## Conventions

- **Mixed Chinese/English codebase** - accept both in comments/docstrings
- **Type hints** throughout
- **Docstrings** required for public APIs
- Use `logger = logging.getLogger(__name__)`, not `print`
