---
layout: home

hero:
  name: CleanBook
  text: Smart Bookmark Cleaner & Classifier
  tagline: Rules-first, ML-assisted, LLM-optional. Offline-ready browser bookmark organization tool.
  image:
    src: /logo.svg
    alt: CleanBook Logo
  actions:
    - theme: brand
      text: Quick Start
      link: /en/quickstart
    - theme: alt
      text: Architecture
      link: /en/design/architecture
    - theme: alt
      text: GitHub
      link: https://github.com/LessUp/bookmarks-cleaner

features:
  - icon: 🚀
    title: Offline-First
    details: Complete cleaning, deduplication, classification and export without cloud services. Perfect for local batch processing and long-term maintenance. Rule engine responds in sub-milliseconds.
  - icon: ⚙️
    title: Config-Driven
    details: Adjust rules, thresholds and directory organization via config.json and vocabulary files. No code changes needed. YAML vocabularies support controlled vocabulary and faceted classification.
  - icon: 🤖
    title: Progressive Enhancement
    details: Layer ML, semantic analysis and optional OpenAI-compatible LLM on top of rules. Automatic fallback when services are unavailable. No worries about service availability.
  - icon: 📦
    title: Multi-Format Export
    details: Export to HTML, Markdown, JSON and more. Supports browser re-import, knowledge base archiving, and further processing needs.
  - icon: 🔧
    title: CLI-First
    details: Provides cleanbook CLI tool and cleanbook-wizard interactive interface. Supports batch processing and automation integration.
  - icon: 📊
    title: Smart Classification
    details: Multi-level feature extraction based on domain, title, and URL. Fusion of rule engine and machine learning achieves 91.4% classification accuracy.
---

## Project Positioning

CleanBook targets the scenario of "long-term browser bookmark maintenance":
start with cleaning, deduplication and normalization, then organize links
into stable, readable, and sustainably evolving classification structures
based on rules and models.

## Who is it For

- **Individual Users**: Heavy browser users who want to organize bookmarks
  offline first, then optionally introduce ML/LLM
- **Team Maintainers**: Technical leads who need unified team bookmark
  classification rules, vocabularies and output formats
- **Developers**: Open source contributors who want to understand bookmark
  processing pipelines, classification fusion and configuration-driven design

## Where to Start

1. Read the [**Quick Start**](/en/quickstart) guide to complete a minimal run
2. Review [**Best Practices**](/en/guide/best-practices) to establish
   classification rules and organization habits
3. When you need to understand the implementation, continue reading
   [**System Architecture**](/en/design/architecture) and
   [**Development Guide**](/en/guide/development)

## Recommended Reading Paths

::: tip I just want to organize my bookmarks
- [Quick Start](/en/quickstart)
- [Best Practices](/en/guide/best-practices)
- [LLM Prompt Templates](/en/reference/llm-templates)
:::

::: tip I want to understand how the system works
- [Design Overview](/en/design/overview)
- [System Architecture](/en/design/architecture)
- [ML Design](/en/design/ml-design)
:::

::: tip I want to contribute to development
- [Development Guide](/en/guide/development)
- [Design Overview](/en/design/overview)
- [Technical Report](/en/advanced/technical-report)
:::

## Core Documentation

| Category | Page | Description |
|----------|------|-------------|
| Quick Start | [Quick Start](/en/quickstart) | Installation, minimal example, common parameters |
| User Guide | [Best Practices](/en/guide/best-practices) | Configuration ideas, directory organization and maintenance tips |
| Architecture | [Design Overview](/en/design/overview) / [System Architecture](/en/design/architecture) | Pipeline, module boundaries and classification strategies |
| Development | [Development Guide](/en/guide/development) | Environment setup, testing and extension points |
| Reference | [LLM Templates](/en/reference/llm-templates) | Prompt structure and optional interface configuration |
| Archive | [Technical Report](/en/advanced/technical-report) | Historical supplementary materials and extended notes |

---

<footer style="text-align: center; margin-top: 4rem; padding: 2rem 0; border-top: 1px solid var(--vp-c-divider);">
  <p>Released under MIT License · Copyright © 2025-2026 LessUp</p>
  <p style="margin-top: 0.5rem;">
    <a href="/zh/">中文</a> · <a href="https://github.com/LessUp/bookmarks-cleaner">GitHub</a> · <a href="https://github.com/LessUp/bookmarks-cleaner/releases">Releases</a>
  </p>
</footer>
