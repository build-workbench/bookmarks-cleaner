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
      text: View on GitHub
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

<script setup>
import HomeHero from '../.vitepress/theme/components/HomeHero.vue'
import TerminalDemo from '../.vitepress/theme/components/TerminalDemo.vue'
import StatsCounter from '../.vitepress/theme/components/StatsCounter.vue'
import PipelineDiagram from '../.vitepress/theme/components/PipelineDiagram.vue'
import ProjectStructure from '../.vitepress/theme/components/ProjectStructure.vue'

const structure = [
  {
    name: 'src/',
    type: 'folder',
    desc: 'Source code directory',
    children: [
      { name: 'classifiers/', type: 'folder', desc: 'AI/ML/LLM classifiers' },
      { name: 'engines/', type: 'folder', desc: 'Rule/Semantic/URL engines' },
      { name: 'core/', type: 'folder', desc: 'Processor/Exporter/Deduplicator' },
      { name: 'llm/', type: 'folder', desc: 'LLM tools and prompts' },
      { name: 'health/', type: 'folder', desc: 'Health check modules' },
      { name: 'data/', type: 'folder', desc: 'Data processing modules' },
      { name: 'utils/', type: 'folder', desc: 'Config & utilities' },
      { name: 'cli/', type: 'folder', desc: 'Command-line interfaces' },
      { name: 'plugins/', type: 'folder', desc: 'Plugin system' },
      { name: 'services/', type: 'folder', desc: 'Service layer' },
    ]
  },
  {
    name: 'config/',
    type: 'folder',
    desc: 'Configuration directory',
    children: [
      { name: 'taxonomy/', type: 'folder', desc: 'Taxonomy vocabularies' },
      { name: 'agent/', type: 'folder', desc: 'Agent configurations' },
    ]
  },
  {
    name: 'docs/',
    type: 'folder',
    desc: 'Documentation (VitePress)'
  },
  {
    name: 'tests/',
    type: 'folder',
    desc: 'Test code'
  },
]

const terminalLines = [
  { type: 'input', content: 'cleanbook -i bookmarks.html -o output/', delay: 500 },
  { type: 'output', content: '✓ Loaded 1,247 bookmarks from bookmarks.html', delay: 300 },
  { type: 'output', content: '✓ Removed 23 duplicates', delay: 200 },
  { type: 'output', content: '✓ Classified 1,224 bookmarks (91.4% accuracy)', delay: 400 },
  { type: 'output', content: '✓ Generated output/bookmarks_clean.html', delay: 200 },
  { type: 'output', content: '✓ Done in 2.34s', delay: 100 },
  { type: 'input', content: 'cleanbook-wizard', delay: 800 },
]

const pipelineSteps = [
  {
    title: 'Data Parsing',
    description: 'Parse HTML/JSON bookmark files, extract URLs, titles, and folder structures',
    icon: '📄',
    meta: ['Netscape HTML', 'JSON', 'Chrome/Firefox']
  },
  {
    title: 'Smart Deduplication',
    description: 'URL normalization and multi-dimensional similarity detection for duplicate links',
    icon: '🔍',
    meta: ['URL Norm', 'SimHash', 'Levenshtein']
  },
  {
    title: 'Multi-Level Classification',
    description: 'Rules engine + ML + Semantic analysis + LLM fusion classification',
    icon: '🤖',
    meta: ['91.4% Acc', 'Fusion Voting', 'Auto-Fallback']
  },
  {
    title: 'Output Generation',
    description: 'Generate organized bookmark files and statistical reports',
    icon: '📦',
    meta: ['HTML', 'Markdown', 'JSON']
  },
]
</script>

<HomeHero
  :version="'2.0.0'"
  :statusText="'Stable'"
  :subtitle="'Smart Bookmark Cleaner & Classifier'"
  :description="'Rules-first, ML-assisted, LLM-optional. Offline-ready browser bookmark organization tool.'"
  :actions="[
    { text: 'Quick Start →', link: '/en/quickstart', theme: 'brand' },
    { text: 'GitHub', link: 'https://github.com/LessUp/bookmarks-cleaner', theme: 'alt' }
  ]"
/>

## Why CleanBook?

