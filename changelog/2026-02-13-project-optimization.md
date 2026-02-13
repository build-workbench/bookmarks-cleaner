# 2026-02-13 项目整体优化

## 概述

对项目代码结构、依赖管理、配置文件进行全面优化清理。

## 变更内容

### 1. 提取重复代码 → `src/category_utils.py`（新增）

- 将 `ai_classifier.py` 和 `bookmark_processor.py` 中重复实现的 `_strip_category_prefix`、`_normalize_category_string`、`_normalize_category_config` 提取到共享模块 `category_utils.py`。
- 两个原模块保留静态方法签名，内部委托给共享函数，保持 API 兼容。

### 2. 拆分 `placeholder_modules.py`（2002 行 → 46 行转发层）

原始巨型文件拆分为 5 个独立模块：

| 新模块文件 | 类 | 职责 |
|---|---|---|
| `semantic_analyzer.py` | `SemanticAnalyzer` | 基于词向量和语义相似度的分类 |
| `user_profiler.py` | `UserProfiler` | 基于用户行为的个性化分类 |
| `deduplicator.py` | `BookmarkDeduplicator` | 高级相似度检测和去重 |
| `bookmark_health_checker.py` | `HealthChecker`, `HealthStatus` | 网络连接检测和书签状态验证 |
| `data_exporter.py` | `DataExporter` | 多格式书签导出 (HTML/JSON/MD/CSV/XML/OPML) |

`placeholder_modules.py` 保留为纯导入转发层，确保向后兼容。

### 3. 清理 `.gitignore`

- 移除自引用条目和重复项。
- 使用通配符 `output/`、`logs/`、`results/` 替代硬编码文件名。
- 新增忽略 `config_temp.json`。

### 4. 修复 `pyproject.toml`

- 将 `pytest>=8.2.2` 和 `pytest-cov>=5.0.0` 从 `dependencies` 移至 `[project.optional-dependencies] dev`。
- 修正 `Homepage` URL 指向正确的仓库地址。

### 5. 分离 `requirements.txt` / `requirements-dev.txt`

- 从 `requirements.txt` 中移除 `pytest` 和 `pytest-cov`。
- 将它们添加到 `requirements-dev.txt`。

### 6. 删除空文件

- 删除空文件 `src/second_pass_classifier.py`。

### 7. 修复 `src/health_checker.py`

- 移除函数内部重复的 `import sys` / `import os` 和冗余的 `sys.path` 操作。
- Python 版本检查从 `>= 3.8` 对齐至 `>= 3.10`（与 `pyproject.toml` 一致）。

### 8. 修复 `src/enhanced_cli.py`

- 移除不必要的 `sys.path.insert(0, ...)` 操作（包安装后无需手动修改路径）。

## 影响范围

- 所有改动均保持向后兼容，无 API 变更。
- 已通过导入测试验证拆分后模块加载正常。
