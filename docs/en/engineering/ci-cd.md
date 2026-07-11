# CI/CD Configuration

This page explains the project's continuous integration and deployment configuration to help contributors understand automated workflows.

## Workflow Overview

The project maintains one main GitHub Actions workflow:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push to master | Testing and code quality checks |

## CI Workflow Details

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        python: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest -q --cov
      
      - name: Type check
        run: mypy src
      
      - name: Lint
        run: ruff check src

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: docs/package-lock.json
      
      - name: Build docs
        run: |
          cd docs
          npm ci
          npm run build
      
      - name: Test docs
        run: cd docs && node --test tests/*.test.mjs
```

## Local Verification

You can run full CI checks locally before committing:

```bash
# Run tests
pytest -q

# Type checking
mypy src

# Code style
ruff check src
ruff format src --check

# Build docs
cd docs && npm run build

# Test docs
cd docs && node --test tests/*.test.mjs
```

## References

- [Testing Strategy](/en/engineering/testing-strategy) — Detailed testing architecture
- [ADR-007](/en/adr#adr-007-cicd-strategy) — CI/CD decision record
