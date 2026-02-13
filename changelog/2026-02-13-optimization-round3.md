# 2026-02-13 项目优化（第三轮）

## 概述

去重性能优化、服务层健壮性提升、词表补全和健康检查修正。

## 变更内容

### 1. 去重器性能优化（`src/deduplicator.py`）

- `remove_duplicates` 从全局 O(n²) 逐一比较改为**按域名预分组**后组内比较。
- 重复书签几乎总是同域名，分桶后每个桶内的 m 远小于 n，总体复杂度从 O(n²) 降至 ΣO(mᵢ²)。
- 对于 4000+ 书签跨浏览器合并场景，预期提速 5-10 倍。

### 2. 服务层延迟导入（`src/services/__init__.py`）

- 将 7 个服务类的急切 `from ... import` 改为 `__getattr__` 延迟导入。
- 效果：缺少可选依赖（如 numpy/sklearn）时，`import src.services` 不再崩溃，仅在实际访问具体服务时才触发 ImportError。

### 3. 受控词表补全（`taxonomy/subjects.yaml`）

- 新增「工作台」主题及其变体（司内业务、内部工具、Workspace）。
- 修复 `config.json` 中 `💼 工作台` 分类经 `TaxonomyStandardizer` 标准化后找不到对应主题的问题。

### 4. 健康检查目录修正（`src/health_checker.py`）

- `required_dirs` 从 `tests/input`、`tests/output`（已被 gitignore）改为 `examples`、`taxonomy`（项目实际使用的目录）。

## 影响范围

- 所有改动向后兼容。
- `deduplicator.remove_duplicates` 返回值和行为不变，仅内部算法优化。
- `services/__init__` 公开 API 不变，仅导入时机延后。
