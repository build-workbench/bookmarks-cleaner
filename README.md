# CleanBook

**规则优先 · ML 辅助 · LLM 可选 · 离线优先**

CleanBook 是一个命令行工具，用来 **清理、去重、分类浏览器书签导出文件**。输入浏览器导出的 HTML，跑一条命令，得到更干净、可导入、可分析的结果。全程留在本机。

## 快速开始

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

只走规则路径（不装 ML 依赖）：

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

从源码运行：

```bash
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e ".[dev]"
cleanbook -i examples/demo_bookmarks.html -o output/
```

安装可选能力：

```bash
pip install -e ".[ml]"     # 机器学习分类
pip install -e ".[llm]"    # LLM 分类（需配置 API Key）
```

## 架构

```
main.py / cleanbook
  -> BookmarkProcessor          # 编排 load -> dedup -> classify -> organize -> export
  -> BookmarkClassifier         # 规则优先 + ML(可选) + LLM(可选)，加权融合
  -> BookmarkDeduplicator       # 两阶段去重（URL 精确 + 相似度）
  -> OrganizationPipeline       # subject/resource_type 两级组织
  -> DataExporter               # HTML / JSON / Markdown 导出
```

核心目录：`main.py`、`cleanbook/`、`config.json`、`taxonomy/`。

## 开发

```bash
pytest -q tests/test_runtime_paths.py   # 快速路径验证
pytest -q                                # 全量测试
```

项目约定详见 `AGENTS.md`。
