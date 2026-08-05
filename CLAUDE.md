# CLAUDE.md

本文件为 Claude Code 提供仓库级指引。完整的项目约定、验证基线见 `AGENTS.md`。

## 基本原则

- 面向 **当前维护的 CLI**，不做平台扩展
- 业余项目，单人直接推 master，保持仓库小巧低噪
- 不考虑向后兼容，可以破坏性更改

## 保留什么

- `cleanbook` 作为打包 CLI 入口
- 处理流水线保持：规则优先、ML 辅助、LLM 可选
- 公开文档与实际支持行为对齐
- CI 在真实错误上必须响亮失败

## 避免什么

- 引入 API/数据库等新作用域
- 堆砌通用或重复的 AI 指令
- 为了显得全面而扩张文档
- 用 `|| true` 让必需校验软失败
- 没有具体复用场景就扩张工具面

## 高价值文件

- `main.py`
- `pyproject.toml`
- `config.json`
- `src/bookmark_processor.py`
- `src/plugins/`
- `src/services/`
