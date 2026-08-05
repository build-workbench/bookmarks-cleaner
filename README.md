# CleanBook

**规则优先 · ML 辅助 · LLM 可选 · 离线优先**

CleanBook 是一个命令行工具，用来 **清理、去重、分类浏览器书签导出文件**。输入浏览器导出的 HTML，跑一条命令，得到更干净、可导入、可分析的结果。全程留在本机。

## 为什么用

- **默认离线**：处理在本机完成，不依赖外部服务
- **规则优先**：分类基础由可维护的配置驱动，不靠黑盒提示词
- **AI 适度增强**：ML 和可选 LLM 提升覆盖率，不接管整条流水线
- **结果可复用**：输出清洗后的 HTML、JSON 数据和报告

## 快速开始

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

只走最稳定的规则路径：

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

## 项目结构

```text
main.py / cleanbook
  -> BookmarkProcessor
  -> 分类器编排（规则 -> ML -> LLM 可选）
  -> 插件流水线
  -> 服务层（feature store、taxonomy 等）
```

核心目录：`main.py`、`src/`、`config.json`、`taxonomy/`。

## 开发

验证基线：

```bash
pytest -q tests/test_runtime_paths.py
pytest -q
```

项目约定、架构和验证基线详见 `AGENTS.md`。变更历史见 `CHANGELOG.md`。
