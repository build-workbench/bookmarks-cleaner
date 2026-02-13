# 2026-02-13 项目优化（第五轮）

## 概述

代码质量清理：消除裸 except、移除残留 sys.path.insert 和无点前缀导入。

## 变更内容

### 1. 修复 5 处裸 `except:` → `except Exception:`

| 文件 | 行数 | 上下文 |
|------|------|--------|
| `src/bookmark_processor.py` | 1 处 | lxml 解析器回退 |
| `src/performance_optimizer.py` | 1 处 | cache_clear 回退 |
| `src/advanced_features.py` | 3 处 | URL 解析、域名提取 |

裸 `except:` 会捕获 `KeyboardInterrupt` 和 `SystemExit` 等不应被静默吞掉的异常。

### 2. 清理 `sys.path.insert` 和无点前缀导入

| 文件 | 改动 |
|------|------|
| `src/plugins/classifiers/embedding_classifier.py` | 移除 `sys.path.insert`，`from plugins.base` → `from ..base` |
| `src/enhanced_clean_tidy.py` | 移除 `sys.path.insert`，`from emoji_cleaner` → `from .emoji_cleaner`，`from enhanced_classifier` → `from .enhanced_classifier` |
| `src/advanced_features.py` | 移除 `sys.path.insert`（此文件不依赖同包其他模块的顶层导入） |

包安装后无点前缀导入不会生效，`sys.path.insert` 在已安装环境中是多余且有害的（会引入路径污染）。

## 影响范围

- 所有改动向后兼容。
- 以 `pip install .` 或 `pip install -e .` 方式安装后行为不变。
