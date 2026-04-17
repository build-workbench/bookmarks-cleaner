# QWEN.md - Qwen Code Interaction Guide

## ⚠️ Important: Spec-Driven Development (SDD)

This project strictly follows **Spec-Driven Development (SDD)** paradigm. All code implementations must use the specification documents in the `/specs` directory as the single source of truth.

**AI Agent Workflow**:
1. **Review Specs First**: Before writing code, read relevant product docs, RFCs, and API definitions in `/specs`
2. **Spec-First**: For new features or interface changes, propose spec modifications first, wait for user confirmation before coding
3. **Implementation**: Code must 100% comply with spec definitions (variable names, API paths, data types, etc.)
4. **Test Verification**: Write unit and integration tests based on acceptance criteria in `/specs`

For complete AI agent workflow instructions, see `AGENTS.md`.

## Project Overview

CleanBook is an AI-powered bookmark classification system that automatically analyzes, classifies, and organizes browser bookmarks.

Core Components:
- `src/ai_classifier.py` - Central orchestrator coordinating multiple classification strategies
- `src/bookmark_processor.py` - Batch bookmark processing coordinator
- `src/plugins/` - Modular classifier plugins (rule, ML, embedding, LLM)
- `src/services/` - Cross-cutting services (embedding, taxonomy, performance monitoring)

## Code Style Conventions

1. Follow PEP8 Python coding standards
2. Use type hints throughout
3. Complete docstrings for all functions and classes
4. High-value comments explaining **why**, not **what**
5. Configuration in JSON format with clear structure

## Key Implementation Details

### Classifier Architecture
- Ensemble learning combining multiple classification techniques
- LRU caching for performance optimization
- Dynamic rule addition and weight adjustment
- Confidence scoring system

### Processing Flow
1. Parse HTML bookmark file
2. Extract bookmark features
3. Apply classification rules
4. ML model prediction (if enabled)
5. Result fusion and optimization
6. Output multiple format files

### Performance Optimization
- Multi-threaded parallel processing
- Intelligent caching strategy
- Batch processing mechanism
- Lazy component initialization

## Configuration Files

Main configuration file is `config.json`, containing:
- `category_rules`: Classification rule definitions
- `ai_settings`: AI-related settings
- `category_order`: Category display order
- `title_cleaning_rules`: Title cleaning rules

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run health check
python main.py --health-check

# Process bookmarks (CLI mode)
python main.py -i examples/demo_bookmarks.html

# Start interactive mode
python main.py --interactive

# Run tests
pytest
```

## Output File Formats

Processing generates three output formats:
1. **HTML**: Importable to browsers
2. **JSON**: Detailed classification metadata and statistics
3. **Markdown**: Readable classification report

## Important Notes

1. ML features require additional dependencies (scikit-learn, jieba, etc.)
2. Adjust thread count for optimal performance with large bookmark sets
3. Customize classification rules and weights via configuration
4. Supports both Chinese and English content
5. System has learning capability from user feedback

## Test Strategy

The project includes comprehensive test suite:
- Unit tests covering core functionality
- Integration tests validating component coordination
- Property-based tests using Hypothesis
- End-to-end tests simulating complete workflows

Run tests: `pytest`

## Extension Development Guide

Adding new classification methods:
1. Create new classifier plugin in `src/plugins/classifiers/`
2. Inherit from `BaseClassifier`
3. Implement `classify()` method
4. Register in `CLASSIFIER_REGISTRY`
5. Add corresponding test cases
