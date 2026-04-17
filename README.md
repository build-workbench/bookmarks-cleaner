# CleanBook — Smart Bookmark Cleaning & Classification

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platform">
  <a href="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml">
    <img src="https://github.com/LessUp/bookmarks-cleaner/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://lessup.github.io/bookmarks-cleaner/">
    <img src="https://img.shields.io/badge/Docs-VitePress-blue.svg" alt="Documentation">
  </a>
</p>

<p align="center">
  <b>Rules-first · ML-assisted · LLM-optional · Offline-ready</b>
</p>

<p align="center">
  <a href="./README.zh-CN.md">简体中文</a> |
  <a href="https://lessup.github.io/bookmarks-cleaner/">Documentation</a> |
  <a href="https://github.com/LessUp/bookmarks-cleaner/releases">Releases</a>
</p>

---

CleanBook is an **open-source, offline-first** bookmark cleaning and classification tool. It transforms chaotic browser bookmark collections into well-organized, categorized libraries using a hybrid approach that prioritizes rules, enhances with machine learning, and optionally leverages LLM capabilities.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Offline-First** | Complete pipeline runs locally without cloud services. Perfect for local batch processing and long-term maintenance |
| 🤖 **Hybrid Classification** | Rule engine + ML classifier (91.4% accuracy) + optional LLM fallback. Automatic degradation when services unavailable |
| ⚙️ **Configuration-Driven** | Customize rules, thresholds, and vocabularies via JSON/YAML—no code changes required |
| 📦 **Multi-Format Export** | Export to HTML (Netscape), Markdown (reports), and JSON (structured data) |
| 🔧 **CLI + Wizard** | Command-line tool for automation, interactive wizard for guided experience |
| 🎯 **Smart Deduplication** | URL normalization and multi-dimensional similarity detection |
| 💾 **LRU Caching** | Intelligent caching with automatic eviction for optimal performance |

## 🚀 Quick Start

### Installation

```bash
# Via pipx (recommended for isolated environment)
pipx install cleanbook

# Via pip
pip install cleanbook

# From source
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install .
```

### Basic Usage

```bash
# Process a bookmark HTML file
cleanbook -i bookmarks.html -o output/

# Interactive wizard mode
cleanbook-wizard

# With ML training enabled
cleanbook -i bookmarks.html --train

# Health check
cleanbook --health-check
```

## 📊 Classification Pipeline

```
HTML Bookmarks
    ↓
┌─────────────────────────────────────────────────────┐
│  1. Rule Engine (Fast, 0.1ms, Priority: 0.3)       │
│     Domain/Title/URL pattern matching               │
├─────────────────────────────────────────────────────┤
│  2. ML Classifier (91.4% accuracy, Priority: 0.25) │
│     TF-IDF + Ensemble (RF + LR + Naive Bayes)      │
├─────────────────────────────────────────────────────┤
│  3. Semantic Analysis (Priority: 0.2)              │
│     Word vectors, TF-IDF similarity                │
├─────────────────────────────────────────────────────┤
│  4. LLM Classifier (Optional, Priority: 0.15)      │
│     OpenAI-compatible API with auto-fallback       │
└─────────────────────────────────────────────────────┘
    ↓
Weighted Voting Fusion → Organized Output
```

## 🏗️ Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│    Input     │───▶│   Process    │───▶│     Output       │
│  bookmarks   │    │  ┌────────┐  │    │  bookmarks.html  │
│   .html      │    │  │ Parse  │  │    │  bookmarks.json  │
└──────────────┘    │  │ Deduplicate  │  │    │  report.md       │
                    │  │ Classify│  │    └──────────────────┘
                    │  │ Organize│  │
                    │  └────────┘  │
                    └──────────────┘
                         ↓
                    ┌──────────────┐
                    │  Config      │
                    │  ├─ Rules    │
                    │  ├─ ML Model │
                    │  └─ Taxonomy │
                    └──────────────┘
```

## 📖 Documentation

| Resource | Link |
|----------|------|
| **Homepage** | [lessup.github.io/bookmarks-cleaner](https://lessup.github.io/bookmarks-cleaner/) |
| **Quick Start** | [/en/quickstart](https://lessup.github.io/bookmarks-cleaner/en/quickstart) |
| **Best Practices** | [/en/guide/best-practices](https://lessup.github.io/bookmarks-cleaner/en/guide/best-practices) |
| **Architecture** | [/en/design/architecture](https://lessup.github.io/bookmarks-cleaner/en/design/architecture) |
| **Development** | [/en/guide/development](https://lessup.github.io/bookmarks-cleaner/en/guide/development) |
| **API Reference** | [/en/reference/llm-templates](https://lessup.github.io/bookmarks-cleaner/en/reference/llm-templates) |

## ⚙️ Configuration Example

```json
{
  "category_rules": {
    "Technology/AI": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["openai.com", "huggingface.co", "arxiv.org"],
          "weight": 15
        },
        {
          "match": "title",
          "keywords": ["GPT", "LLM", "neural network"],
          "weight": 10
        }
      ]
    }
  },
  "ai_settings": {
    "confidence_threshold": 0.7,
    "cache_size": 10000,
    "max_workers": 4
  },
  "llm": {
    "enable": false,
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

## 🔬 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Classification Accuracy | 91.4% |
| Processing Speed | ~50 bookmarks/second |
| Cache Hit Rate | 87-92% |
| Memory (baseline) | ~45MB |
| Memory (1000 bookmarks) | ~125MB |

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

This project follows **Spec-Driven Development (SDD)**. Before writing any code, please review the specification documents in the `/specs` directory. See [AGENTS.md](AGENTS.md) for the complete SDD workflow.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Inspired by the need for efficient personal knowledge management
- Built with [scikit-learn](https://scikit-learn.org/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [Rich](https://github.com/Textualize/rich)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
