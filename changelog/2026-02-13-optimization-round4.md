# 2026-02-13 项目优化（第四轮）

## 概述

模块导入健壮性和代码质量清理。

## 变更内容

### 1. `performance_optimizer.py` — psutil 防御性导入

- `import psutil` 改为 `try/except ImportError` 包裹，缺少时设为 `None`。
- `start_monitoring()` 添加 `psutil is None` 守卫，避免运行时 `AttributeError`。

### 2. `plugins/classifiers/__init__.py` — 延迟导入

- 4 个插件类的急切导入改为 `__getattr__` 延迟导入，与 `services/__init__.py` 保持一致。
- 缺少可选依赖时 `import src.plugins.classifiers` 不再崩溃。

### 3. `enhanced_classifier.py` — 移除无点前缀后备导入

- 删除 `from ml_classifier import ...` 和 `from llm_classifier import ...` 两处嵌套后备导入。
- 包安装后这些无点前缀导入不会生效，仅增加混淆；保留 `.ml_classifier` 和 `.llm_classifier` 相对导入即可。

## 影响范围

- 所有改动向后兼容，无 API 变更。
