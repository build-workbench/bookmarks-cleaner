# 2026-02-13 项目优化（第六轮）

## 概述

最终清理：防御性导入补全、包版本号统一。

## 变更内容

### 1. `src/enhanced_clean_tidy.py` — bs4 防御性导入

- `from bs4 import BeautifulSoup` 改为 `try/except ImportError` 包裹，与 `bookmark_processor.py` 保持一致。

### 2. `src/__init__.py` — 添加 `__version__`

- 新增 `__version__ = "2.0.0"`，便于 `from src import __version__` 程序化访问版本号。

## 影响范围

- 向后兼容，无 API 变更。
