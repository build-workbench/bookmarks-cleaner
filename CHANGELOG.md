# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Calendar Versioning](https://calver.org/).

## [Unreleased]

### Added
- Bilingual documentation support (Chinese & English)
- Professional VitePress documentation site
- Comprehensive API documentation for plugin development

### Changed
- Restructured documentation with `zh/` and `en/` directories
- Enhanced README with badges and professional layout

---

## [2026.04.16] - 2026-04-16

### Performance
- **LRU Cache Optimization**: Migrated all caches from plain dict to OrderedDict for LRU eviction
  - `AIBookmarkClassifier.feature_cache`: Max 10,000 entries
  - `AIBookmarkClassifier.classification_cache`: Max 5,000 entries
  - `BookmarkProcessor._classification_cache`: Max 10,000 entries

### Code Quality
- **Pre-compiled Regex**: Module-level pre-compilation of commonly used patterns
  - `_CHINESE_REGEX`, `_ENGLISH_REGEX`, `_DIGIT_REGEX`, `_WORD_REGEX`
- **Unified Data Structure**: ClassificationResult centrally defined in `ai_classifier.py`
- **Cache Invalidation Fix**: `learn_from_feedback()` now clears both feature_cache and classification_cache

---

## [2026.03.13] - 2026-03-13

### Documentation
- Information architecture standardization
- Separation of concerns between README and docs/index.md
- Unified navigation: Overview, Quick Start, Guides, Design, Development

---

## [2026.02.13] - 2026-02-13

### Refactored
- Extracted duplicate code to `src/category_utils.py`
- Split `placeholder_modules.py` (2002 lines → 46-line forwarding layer)
  - Added: `semantic_analyzer.py`, `user_profiler.py`, `deduplicator.py`
  - Added: `bookmark_health_checker.py`, `data_exporter.py`

### Fixed
- Cleaned up `.gitignore` duplicates
- Fixed `pyproject.toml` dependency configuration
- Separated `requirements.txt` / `requirements-dev.txt`
- Removed empty file `src/second_pass_classifier.py`

---

## [2025.12.19] - 2025-12-19

### Added
- Threshold and rule engine extensions

### Fixed
- Enhanced classifier ML availability guard

---

## [2025.12.18] - 2025-12-18

### Added
- CLI category normalization
- CLI interface feature completion

### Fixed
- Performance monitor bridge and output order

---

## [2025.12.15] - 2025-12-15

### Fixed
- ML classifier warning noise reduction

---

## [2025.12.14] - 2025-12-14

### Added
- CI/CD configuration (GitHub Actions)
- Optional dependency support (watchdog, pytest)
- CLI classification standardization
- Performance monitoring bridge

### Fixed
- Enhanced classifier import error
- Python 3.10 compatibility

---

## [2025.10.20] - 2025-10-20

### Added
- Documentation cleanup and reorganization
- Phase 1 & Phase 2 optimizations

---

## [2025.09.15] - 2025-09-15

### Added
- LLM classifier integration (OpenAI-compatible)
- Emoji cleanup functionality
- Package management and CLI refactoring
- `cleanbook` and `cleanbook-wizard` entry points

---

## Version Format

This project uses calendar versioning:

- **YYYY.MM.DD** - Release date based versioning
- **Major changes** - Significant architecture updates
- **Feature additions** - New functionality
- **Bug fixes** - Small improvements and fixes

[Unreleased]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.04.16...HEAD
[2026.04.16]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.03.13...v2026.04.16
[2026.03.13]: https://github.com/LessUp/bookmarks-cleaner/compare/v2026.02.13...v2026.03.13
[2026.02.13]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.19...v2026.02.13
[2025.12.19]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.18...v2025.12.19
[2025.12.18]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.15...v2025.12.18
[2025.12.15]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.12.14...v2025.12.15
[2025.12.14]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.10.20...v2025.12.14
[2025.10.20]: https://github.com/LessUp/bookmarks-cleaner/compare/v2025.09.15...v2025.10.20
[2025.09.15]: https://github.com/LessUp/bookmarks-cleaner/releases/tag/v2025.09.15
