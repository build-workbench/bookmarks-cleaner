# CleanBook

<p align="center">
  <a href="https://pypi.org/project/cleanbook/"><img src="https://img.shields.io/pypi/v/cleanbook.svg?logo=pypi&logoColor=white" alt="PyPI"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT">
  <a href="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml"><img src="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://lessup.github.io/bookmarks-cleaner/"><img src="https://img.shields.io/badge/Docs-GitHub%20Pages-blue.svg" alt="Docs"></a>
</p>

<p align="center"><strong>Rules-first · ML-assisted · LLM-optional · Offline-first</strong></p>

<p align="center">
  <a href="./README.zh-CN.md">简体中文</a> ·
  <a href="https://lessup.github.io/bookmarks-cleaner/">Documentation</a> ·
  <a href="https://github.com/LessUp/bookmarks-cleaner/releases">Releases</a>
</p>

CleanBook is a command-line tool for **cleaning, deduplicating, and classifying browser bookmark exports**. It is designed for people who want a practical offline workflow: take an exported HTML bookmark file, run one command, and get a cleaner categorized result back.

## Why use it

- **Offline by default**: bookmark processing stays on your machine
- **Rules first**: stable category matches are driven by config, not opaque prompts
- **ML where it helps**: optional ML and LLM layers improve recall instead of owning the whole pipeline
- **Export-friendly**: generate cleaned bookmark HTML, JSON data, and report-style outputs

## Quick start

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

Stable rules-only mode:

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

From source:

```bash
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -e ".[dev]"
cleanbook -i examples/demo_bookmarks.html -o output/
```

Optional local extras:

```bash
pip install -e ".[dev,semantic]"   # sentence-transformers + hnswlib
pip install -e ".[dev,audit]"      # cleanlab-backed feedback data audit
```

Offline feedback loop:

```bash
cleanbook -i bookmarks.html -o output/ --export-review-queue output/review-queue.json
cleanbook --apply-feedback reviewed-feedback.json
cleanbook --train-feedback reviewed-feedback.json
cleanbook --audit-feedback reviewed-feedback.json --audit-output output/feedback-audit.json
```

## What it ships

- `cleanbook` — the maintained CLI entry point
- `cleanbook-wizard` — interactive wizard entry point
- `config.json` + taxonomy YAML files — the default classification surface

## Project shape

```text
main.py / cleanbook
  -> BookmarkProcessor
  -> classifier orchestration
  -> plugin pipeline
  -> services (feature store, taxonomy, performance, etc.)
```

## Documentation

- [Quick Start](https://lessup.github.io/bookmarks-cleaner/en/quickstart/)
- [Installation](https://lessup.github.io/bookmarks-cleaner/en/guide/installation/)
- [Configuration Reference](https://lessup.github.io/bookmarks-cleaner/en/reference/config/)
- [Taxonomy Reference](https://lessup.github.io/bookmarks-cleaner/en/reference/taxonomy/)

## Development

This repository uses **OpenSpec** as the only active change workflow:

1. `/opsx:explore`
2. `/opsx:propose`
3. `/opsx:apply`
4. `/opsx:archive`

Maintained verification baseline:

```bash
python3 -m pytest -q tests/test_runtime_paths.py
python3 -m pytest -q
```