<StatsCounter
  :stats="[
    { value: 91.4, suffix: '%', label: 'Classification Accuracy', description: 'Tested on 10000+ bookmarks' },
    { value: 50, suffix: '+', label: 'Bookmarks/sec', description: 'Single-core processing' },
    { value: 0, suffix: '', label: 'Network Required', description: 'Runs offline by default' },
    { value: 3, suffix: '', label: 'Output Formats', description: 'HTML / JSON / Markdown' },
  ]"
/>

## Try It Now

<TerminalDemo
  :lines="terminalLines"
  :title="'cleanbook — bash'"
  :prompt="'$'"
/>

## Processing Pipeline

<PipelineDiagram
  :steps="pipelineSteps"
/>

## Core Features

### 🚀 Offline-First Design

CleanBook's core philosophy is "offline-first". **No cloud services required** to clean, deduplicate, classify and export your bookmarks. Your data never leaves your device.

### ⚙️ Configuration-Driven

All features can be configured via JSON — no code changes needed:

```json
{
  "category_rules": {
    "Technology/AI": {
      "rules": [
        { "match": "domain", "keywords": ["openai.com", "huggingface.co"], "weight": 15 }
      ]
    }
  },
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000
  }
}
```

### 🤖 Progressive Intelligence

Multi-layer classification with automatic fallback:

```
Rules Engine (30%) + ML Classifier (25%) + Semantic Analysis (20%) + LLM (15%) + User Profile (10%)
```

When any layer is unavailable, the system automatically redistributes weights to other layers, ensuring classification quality.

### 📦 Multi-Format Export

Support for multiple output formats to meet different needs:

| Format | Use Case | Features |
|--------|----------|----------|
| HTML | Browser Import | Standard Netscape format, all browsers supported |
| JSON | Data Analysis | Structured data for further processing |
| Markdown | Knowledge Base | Perfect for Notion/Obsidian |

## Get Started

### Installation

::: code-group

```bash [pipx - Recommended]
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [From Source]
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner && pip install .
```

:::

### First Run

```bash
# Basic cleaning
cleanbook -i bookmarks.html -o output/

# With ML training
cleanbook -i bookmarks.html --train

# Interactive wizard
cleanbook-wizard
```

## Target Users

CleanBook targets the scenario of "long-term browser bookmark maintenance":

- **Individual Users**: Heavy browser users who want to organize bookmarks offline first, then optionally introduce ML/LLM
- **Team Maintainers**: Technical leads who need unified team bookmark classification rules, vocabularies and output formats
- **Developers**: Open source contributors who want to understand bookmark processing pipelines and configuration-driven design

## Project Structure

<ProjectStructure title="Modular Project Structure" :structure="structure" />

CleanBook adopts a clear modular directory structure for easy maintenance and extension:

- **`src/classifiers/`** - Layered classifiers: Rules → ML → LLM
- **`src/engines/`** - Core engines: rule matching, semantic analysis, URL parsing
- **`src/core/`** - Core processing: BookmarkProcessor, exporter, deduplicator
- **`src/llm/`** - LLM related: organizer, prompt builder, exporter
- **`src/health/`** - System health checks
- **`src/data/`** - Data processing layer
- **`src/utils/`** - Utilities and config management
- **`src/cli/`** - Unified CLI entry point
- **`config/`** - Centralized configuration management

---

## Learning Paths

### I just want to organize my bookmarks
1. [Quick Start](/en/quickstart) - Installation and basic usage
2. [Best Practices](/en/guide/best-practices) - Classification strategies and organization habits
3. [LLM Templates](/en/reference/llm-templates) - Optimize classification quality

### I want to understand how it works
1. [Design Overview](/en/design/overview) - Overall architecture philosophy
2. [System Architecture](/en/design/architecture) - Module design and data flow
3. [ML Design](/en/design/ml-design) - Classification algorithms and models

### I want to contribute
1. [Development Guide](/en/guide/development) - Environment setup and contribution guidelines
2. [Design Overview](/en/design/overview) - Understand core design decisions
3. [Technical Report](/en/advanced/technical-report) - Deep technical details

---

<p align="center" style="margin-top: 4rem;">
  <a href="https://github.com/LessUp/bookmarks-cleaner" target="_blank">
    <img src="https://img.shields.io/github/stars/LessUp/bookmarks-cleaner?style=social" alt="GitHub Stars">
  </a>
</p>

<p align="center" style="color: var(--vp-c-text-3); margin-top: 1rem;">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
