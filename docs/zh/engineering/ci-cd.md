# CI/CD 配置

本页说明项目的持续集成与持续部署配置，帮助贡献者理解自动化工作流。

## 工作流概览

项目维护三个主要 GitHub Actions 工作流：

| 工作流 | 触发条件 | 用途 |
|--------|----------|------|
| `ci.yml` | Push/PR 到 master | 测试与代码质量检查 |
| `pages.yml` | Push 到 master | 文档站点部署 |
| `release.yml` | 创建 Release Tag | PyPI 发布 |

## CI 工作流详解

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

## Pages 部署

文档站点通过 GitHub Pages 自动部署：

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

## 发布流程

创建新的 Release Tag 时自动触发 PyPI 发布：

```bash
# 创建新版本发布
git tag v2.1.0
git push origin v2.1.0

# GitHub Actions 自动执行：
# 1. 构建分发包
# 2. 发布到 PyPI
# 3. 创建 GitHub Release
```

## 本地验证

提交前可在本地运行完整的 CI 检查：

```bash
# 运行测试
pytest -q

# 类型检查
mypy src

# 代码风格
ruff check src
ruff format src --check

# 文档构建
cd docs && npm run build

# 文档测试
cd docs && node --test tests/*.test.mjs
```

## 参考链接

- [测试策略](/zh/engineering/testing-strategy) — 测试架构详解
- [ADR-007](/zh/adr#adr-007-cicd-策略) — CI/CD 决策记录
