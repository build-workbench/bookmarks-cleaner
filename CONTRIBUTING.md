# Contributing to CleanBook

Thank you for your interest in contributing to CleanBook! This document provides guidelines for contributing to the project, including how to participate in Spec-Driven Development (SDD).

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Spec-Driven Development Workflow](#spec-driven-development-workflow)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🎯 How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Reproduction steps**
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Example code** if possible

### Suggesting Features

Feature suggestions should:

- Use clear, concise language
- Explain the problem the feature solves
- Include examples or use cases
- Reference related issues if applicable

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Review existing specs** in `/specs` directory
4. **Update or create specs** before writing code (see SDD workflow)
5. **Write code** following the project's coding standards
6. **Write tests** covering the new functionality
7. **Update documentation** as needed
8. **Submit a pull request**

## 📝 Spec-Driven Development Workflow

CleanBook follows **Spec-Driven Development (SDD)** methodology. This means specifications in the `/specs` directory are the single source of truth for all development.

### Specification Structure

```
specs/
├── product/          # Product requirements and user stories
│   └── bookmark-classifier-system.md
├── rfc/              # Technical design documents (RFCs)
│   └── 0001-architecture-algorithm-upgrade.md
├── api/              # API interface definitions
│   └── README.md
├── db/               # Database schemas
│   └── README.md
└── testing/          # Test specifications (BDD format)
    └── classification-tests.md
```

### Contribution Workflow

1. **Review Existing Specs**
   - Read relevant product requirements (`/specs/product/`)
   - Review technical designs (`/specs/rfc/`)
   - Check API definitions (`/specs/api/`)
   - Understand test specifications (`/specs/testing/`)

2. **Propose Spec Changes**
   - For new features: Create a new RFC in `/specs/rfc/`
   - For API changes: Update `/specs/api/openapi.yaml`
   - For requirement changes: Update `/specs/product/`
   - **Wait for review and approval** before coding

3. **Implement to Spec**
   - Code must 100% comply with specs
   - No gold-plating (don't add unrequested features)
   - Follow coding standards strictly

4. **Write Tests**
   - Tests must verify spec acceptance criteria
   - Use property-based testing where applicable
   - Ensure all tests pass

5. **Submit PR with Spec Updates**
   - Include spec changes in the same PR
   - Reference the RFC number in commit messages
   - Document any deviations from spec

### Creating a New RFC

For significant technical changes, create an RFC:

1. Create `/specs/rfc/NNNN-short-description.md`
2. Include:
   - **Overview**: What and why
   - **Design Goals**: Key objectives
   - **Proposed Solution**: Technical approach
   - **Architecture Diagrams**: Mermaid diagrams
   - **Data Models**: New/modified data structures
   - **Migration Path**: How to transition from current state
   - **Testing Strategy**: How to verify correctness

3. Submit PR with `[RFC]` prefix
4. Wait for review and approval before implementation

## 🛠️ Development Setup

### Prerequisites

- Python 3.10+
- pip or pipx
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode (creates CLI commands)
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_plugin_registry_properties.py -v
```

## 🔄 Pull Request Process

### PR Title Format

Use conventional commits format:

```
type(scope): description

Examples:
feat(classifier): add embedding-based classification
fix(parser): handle malformed bookmark HTML
docs(specs): update RFC 0001 architecture design
test(active-learning): add property tests for sampling
```

### PR Checklist

- [ ] **Specs Updated**: Related specs updated or new specs created
- [ ] **Tests Pass**: All tests pass locally
- [ ] **Tests Added**: New tests cover the changes
- [ ] **Documentation Updated**: README, docs, and comments updated
- [ ] **Code Style**: Follows PEP8 and project conventions
- [ ] **Type Hints**: Added where missing
- [ ] **No Breaking Changes**: Or clearly documented breaking changes

### PR Review Process

1. Automated CI checks must pass
2. At least one maintainer review required
3. Address all review comments
4. Squash commits if requested
5. Merge after approval

## 📏 Coding Standards

### Python Style

- Follow **PEP8** with 88-character line limit
- Use **type hints** for all functions
- Use **docstrings** for all public functions and classes (Google style)
- Use **meaningful variable names**
- Add comments explaining **why**, not **what**

### Example

```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    """Represents the result of classifying a bookmark.

    Attributes:
        category: The assigned category name
        confidence: Confidence score (0.0-1.0)
        method: Classification method used
        alternatives: Alternative categories with scores
    """
    category: str
    confidence: float
    method: str
    alternatives: List[tuple[str, float]] = None

    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check if classification meets confidence threshold.

        Args:
            threshold: Minimum confidence required

        Returns:
            True if confidence >= threshold, False otherwise
        """
        return self.confidence >= threshold
```

### Commit Messages

Follow conventional commits:

```
type(scope): short description

Longer explanation of the change (optional)

Refs: #123 (optional issue reference)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🧪 Testing Guidelines

### Test Types

1. **Property-Based Tests**: Verify universal properties using Hypothesis
2. **Unit Tests**: Test individual functions/classes
3. **Integration Tests**: Test component interactions
4. **End-to-End Tests**: Test complete workflows

### Writing Tests

- Place tests in `/tests` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_should_classify_github_repo_as_programming`
- Include edge cases and boundary conditions
- Mock external dependencies

### Property-Based Testing

Use Hypothesis for property-based tests:

```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0.0, max_value=1.0))
def test_confidence_score_in_valid_range(confidence: float):
    """Property: Confidence scores must be between 0.0 and 1.0."""
    assert 0.0 <= confidence <= 1.0
```

## 📚 Documentation

### Types of Documentation

- **Specs** (`/specs`): Formal requirements and designs
- **Architecture** (`/docs/architecture/`): System architecture
- **Tutorials** (`/docs/tutorials/`): User how-to guides
- **Setup** (`/docs/setup/`): Environment setup guides
- **README**: Project overview and quick start
- **CHANGELOG**: Release notes

### Documentation Standards

- Write in **English** (primary language)
- Use **Markdown** format
- Include **code examples** where helpful
- Use **Mermaid** for diagrams
- Keep docs **up-to-date** with code changes

### Updating Documentation

When making changes:

1. Update related specs first (if applicable)
2. Update `/docs` documentation
3. Update README if user-facing changes
4. Update CHANGELOG under "Unreleased" section

## 🙏 Thank You

Every contribution helps make CleanBook better! Whether it's a bug fix, feature addition, documentation improvement, or spec refinement - your efforts are appreciated.

For questions, please:
- Open an issue on GitHub
- Join our discussions
- Read existing documentation

---

**Happy Contributing!** 🚀
