# AGENTS.md

## 项目阶段

CleanBook 是一个 **业余维护** 的离线书签清理与分类 CLI，仓库保持小巧、低维护。

## 产品边界

- **入口**：`cleanbook`、`python main.py`
- **输入**：浏览器导出的书签 HTML
- **输出**：清洗后的 HTML、JSON 数据、markdown 报告
- **分类栈**：规则优先，ML 辅助，LLM 可选

## 架构

```
CLI / main.py
  -> BookmarkProcessor
  -> classifier orchestration
  -> plugin pipeline
  -> services (feature store, taxonomy, etc.)
```

## 验证基线

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

## 约定

- 类型注解贯穿
- 公共 API 写 docstring
- 用 `logging.getLogger(__name__)` 而不是 `print`
- 中英文混用注释和文档均可
