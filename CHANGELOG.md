# 更新日志

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [Unreleased]

### Added
- 预编译正则表达式优化（ai_classifier, llm_classifier, ml_classifier, semantic_analyzer, user_profiler）
- 统一的 ClassificationResult 数据类定义

### Changed
- 所有缓存改用 OrderedDict 实现 LRU 淘汰机制
- 更新系统架构文档以反映最新代码结构

---

## [2026.04] - 2026-04-16

### Performance
- **缓存优化**: 将所有缓存从普通 dict 改为 OrderedDict 实现 LRU 淘汰
  - `AIBookmarkClassifier.feature_cache`: 最大 10,000 条
  - `AIBookmarkClassifier.classification_cache`: 最大 5,000 条
  - `BookmarkProcessor._classification_cache`: 最大 10,000 条
  - `EnhancedClassifier` 所有缓存: 最大 10,000 条

### Code Quality
- **预编译正则**: 在模块级别预编译常用正则表达式
  - `_CHINESE_REGEX`, `_ENGLISH_REGEX`, `_DIGIT_REGEX`, `_WORD_REGEX`
- **统一数据结构**: ClassificationResult 统一定义在 `ai_classifier.py`，其他模块从此导入
- **缓存失效修复**: `learn_from_feedback()` 现在同时清理 feature_cache 和 classification_cache

---

## [2026.03] - 2026-03-13

### Docs
- 文档信息架构规范化
- README 与 docs/index.md 职责分离
- 统一导航命名：概览、快速开始、使用指南、架构设计、开发指南

---

## [2026.02] - 2026-02-13

### Refactor
- 提取重复代码到 `src/category_utils.py`
- 拆分 `placeholder_modules.py` (2002行 → 46行转发层)
  - 新增: `semantic_analyzer.py`, `user_profiler.py`, `deduplicator.py`
  - 新增: `bookmark_health_checker.py`, `data_exporter.py`

### Fixed
- 清理 `.gitignore` 重复项
- 修复 `pyproject.toml` 依赖配置
- 分离 `requirements.txt` / `requirements-dev.txt`
- 删除空文件 `src/second_pass_classifier.py`

---

## [2025.12] - 2025-12-14 至 2025-12-19

### Added
- CI/CD 配置 (GitHub Actions)
- 可选依赖支持 (watchdog, pytest)
- CLI 分类标准化功能
- 性能监控桥接

### Fixed
- enhanced_classifier 导入错误
- ML 分类器警告噪音
- Python 3.10 兼容性

---

## [2025.10] - 2025-10-20

### Added
- 文档清理与重组
- Phase 1 & Phase 2 优化

---

## [2025.09] - 2025-09-15

### Added
- LLM 分类器集成
- Emoji 清理功能
- 包管理与 CLI 重构

---

## 版本说明

- **主版本号**: 重大架构变更
- **次版本号**: 新功能添加
- **修订号**: Bug 修复与小改进

[Unreleased]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.04...HEAD
