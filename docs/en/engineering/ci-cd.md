# CI/CD Configuration

This page explains the project's continuous integration and deployment configuration to help contributors understand automated workflows.

## Workflow Overview

The project maintains three main GitHub Actions workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push/PR to master | Testing and code quality checks |
| `pages.yml` | Push to master | Documentation site deployment |
| `release.yml` | Create Release Tag | PyPI publishing |

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

## Pages Deployment

The documentation site is automatically deployed via GitHub Pages:

```yaml
# .github/workflows/pages.yml
name: Deploy Pages

on:
  push:
    branches: [master]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Build VitePress
        run: |
          cd docs
          npm ci
          npm run build
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

## Release Process

Creating a new Release Tag automatically triggers PyPI publishing:

```bash
# Create a new version release
git tag v2.1.0
git push origin v2.1.0

# GitHub Actions automatically executes:
# 1. Build distribution packages
# 2. Publish to PyPI
# 3. Create GitHub Release
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
