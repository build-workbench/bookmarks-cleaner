---
layout: home
hero:
  name: Bookmarks Cleaner
  text: Offline-first Smart Bookmark Cleanup Tool
  tagline: Rules-first · ML-assisted · LLM-optional
  actions:
    - theme: brand
      text: Get Started
      link: /en/guide/installation
features:
  - icon: 🔒
    title: Offline-first
    details: All core features run offline, your data never leaves your device
  - icon: 📏
    title: Rule Engine
    details: Domain-based smart classification with customizable rules
  - icon: 🤖
    title: ML-assisted
    details: Optional ML enhancement with incremental and active learning
  - icon: 🧠
    title: LLM-optional
    details: Support for OpenAI and local LLM enhanced classification
  - icon: 🔄
    title: Multi-browser
    details: Support Chrome, Edge, Firefox, Safari
  - icon: 📊
    title: Multi-format Reports
    details: HTML, JSON, Markdown export formats
---

<HeroTerminal />

## Quick Start

Install:

```bash
pipx install cleanbook
```

Usage:

```bash
cleanbook -i bookmarks.html -o output/
```

See [Installation Guide](/en/guide/installation) for details.

## Why Bookmarks Cleaner

| Feature | Bookmarks Cleaner | Traditional Tools |
|---------|-------------------|-------------------|
| Offline | ✅ Fully offline | ❌ Needs internet |
| Smart Classification | ✅ Rules + ML + LLM | ❌ Manual |
| Data Privacy | ✅ Local processing | ❌ Cloud upload |
| Open Source | ✅ MIT License | ❌ Paid subscription |

## Learn More

- [Pipeline Architecture](/en/architecture/pipeline) - 5-stage processing pipeline
- [Fusion Algorithm](/en/algorithms/fusion) - Multi-classifier weighted fusion
- [Performance](/en/performance/concurrency) - Concurrency and caching
