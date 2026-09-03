# AGENTS.md

## 项目阶段

CleanBookmarks 是一个 **业余维护** 的离线书签清理与分类 CLI，仓库保持小巧、低维护。

## 产品边界

- **入口**：`cleanbookmarks`、`python main.py`
- **输入**：浏览器导出的书签 HTML
- **输出**：清洗后的 HTML、JSON 数据、markdown 报告
- **分类栈**：规则优先，LLM 可选（两级级联）

## 架构

```
main.py / cleanbookmarks CLI
  -> BookmarkProcessor (processor.py)
     -> BookmarkLoader (loader.py)
     -> BookmarkDeduplicator (deduplicator.py)
     -> BookmarkClassifier (classifier.py)
        -> RuleEngine (rules.py)
        -> LLMClassifier (llm.py, 可选)
     -> OrganizationPipeline (organizer.py)
     -> DataExporter (exporter.py)
```

## 目录结构

```
cleanbookmarks/
  __init__.py        版本号
  cli.py             CLI 入口 (argparse)
  processor.py       处理流程编排
  loader.py          HTML 书签加载
  deduplicator.py    去重
  classifier.py      分类器（规则+LLM 两级级联）
  rules.py           规则引擎
  url_analyzer.py    URL 智能分析
  organizer.py       分类组织与排序
  exporter.py        HTML/JSON/Markdown 导出
  taxonomy.py        分类法标准化
  text_utils.py      文本清理
  config.py          配置加载
  cache.py           LRU 缓存
  models.py          数据结构 (BookmarkFeatures, ClassificationResult)
  llm.py             LLM 分类器（可选，需 requests）
  health.py          健康检查
  resources/         打包资源（config.json, taxonomy/）
```

## 验证基线

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

## 文档

- README.md 为主（中文），README.en.md 为英文版，顶部互相链接
- 发布元数据 (pyproject readme) 指向中文 README

## 身份约定

- PyPI 包作者与 LICENSE 版权人：**holtwood**（个人）
- 仓库托管：**build-workbench/bookmarks-cleaner**（org），URL 一律指向该处
- git 提交身份保持个人（不随包署名改动）

## 约定

- 类型注解贯穿
- 公共 API 写 docstring
- 用 `logging.getLogger(__name__)` 而不是 `print`
- 中英文混用注释和文档均可
