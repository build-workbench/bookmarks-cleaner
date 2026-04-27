# Bookmarks-Cleaner 终极重构设计规范

## 项目背景

**项目**：bookmarks-cleaner (包名 cleanbook) - 智能书签清理工具
**阶段**：最终收尾，准备归档
**问题**：前期使用能力较弱的模型开发，导致架构腐化

## 用户决策摘要

| 决策点 | 选择 |
|--------|------|
| 重构策略 | **激进重构** - 合并重复、拆分大文件、重组目录 |
| 依赖版本 | **锁定 minor 版本** - 使用 `~=` 约束 |
| 遗留目录 | **全部删除** - agent/, _bmad/, _bmad-output/ |
| AI 工具链 | **精简优化** - 优化现有配置，不添加 MCP |
| Git Pages | **重新设计** - 现代化产品展示页面 |
| 执行模式 | **全自动执行** - YOLO 模式 |

## 探索发现的问题

### 严重问题

1. **文件重复**：存在 3 个完全相同的 deduplicator.py
   - `src/deduplicator.py` (删除)
   - `src/data/deduplicator.py` (保留 - 实际被导入)
   - `src/core/deduplicator.py` (删除)

2. **顶层文件过多**：30 个 `.py` 文件散落在 `src/` 根目录

3. **配置存在但不执行**：mypy, bandit, coverage 配置了但 CI 不运行

4. **依赖版本未锚定**：所有依赖使用 `>=` 无上限锁定

### 中等问题

1. `cli_interface.py` 1115 行，`config.json` 762 行
2. `docs/index.md` 与 `docs/zh/index.md` 完全重复
3. pre-commit 与 pyproject.toml 工具版本不一致
4. OpenSpec 归档有 3 个，内容有部分重叠

### 良好状态

- OpenSpec 工作流符合规范
- 插件系统设计清晰
- 中英文文档同步良好
- CI 工作流精简有效
- AI 指令文件质量高

## 四阶段实施方案

### Phase 1: 激进的审查与规范化重构

#### Task 1.1: 清理重复文件与遗留目录

**删除文件**：
- `src/deduplicator.py` (重复)
- `src/core/deduplicator.py` (重复)
- `config_temp.json` (临时文件)

**删除目录**：
- `agent/`
- `_bmad/`
- `_bmad-output/`

**验证**：`grep -r "from.*deduplicator" src/` 确认导入正确

#### Task 1.2: 依赖版本锁定

**修改文件**：`pyproject.toml`

**修改内容**：将所有 `>=` 改为 `~=`

```toml
# 修改前
"beautifulsoup4>=4.12.3"

# 修改后
"beautifulsoup4~=4.12.3"
```

#### Task 1.3: CI 配置修复

**修改文件**：`.github/workflows/ci.yml`

**添加任务**：
- 类型检查 job：`mypy src/`
- 安全检查 job：`bandit -r src/`
- 覆盖率报告：`pytest --cov=src --cov-report=xml`

#### Task 1.4: 文档治理

**删除**：`docs/index.md` (与 `docs/zh/index.md` 重复)

**整理**：合并 OpenSpec 归档

#### Task 1.5: Git Pages 重新设计

**修改文件**：
- `docs/.vitepress/config.mts`
- `docs/zh/index.md`
- `docs/en/index.md`

**设计要素**：Hero、Features 卡片、Quick Start、Demo

### Phase 2: 工程化与 GitHub 深度集成

#### Task 2.1: 工作流精简

- 增强 `ci.yml`（添加 mypy/bandit/coverage）
- 添加 Dependabot for GitHub Actions

#### Task 2.2: GitHub 仓库元信息更新

```bash
gh repo edit --description "🧹 智能书签清理工具：去重、验证、分类、插件扩展"
gh repo edit --add-topic bookmarks,cleaner,deduplication,python,cli,plugin-system
```

#### Task 2.3: 开发流程固化

- 更新 `CONTRIBUTING.md`
- 确保 `.github/pull_request_template.md` 存在

### Phase 3: AI 工具链精简优化

#### Task 3.1: AGENTS.md 优化

确保与 CLAUDE.md 同步，添加项目收尾阶段说明

#### Task 3.2: LSP 配置优化

启用更严格的 mypy 类型检查

#### Task 3.3: pre-commit 配置统一

对齐 pre-commit 与 pyproject.toml 的工具版本

### Phase 4: 收尾验证

#### Task 4.1: 全量测试

```bash
pytest tests/ -v --cov=src
mypy src/
bandit -r src/ -c pyproject.toml
```

**通过标准**：覆盖率 >= 80%，无类型错误，无高危安全问题

#### Task 4.2: 文档最终审查

检查 README、CHANGELOG、文档链接

#### Task 4.3: 版本与发布准备

更新版本号和 CHANGELOG，构建验证

## 关键文件清单

| 文件 | 用途 | 操作 |
|------|------|------|
| `pyproject.toml` | 依赖版本、入口点 | 修改 |
| `.github/workflows/ci.yml` | CI 工作流 | 增强 |
| `src/data/deduplicator.py` | 去重模块 | 保留 |
| `src/deduplicator.py` | 重复文件 | 删除 |
| `src/core/deduplicator.py` | 重复文件 | 删除 |
| `docs/.vitepress/config.mts` | Git Pages | 修改 |
| `AGENTS.md` | AI 指南 | 优化 |
| `CLAUDE.md` | Claude 指南 | 保持 |

## 验证方法

### Phase 1 验证

```bash
# 无重复文件
find src -name "*.py" -exec md5sum {} \; | sort | uniq -w32 -dD

# 无遗留目录
ls agent/ _bmad/ 2>/dev/null && echo "FAIL" || echo "PASS"

# 依赖锁定
grep ">=" pyproject.toml | head -5
```

### Phase 2 验证

```bash
gh repo view --json description
gh run list --limit 3
```

### Phase 3 验证

```bash
mypy src/
pre-commit run --all-files
```

### Phase 4 验证

```bash
pytest tests/ -q --cov=src
python -m build && twine check dist/*
```

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 删除重复文件破坏导入 | 先 grep 确认所有导入路径 |
| 依赖版本冲突 | 逐个更新，测试验证 |
| CI 修改失败 | 保留原配置备份 |
| Git Pages 部署失败 | 本地构建验证 |

## 执行顺序

```
Phase 1 → Phase 2 → Phase 3 → Phase 4
  │          │          │          │
  ├─ 1.1     ├─ 2.1     ├─ 3.1     ├─ 4.1
  ├─ 1.2     ├─ 2.2     ├─ 3.2     ├─ 4.2
  ├─ 1.3     └─ 2.3     └─ 3.3     └─ 4.3
  ├─ 1.4
  └─ 1.5
```
