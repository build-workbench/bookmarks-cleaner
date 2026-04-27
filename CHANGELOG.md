# Changelog

This file keeps a **small maintained release record** for CleanBook. Detailed historical cleanup notes were intentionally removed during the closeout normalization pass to reduce repository noise.

## [Unreleased]

## [2.0.2] - 2026-04-28

### Fixed
- 删除重复的 deduplicator.py 文件 (src/deduplicator.py, src/core/deduplicator.py)
- 修复 CI 中未执行 mypy/bandit/coverage 的问题
- 锁定依赖版本确保可重复构建 (使用 ~= 约束)

### Removed
- 删除遗留目录 (agent/, _bmad/, _bmad-output/)
- 删除临时配置文件 (config_temp.json)
- 删除重复的 docs/index.md
- 精简 OpenSpec 归档 (保留最新的 2026-04-26)

### Changed
- 增强 CI 工作流：添加 mypy 类型检查、bandit 安全检查、覆盖率报告
- 添加 Dependabot 支持 GitHub Actions 更新
- pre-commit 配置添加 mypy 检查
- 更新 GitHub 仓库描述和 topics

## Recent Releases

### [2026.04.16] - 2026-04-16
- LRU cache behavior was tightened across classifier and processor caches.
- Core data structures and cache invalidation behavior were cleaned up.

### [2026.03.13] - 2026-03-13
- Documentation information architecture was reorganized.

### [2025.09.15] - 2025-09-15
- CLI entry points and optional LLM classification support were introduced.

## Full History

For older release details, use Git tags and GitHub releases.

[Unreleased]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.04.16...HEAD
[2026.04.16]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.03.13...v2026.04.16
[2026.03.13]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.09.15...v2026.03.13
[2025.09.15]: https://github.com/LessUp/bookmarks-cleaner/releases/tag/v2025.09.15
