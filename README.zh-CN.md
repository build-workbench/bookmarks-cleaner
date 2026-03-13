# CleanBook —— 智能书签清理与分类

[![CI](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml)
[![Docs](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/pages.yml/badge.svg)](https://lessup.github.io/bookmarks-cleaner/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

[English](README.md) | 简体中文 | [文档站](https://lessup.github.io/bookmarks-cleaner/)

CleanBook 是一个浏览器书签清理与分类工具：默认走规则 + 本地 ML 的离线路径，需要时再接入 OpenAI 兼容 LLM 做语义增强。

## 仓库入口

- 提供 `cleanbook` 与 `cleanbook-wizard` 两个 CLI 入口
- 通过 `config.json` 配置分类规则、词表与阈值
- 输出 HTML、Markdown、JSON 三种结果格式
- 详细使用方法、架构说明与开发流程统一放在文档站中维护

## 快速开始

```powershell
pipx install .
cleanbook -i examples/demo_bookmarks.html -o output
```

如果你更想直接从源码运行：

```powershell
python main.py -i examples/demo_bookmarks.html -o output
```

## 接下来读什么

- [快速上手](https://lessup.github.io/bookmarks-cleaner/quickstart_zh)
- [系统架构](https://lessup.github.io/bookmarks-cleaner/design/system_architecture)
- [开发指南](https://lessup.github.io/bookmarks-cleaner/guides/development_guide)

## 许可证

MIT，见 `LICENSE`。
