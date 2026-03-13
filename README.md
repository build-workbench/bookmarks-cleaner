# CleanBook — Smart Bookmark Cleaning & Classification

[![CI](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml)
[![Docs](https://github.com/LessUp/bookmarks-cleaner/actions/workflows/pages.yml/badge.svg)](https://lessup.github.io/bookmarks-cleaner/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

English | [简体中文](README.zh-CN.md) | [Docs](https://lessup.github.io/bookmarks-cleaner/)

CleanBook is a bookmark cleaning and classification tool with an offline-first pipeline: rules and local ML by default, optional OpenAI-compatible LLM when you need semantic assistance.

## Repository Overview

- CLI-first workflow with `cleanbook` and `cleanbook-wizard`
- Configurable taxonomy, rules, and thresholds in `config.json`
- Multi-format export to HTML, Markdown, and JSON
- Dedicated docs site for quick start, architecture, and development workflow

## Quick Start

```powershell
pipx install .
cleanbook -i examples/demo_bookmarks.html -o output
```

Run directly from source if you do not want an isolated CLI install:

```powershell
python main.py -i examples/demo_bookmarks.html -o output
```

## Read Next

- [Quick Start](https://lessup.github.io/bookmarks-cleaner/quickstart_zh)
- [System Architecture](https://lessup.github.io/bookmarks-cleaner/design/system_architecture)
- [Development Guide](https://lessup.github.io/bookmarks-cleaner/guides/development_guide)

## License

MIT — see `LICENSE`.
