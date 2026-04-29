## Context

项目当前状态：
- **代码重复**: `src/data_exporter.py` 与 `src/data/exporter.py`，`src/cli_interface.py` 与 `src/cli/interface.py` 等存在约 3500 行重复代码
- **目录漂移**: 多层 CLI 入口（main.py + cleanbook + cleanbook-wizard）导致维护混乱
- **配置冗余**: `taxonomy/`、`src/resources/taxonomy/`、`config/taxonomy/` 三处重复
- **文件膨胀**: 46 个 BMad Skills (2.3MB) 与本项目无关
- **僵尸分支**: 3 个 dependabot 创建的远程分支未清理
- **运行时产物**: `.omc/`、`tests/output-round-*/`、`models/*.pkl` 未纳入 .gitignore

## Goals / Non-Goals

**Goals:**
1. 消除所有代码重复，统一模块布局
2. 清理无关文件，精简项目结构到 ~50 个核心文件
3. 删除僵尸分支，保持仓库干净
4. 更新 .gitignore，排除运行时产物
5. 精简 AI 指令文件，消除重复内容
6. 确保所有测试通过，CI/CD 正常运行

**Non-Goals:**
- 不修改核心分类逻辑
- 不改变 CLI 用户接口（`cleanbook`、`cleanbook-wizard` 入口保持兼容）
- 不引入新功能
- 不添加新的依赖

## Decisions

### D1: 代码去重策略

**决策**: 删除 `src/` 根目录下的重复模块，保留子目录中的模块

**理由**:
- 子目录模块结构更清晰，符合包命名规范
- `pyproject.toml` 已正确配置包路径
- 最小化改动，避免破坏现有导入

**删除文件**:
```
src/data_exporter.py    → 保留 src/data/exporter.py
src/cli_interface.py    → 保留 src/cli/interface.py
src/emoji_cleaner.py    → 保留 src/utils/emoji_cleaner.py
```

**替代方案考虑**:
- ❌ 保留根目录文件：违反模块化原则
- ❌ 合并文件：差异微小，不必要的工作量

### D2: 配置文件布局

**决策**: 保留 `taxonomy/` 根目录，作为规范位置

**理由**:
- 用户可直接编辑，无需了解包内部结构
- `src/resources/taxonomy/` 仅用于打包（已有 `__init__.py`）
- `config/taxonomy/` 完全冗余，删除

**目录结构**:
```
taxonomy/
├── subjects.yaml
└── resource_types.yaml

src/resources/taxonomy/
├── __init__.py (打包用)
└── (软链接或复制)
```

### D3: BMad Skills 精简

**决策**: 删除所有 BMad Skills，保留 OpenSpec 核心

**理由**:
- BMad 是外部方法论，与本项目无关
- Skills 目录 (2.3MB) 增加仓库体积
- 项目已采用 OpenSpec 工作流，不需要 BMad

**保留**:
- `.claude/skills/opsx-*` (OpenSpec 相关)
- 删除所有 `bmad-*` skills

### D4: CLI 入口统一

**决策**: 保持现有入口，调整内部实现

**入口点**:
```
main.py → 调用 src.cleanbook.cli:main
cleanbook → src.cleanbook.cli:main (Click)
cleanbook-wizard → src.enhanced_cli:main (Rich UI)
```

**理由**: 用户接口不变，内部重构

### D5: Git 清理策略

**决策**: 删除所有 dependabot 僵尸分支

**删除分支**:
```bash
git push origin --delete dependabot/github_actions/actions/setup-python-6
git push origin --delete dependabot/npm_and_yarn/docs/vitepress-1.6.4
git push origin --delete dependabot/pip/beautifulsoup4-gte-4.12.3-and-lt-4.15.0
git push origin --delete dependabot/pip/mypy-gte-1.10-and-lt-1.21
```

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 删除文件后导入失败 | 运行完整测试套件验证 |
| 用户自定义配置丢失 | 保留 `taxonomy/` 根目录 |
| CI/CD 失败 | 保持工作流不变，仅清理分支 |
| Skills 删除影响开发 | OpenSpec 已覆盖核心工作流 |

## Migration Plan

### 阶段 1: 代码清理
1. 删除重复源文件
2. 更新 `pyproject.toml` 包配置
3. 运行 `pytest -q` 验证

### 阶段 2: 目录清理
1. 删除 `.omc/` 目录
2. 删除 `config/taxonomy/` 目录
3. 删除 `tests/output-round-*/` 目录
4. 更新 `.gitignore`

### 阶段 3: Skills 清理
1. 删除所有 `bmad-*` skills
2. 保留 `opsx-*` skills
3. 验证 OpenSpec 工作流正常

### 阶段 4: Git 清理
1. 删除僵尸远程分支
2. 验证本地仓库状态

### 阶段 5: 最终验证
1. 运行完整测试套件
2. 验证 CI/CD 通过
3. 验证文档构建

## Open Questions

无待解决问题。本变更为纯清理工作，无需新增决策。
