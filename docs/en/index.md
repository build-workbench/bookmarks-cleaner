---
layout: home
hero:
  name: CleanBook
  text: Offline-first bookmark cleanup for developers
  tagline: Rules-first · ML-assisted · LLM-optional · built for people with too many bookmarks
  image:
    src: /logo.svg
    alt: CleanBook
  actions:
    - theme: brand
      text: Start in 10 minutes
      link: /en/quickstart
    - theme: alt
      text: View on GitHub
      link: https://github.com/LessUp/bookmarks-cleaner
features:
  - icon: 🔒
    title: Actually offline
    details: Processing stays local by default. Your bookmarks and rules do not need a cloud account.
  - icon: ⚙️
    title: Config-driven
    details: Adjust categories, thresholds, and taxonomy files without rebuilding the tool.
  - icon: 🤖
    title: Rules first, AI where it helps
    details: Stable rule matches come first, with ML and optional LLM layers improving recall rather than replacing the whole pipeline.
  - icon: 📦
    title: Built to ship results
    details: Feed it browser-exported bookmark HTML and get cleaned HTML, JSON, and report-friendly output back.
---

## Why CleanBook

CleanBook is for people who already have a large bookmark pile and want to clean it up **without handing it to a hosted platform**. It is meant to help you deduplicate, classify, and export the collection you already own.

## Fastest path

```bash
pipx install cleanbook
cleanbook -i bookmarks.html -o output/
```

For the most stable execution path:

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## Who it fits

- **Individuals** cleaning years of saved browser bookmarks
- **Team maintainers** sharing classification rules and taxonomy files
- **Developers** studying bookmark-processing pipelines and CLI design

## Next steps

- [Quick Start](/en/quickstart)
- [Installation](/en/guide/installation)
- [Configuration](/en/reference/config)
- [Taxonomy](/en/reference/taxonomy)
