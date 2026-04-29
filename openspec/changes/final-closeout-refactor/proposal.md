## Why

项目经过多轮开发后积累了严重的架构腐化：代码重复（~3500行）、目录结构漂移、配置冗余、僵尸分支、过量的 BMad Skills（46个/2.3MB）与本项目无关。作为最终收尾，必须彻底清理以达到工业级可归档状态。

## What Changes

### 代码架构清洗
- **BREAKING** 删除重复模块：`src/data_exporter.py`、`src/cli_interface.py`、`src/emoji_cleaner.py`
- 统一 CLI 入口：`main.py` → `src.cleanbook.cli:main`
- 配置去重：保留 `taxonomy/`，删除 `config/taxonomy/`

### 文件系统清理
- 删除 `.omc/` 目录（Opencode 配置，不应存在）
- 删除 `tests/output-round-*/` 测试输出目录
- 精简 BMad Skills：从 46 个减少到项目实际需要的 <5 个
- 更新 `.gitignore` 添加运行时产物

### Git 清理
- 删除 3 个 dependabot 僵尸远程分支
- 验证 CI/CD 工作流精简合理

### 文档优化
- 精简 AI 指令文件，消除重复内容
- 验证 GitHub Pages 文档完整性

## Capabilities

### New Capabilities

无新增能力。本变更为清理收尾，不引入新功能。

### Modified Capabilities

- `project-surface`: 项目文件结构规范变更（删除冗余文件、统一目录布局）
- `project-governance`: 更新收尾后的维护状态说明

## Impact

- **代码**: 删除 ~15 个冗余/重复文件，减少 ~3500 行重复代码
- **目录**: 从 90 个源文件精简到 ~50 个核心文件
- **Skills**: 从 46 个精简到 <5 个
- **Git**: 删除 3 个僵尸分支，仅保留 master
- **文档**: 保持现有文档结构，精简 AI 指令
- **无破坏性变更**: 所有公开 API 入口保持兼容（`cleanbook`、`cleanbook-wizard`）

## Non-goals

- 不引入新功能或 API
- 不修改核心分类逻辑
- 不改变 CLI 用户接口
- 不添加新的 MCP 或插件层
