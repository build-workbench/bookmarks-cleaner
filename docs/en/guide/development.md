# Development Guide

This guide is for developers who want to contribute to CleanBook or build upon it.

## Environment Setup

### System Requirements

- **Python**: 3.10+
- **Operating System**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Memory**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 2GB available space

### Recommended Development Tools

```bash
# IDE recommendations
- VS Code + Python Extension
- PyCharm Professional
- Vim/Neovim + LSP

# Version control
- Git 2.20+

# Virtual environments
- venv (Python built-in)
- conda
- poetry
```

### Project Initialization

```bash
# Clone repository
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run health check
python main.py --health-check
```

## Project Structure

```
bookmarks-cleaner/
├── main.py                     # Main entry point
├── config.json                 # Configuration file
├── pyproject.toml              # Project metadata
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── src/                        # Source code
│   ├── cleanbook/             # Core package
│   │   ├── cli.py             # CLI entry
│   │   └── ...
│   ├── plugins/               # Plugin system
│   │   ├── base.py            # Base plugin class
│   │   └── classifiers/       # Classifier plugins
│   ├── services/              # Service layer
│   ├── ai_classifier.py       # AI classifier
│   ├── bookmark_processor.py  # Bookmark processor
│   ├── rule_engine.py         # Rule engine
│   └── ...
├── tests/                      # Test code
├── models/                     # Model storage
├── taxonomy/                   # Vocabulary configs
└── docs/                       # Documentation
```

## Code Standards

### Python Code Style

Use type annotations and dataclasses:

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class BookmarkFeatures:
    """Bookmark features dataclass"""
    url: str
    title: str
    domain: str = ""
    confidence: float = 0.0

def classify_bookmark(url: str, title: str) -> ClassificationResult:
    """
    Classify a single bookmark
    
    Args:
        url: Bookmark URL
        title: Bookmark title
        
    Returns:
        Classification result object
        
    Raises:
        ClassificationError: Raised when classification fails
    """
    pass
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Usage
logger.debug("Debug: Starting feature extraction")
logger.info(f"Processing complete: {count} bookmarks")
logger.warning("Config file missing some fields")
logger.error(f"Processing failed: {error_msg}")
```

### Testing Standards

```python
import pytest
from unittest.mock import Mock, patch

class TestAIClassifier:
    """AI classifier test class"""
    
    def setup_method(self):
        """Initialize for each test method"""
        self.classifier = AIClassifier("test_config.json")
    
    def test_classify_github_url(self):
        """Test GitHub URL classification"""
        url = "https://github.com/user/repo"
        title = "Test Repository"
        
        result = self.classifier.classify(url, title)
        
        assert result.category == "Technology/Code Repository"
        assert result.confidence > 0.8
```

## Extension Development

### Adding a New Classifier Plugin

1. Create new file in `src/plugins/classifiers/`
2. Inherit from `ClassifierPlugin` base class
3. Implement required methods
4. Register in `registry.py`

```python
# src/plugins/classifiers/my_classifier.py
from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult

class MyClassifier(ClassifierPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_classifier",
            version="1.0.0",
            capabilities=["custom"],
            priority=50
        )
    
    def classify(self, features):
        # Implement classification logic
        return ClassificationResult(
            category="Result",
            confidence=0.9,
            method="my_classifier"
        )
```

### Adding a New Export Format

1. Extend `DataExporter` class
2. Register in `bookmark_processor.py`

```python
class XMLExporter(DataExporter):
    """XML format exporter"""
    
    def export(self, organized_bookmarks, output_file, stats=None):
        """Export to XML format"""
        # Implement export logic
        pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rule_engine.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run property tests
pytest tests/test_*_properties.py
```

### Performance Testing

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.performance
    def test_classification_speed(self):
        classifier = AIClassifier("config.json")
        test_bookmarks = [("https://example.com", "Test")] * 100
        
        start = time.time()
        for url, title in test_bookmarks:
            classifier.classify(url, title)
        elapsed = time.time() - start
        
        assert len(test_bookmarks) / elapsed > 20  # At least 20/sec
```

## Debugging Tips

### Enable Debug Mode

```bash
# Command line
python main.py --log-level DEBUG

# In code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Using Breakpoints

```python
import pdb; pdb.set_trace()
# Or use more friendly ipdb
import ipdb; ipdb.set_trace()
```

### Performance Profiling

```bash
# Using cProfile
python -m cProfile -o profile.prof main.py -i input.html

# Analyze results
python -c "import pstats; pstats.Stats('profile.prof').sort_stats('cumulative').print_stats(20)"
```

## Submitting Pull Requests

1. Fork the repository and create a feature branch
2. Write code and add tests
3. Ensure all tests pass
4. Update documentation (if needed)
5. Submit PR with clear description of changes

### Commit Message Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new classifier plugin
fix: fix cache invalidation issue
docs: update README
test: add performance tests
refactor: refactor rule engine
```

## Release Process

```bash
# 1. Update version
# Edit version in pyproject.toml

# 2. Update CHANGELOG.md

# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): prepare v2.0.1"

# 4. Tag
git tag v2.0.1

# 5. Push
git push origin main --tags

# 6. GitHub Actions will automatically publish to PyPI
```
