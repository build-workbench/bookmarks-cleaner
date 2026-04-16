# 更新日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [日历版本控制](https://calver.org/)。

## [未发布]

### 新增
- 双语文档支持（中文和英文）
- 专业的 VitePress 文档站点
- 插件开发的完整 API 文档

### 变更
- 重构文档结构，分为 `zh/` 和 `en/` 目录
- 增强 README，添加徽章和专业布局

---

## [2026.04.16] - 2026-04-16

### 性能优化
- **LRU 缓存优化**: 将所有缓存从普通 dict 改为 OrderedDict 实现 LRU 淘汰
  - `AIBookmarkClassifier.feature_cache`: 最大 10,000 条
  - `AIBookmarkClassifier.classification_cache`: 最大 5,000 条
  - `BookmarkProcessor._classification_cache`: 最大 10,000 条

### 代码质量
- **预编译正则**: 在模块级别预编译常用正则表达式
  - `_CHINESE_REGEX`, `_ENGLISH_REGEX`, `_DIGIT_REGEX`, `_WORD_REGEX`
- **统一数据结构**: ClassificationResult 统一定义在 `ai_classifier.py`
- **缓存失效修复**: `learn_from_feedback()` 现在同时清理 feature_cache 和 classification_cache

---

## [2026.03.13] - 2026-03-13

### 文档
- 文档信息架构规范化
- README 与 docs/index.md 职责分离
- 统一导航：概览、快速开始、使用指南、架构设计、开发指南

---

## [2026.02.13] - 2026-02-13

### 重构
- 提取重复代码到 `src/category_utils.py`
- 拆分 `placeholder_modules.py` (2002行 → 46行转发层)
  - 新增: `semantic_analyzer.py`, `user_profiler.py`, `deduplicator.py`
  - 新增: `bookmark_health_checker.py`, `data_exporter.py`

### 修复
- 清理 `.gitignore` 重复项
- 修复 `pyproject.toml` 依赖配置
- 分离 `requirements.txt` / `requirements-dev.txt`
- 删除空文件 `src/second_pass_classifier.py`

---

## [2025.12.19] - 2025-12-19

### 新增
- 阈值和规则引擎扩展

### 修复
- 增强分类器 ML 可用性保护

---

## [2025.12.18] - 2025-12-18

### 新增
- CLI 分类标准化功能
- CLI 界面功能完善

### 修复
- 性能监控桥接和输出顺序

---

## [2025.12.15] - 2025-12-15

### 修复
- ML 分类器警告噪音减少

---

## [2025.12.14] - 2025-12-14

### 新增
- CI/CD 配置 (GitHub Actions)
- 可选依赖支持 (watchdog, pytest)
- CLI 分类标准化功能
- 性能监控桥接

### 修复
- enhanced_classifier 导入错误
- Python 3.10 兼容性

---

## [2025.10.20] - 2025-10-20

### 新增
- 文档清理与重组
- Phase 1 & Phase 2 优化

---

## [2025.09.15] - 2025-09-15

### 新增
- LLM 分类器集成（OpenAI 兼容）
- Emoji 清理功能
- 包管理与 CLI 重构
- `cleanbook` 和 `cleanbook-wizard` 入口点

---

## 版本说明

本项目使用日历版本控制：

- **YYYY.MM.DD** - 基于发布日期的版本号
- **重大变更** - 重要的架构更新
- **功能新增** - 新功能
- **Bug 修复** - 小幅改进和修复

[未发布]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.04.16...HEAD
[2026.04.16]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.03.13...v2026.04.16
[2026.03.13]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.02.13...v2026.03.13
[2026.02.13]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.19...v2026.02.13
[2025.12.19]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.18...v2025.12.19
[2025.12.18]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.15...v2025.12.18
[2025.12.15]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.14...v2025.12.15
[2025.12.14]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.10.20...v2025.12.14
[2025.10.20]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.09.15...v2025.10.20
[2025.09.15]: https://github.com/LessUp/bookmarks-cleaner/releases/tag/v2025.09.15
