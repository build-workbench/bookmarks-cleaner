# 2026-02-13 项目优化（第二轮）

## 概述

针对代码质量、性能、CI 和 CLI 体验进行多项优化升级。

## 变更内容

### 1. 修复版本号不一致（`pyproject.toml`）

- `version` 从 `0.1.0` 更正为 `2.0.0`，与文档和代码中的 `v2.0` 保持一致。

### 2. 补全打包声明（`pyproject.toml`）

- `[tool.setuptools] packages` 新增 `src.plugins`、`src.plugins.classifiers`、`src.services`，确保 `pip install .` 后这些子包能正确安装。

### 3. 优化 ThreadPoolExecutor 复用（`src/bookmark_processor.py`）

- `_classify_bookmarks_parallel` 原来每批 100 条书签都创建/销毁一个新的 `ThreadPoolExecutor`，现在改为**全局复用同一个线程池**，减少线程创建开销，提升批量分类性能。

### 4. 修复线程安全问题（`src/bookmark_processor.py`）

- 新增 `threading.Lock` (`_stats_lock`)，在多线程并行分类时保护 `self.stats` 字典的写入操作（`errors`、`categories_found`），消除竞态条件。

### 5. 优化 `_is_valid_url` 性能（`src/bookmark_processor.py`）

- 将无效 URL 前缀列表从局部变量 `list` 提升为类常量 `tuple`（`_INVALID_URL_PREFIXES`），利用 `str.startswith(tuple)` 一次性匹配，减少循环开销。

### 6. 修复导出时间戳过时问题（`src/data_exporter.py`）

- `export_timestamp` 从 `__init__` 时固定值改为 `@property`，每次导出时动态生成当前时间，避免复用 `DataExporter` 实例时时间戳陈旧。

### 7. 增强 CI workflow（`.github/workflows/ci.yml`）

- 新增独立的 `lint` job（flake8 检查严重语法错误：E9, F63, F7, F82）。
- `test` job 依赖 `lint` 通过后再运行。
- 统一使用 `pip install ".[dev]"` 安装运行依赖 + 开发依赖。
- pytest 添加 `--tb=short` 参数提升失败时的输出可读性。

### 8. 添加 `--version` CLI 参数（`main.py`）

- 新增 `-V` / `--version` 参数，输出 `cleanbook 2.0.0`。

### 9. 实现 `--limit` CLI 参数（`main.py` + `src/bookmark_processor.py`）

- 文档中已提及但此前未实现。现在 `--limit N` 可在加载书签后截断至前 N 条，方便调试和快速验证。
- `BookmarkProcessor.process_files` 新增 `limit` 参数。

## 影响范围

- 所有改动均保持向后兼容。
- `process_files` 新增的 `limit` 参数默认值为 `0`（不截断），不影响现有调用方。
