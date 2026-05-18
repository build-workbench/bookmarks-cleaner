# Testing Strategy

This page explains the project's testing architecture, coverage goals, and execution methods to help contributors understand quality assurance boundaries and expectations.

## Test Pyramid

The project adopts a classic test pyramid structure:

```
        ┌──────────────┐
        │   E2E Tests   │  CLI end-to-end
        │   (minimal)   │
        └──────────────┘
      ┌────────────────────┐
      │ Integration Tests  │  Pipeline stage interaction
      │    (moderate)      │
      └────────────────────┘
    ┌──────────────────────────┐
    │      Unit Tests          │  Classifiers, utilities
    │       (abundant)         │
    └──────────────────────────┘
```

| Level | Coverage Target | When to Run | Typical Scenarios |
|-------|-----------------|-------------|-------------------|
| Unit tests | Individual functions/class methods | Every commit | Rule matching, confidence calculation |
| Integration tests | Multi-module interaction | Before PR merge | Pipeline stage data contracts |
| E2E tests | CLI entry to output | Before release | Full processing flow validation |

## Running Tests

```bash
# Run all tests
pytest -q

# Run specific module
pytest tests/test_fusion_engine.py -v

# With coverage report
pytest --cov=src --cov-report=html

# Run only fast tests
pytest -q -m "not slow"
```

## Mock Strategy

The project uses explicit mock boundaries for external dependencies:

| Dependency Type | Mock Approach | Tool |
|-----------------|---------------|------|
| LLM API calls | Fixed responses | `unittest.mock` |
| File system | Temporary directories | `pytest.tmp_path` |
| Network requests | Record/replay | `responses` library |
| ML models | Lightweight stubs | Pre-computed features |

### Mock Example

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_llm_client():
    """Mock LLM API calls to avoid actual network requests"""
    with patch('bookmarks_cleaner.services.llm.client.LLMClient') as mock:
        mock.return_value.classify.return_value = {
            'category': 'Development',
            'confidence': 0.92
        }
        yield mock

def test_llm_classifier_uses_mock(mock_llm_client):
    from bookmarks_cleaner.services.llm.classifier import LLMClassifier
    classifier = LLMClassifier()
    result = classifier.classify({'title': 'Python Tutorial', 'url': 'https://docs.python.org'})
    assert result['category'] == 'Development'
    assert mock_llm_client.return_value.classify.called
```

## Test Data

The project maintains two sets of test data:

1. **Unit test data** (`tests/fixtures/`): Small, deterministic, version-controlled
2. **Integration test data** (`tests/data/`): Larger samples, simulated real export formats

```bash
tests/
├── fixtures/
│   ├── sample_bookmarks.html    # 10 bookmarks
│   └── sample_bookmarks.json    # JSON format reference
├── data/
│   └── large_export.html        # 1000+ bookmarks
└── conftest.py                  # Shared fixtures
```

## Fault Injection Testing

Pipeline fault tolerance is verified through fault injection tests:

```python
def test_malformed_html_recovery():
    """Verify corrupted HTML should not crash entire processing"""
    loader = BookmarkLoader()
    with pytest.raises(PartialParseError) as exc_info:
        loader.load('tests/fixtures/corrupted.html')
    assert exc_info.value.recovered_count > 0  # Partial recovery

def test_ml_model_missing_fallback():
    """Should fallback to rules mode when ML model is missing"""
    with patch.dict(os.environ, {'ML_MODEL_PATH': '/nonexistent'}):
        classifier = MLClassifier()
        result = classifier.classify({'title': 'Test', 'url': 'https://example.com'})
        assert result['source'] == 'rule'  # Fallback to rules
        assert 'fallback' in result
```

## Coverage Targets

| Module | Target Coverage | Current Status |
|--------|-----------------|----------------|
| `src.pipelines` | ≥90% | ✅ 92% |
| `src.services.fusion` | ≥95% | ✅ 95% |
| `src.services.rules` | ≥90% | ✅ 91% |
| `src.services.ml` | ≥85% | ✅ 88% |
| `src.plugins` | ≥80% | ⚠️ 76% |

## Continuous Integration

Every PR triggers the full test matrix:

```yaml
# .github/workflows/ci.yml snippet
jobs:
  test:
    strategy:
      matrix:
        python: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e ".[dev]"
      - run: pytest -q --cov
```

## References

- [Pipeline Architecture](/en/architecture/pipeline) — Background for understanding test boundaries
- [ADR-005](/en/adr#adr-005-test-boundaries-and-mock-strategy) — Decision record for mock strategy
