# CleanBook

<p align="center">
  <a href="https://pypi.org/project/cleanbook/"><img src="https://img.shields.io/pypi/v/cleanbook.svg?logo=pypi&logoColor=white" alt="PyPI"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT">
  <a href="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml"><img src="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://lessup.github.io/bookmarks-cleaner/"><img src="https://img.shields.io/badge/文档-GitHub%20Pages-blue.svg" alt="Docs"></a>
</p>

<p align="center"><strong>规则优先 · ML 辅助 · LLM 可选 · 离线优先</strong></p>

<p align="center">
  <a href="https://lessup.github.io/bookmarks-cleaner/">文档</a> ·
  <a href="https://github.com/LessUp/bookmarks-cleaner/releases">发布</a>
</p>

CleanBook 是一个用于 **清理、去重、分类浏览器书签导出文件** 的命令行工具。它面向那些希望以离线方式整理历史书签的用户：输入浏览器导出的 HTML，运行一条命令，得到更干净、更可导入、更可分析的结果。

## 为什么使用它

- **默认离线**：书签处理留在本机完成
- **规则优先**：分类基础由可维护的配置驱动，而不是完全依赖黑盒提示词
- **AI 适度增强**：ML 和可选 LLM 用于提升覆盖率，而不是接管整条流水线
- **结果可复用**：输出清洗后的 HTML、JSON 数据和报告式结果

## 快速开始

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

如果你想走最稳定的规则路径：

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

## 当前维护的入口

- `cleanbook` — 主 CLI 入口
- `cleanbook-wizard` — 交互式向导
- `config.json` 与 taxonomy YAML — 默认分类配置面

## 项目结构

```text
main.py / cleanbook
  -> BookmarkProcessor
  -> 分类器编排
  -> 插件流水线
  -> 服务层（feature store、taxonomy、performance 等）
```

## 文档入口

- [快速开始](https://lessup.github.io/bookmarks-cleaner/zh/quickstart/)
- [安装指南](https://lessup.github.io/bookmarks-cleaner/zh/guide/installation/)
- [配置说明](https://lessup.github.io/bookmarks-cleaner/zh/reference/config/)
- [词表格式](https://lessup.github.io/bookmarks-cleaner/zh/reference/taxonomy/)

## 开发流程

本仓库使用 **OpenSpec** 作为唯一活跃变更流程：

1. `/opsx:explore`
2. `/opsx:propose`
3. `/opsx:apply`
4. `/opsx:archive`

当前维护的验证基线：

```bash
python3 -m pytest -q tests/test_runtime_paths.py
python3 -m pytest -q
```
