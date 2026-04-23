# CleanBook — Smart Bookmark Cleaning & Classification

<p align="center">
  <a href="https://pypi.org/project/cleanbook/">
    <img src="https://img.shields.io/pypi/v/cleanbook.svg?color=blue&logo=pypi&logoColor=white" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/cleanbook/">
    <img src="https://img.shields.io/pypi/dm/cleanbook.svg?color=brightgreen" alt="PyPI Downloads">
  </a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white" alt="Python 3.10+">
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style: Black">
  </a>
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

**CleanBook** is an open-source, offline-first bookmark cleaning and classification tool. It transforms chaotic browser bookmark collections into well-organized, categorized libraries using a hybrid approach that prioritizes rules, enhances with machine learning, and optionally leverages LLM capabilities.

> Your bookmarks stay on your machine. No cloud uploads, no privacy concerns.

---

## 📖 Table of Contents

- [Why CleanBook?](#why-cleanbook)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Features](#-features)
- [Target Users](#-target-users)
- [Performance](#-performance)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)
- [Documentation](#-documentation)
- [Development](#-development)
- [Contributing](#-contributing)

---

## Why CleanBook?

| Problem | CleanBook Solution |
|---------|-------------------|
| 🔍 **Can't find bookmarks** in a messy collection of hundreds or thousands | Smart classification into categories you define, with 91.4% accuracy |
| ⏱️ **Manual organizing is tedious** and hard to maintain | Fully automated batch processing—point it at your export, get organized results |
| 🔒 **Privacy concerns** with cloud-based bookmark managers | 100% offline processing. Your data never leaves your device |
| ⚙️ **One-size-fits-all** tools don't match your workflow | Configuration-driven: customize categories, rules, and thresholds via JSON/YAML |

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, Windows

Verify your Python version:
```bash
python --version  # Should be >= 3.10
```

### Install

```bash
# Via pipx (recommended - isolated environment)
pipx install cleanbook

# Via pip
pip install cleanbook

# From source (development)
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner
pip install -r requirements.txt
pip install -e .
```

### Run

```bash
# Basic usage - process bookmarks
cleanbook -i bookmarks.html -o output/

# Interactive wizard mode
cleanbook-wizard

# Batch processing multiple files
cleanbook -i file1.html file2.html file3.html -o output/

# Custom confidence threshold (higher = more strict)
cleanbook -i bookmarks.html -o output/ --threshold 0.8

# Disable ML to save memory (rules only)
cleanbook -i bookmarks.html -o output/ --no-ml

# Debug mode with limited bookmarks
cleanbook -i bookmarks.html -o output/ --limit 100 --log-level DEBUG

# Health check - verify all components
cleanbook --health-check
```

### Example Output

```
✓ Loaded 1,247 bookmarks from bookmarks.html
✓ Removed 23 duplicates (1.8%)
✓ Classified 1,224 bookmarks (91.4% accuracy)
✓ Generated:
    output/bookmarks_clean.html    # Import to browser
    output/bookmarks_data.json     # Structured data
    output/report.md               # Classification report
✓ Done in 2.34s
```

---

## 🏗️ How It Works

```
                    ┌─────────────────────────────────────┐
  bookmarks.html ──▶│  1. Parse & Extract                 │
                    │     URLs, titles, metadata          │
                    └─────────────┬───────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │  2. Smart Deduplication             │
                    │     URL normalization, similarity   │
                    └─────────────┬───────────────────────┘
                                  ▼
┌───────────────────┬─────────────────────────────────────┬───────────────────┐
│                   │  3. Multi-Layer Classification      │                   │
│  High Priority    │     ┌─────────────────────────┐     │                   │
│  ═════════════    │     │ Rule Engine  (30%)      │◀────┤ Domain, keyword   │
│                   │     │ ML Classifier (25%)     │◀────┤ TF-IDF + Ensemble │
│  Automatic        │     │ Semantic (20%)          │◀────┤ Word vectors      │
│  Fallback ────────┼────▶│ User Profile (10%)      │     │                   │
│                   │     │ LLM (15%, optional)     │◀────┤ OpenAI-compatible │
│                   │     └───────────┬─────────────┘     │   (if configured) │
└───────────────────┴─────────────────┼───────────────────┴───────────────────┘
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  4. Weighted Voting Fusion          │
                    │     Combine results, confidence calc│
                    └─────────────┬───────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────┐
                    │  5. Multi-Format Export             │
                    │     HTML | JSON | Markdown          │
                    └─────────────────────────────────────┘
```

**Key Design**: Each layer provides confidence scores. If ML or LLM is unavailable, the system automatically redistributes weights to other layers—classification always completes.

---

## ✨ Features

<details open>
<summary><b>🚀 Offline-First Design</b></summary>

Complete pipeline runs locally without any cloud services. Rule engine responds in sub-milliseconds. Perfect for:
- Air-gapped environments
- Privacy-sensitive users
- Batch processing large collections

</details>

<details open>
<summary><b>🤖 Hybrid Classification (91.4% Accuracy)</b></summary>

Multi-layer approach with automatic fallback:
| Layer | Priority | Speed | Fallback |
|-------|----------|-------|----------|
| Rule Engine | High | 0.1ms | Never fails |
| ML Classifier | Medium | ~5ms | Rules |
| Semantic Analysis | Medium | ~3ms | Rules |
| LLM (optional) | Low | ~500ms | All above |

</details>

<details>
<summary><b>⚙️ Configuration-Driven</b></summary>

Customize everything via `config.json`—no code changes required:

```json
{
  "category_rules": {
    "Technology/AI": {
      "rules": [
        { "match": "domain", "keywords": ["openai.com", "huggingface.co"], "weight": 15 },
        { "match": "title", "keywords": ["GPT", "LLM", "neural network"], "weight": 10 }
      ]
    }
  }
}
```

</details>

<details>
<summary><b>📦 Multi-Format Export</b></summary>

| Format | Use Case | Browser Support |
|--------|----------|-----------------|
| HTML (Netscape) | Re-import to browser | Chrome, Firefox, Safari, Edge |
| JSON | Data analysis, further processing | Universal |
| Markdown | Knowledge base, documentation | Notion, Obsidian, GitHub |

</details>

<details>
<summary><b>🎯 Smart Deduplication</b></summary>

- URL normalization (HTTP → HTTPS, www removal, trailing slashes)
- Multi-dimensional similarity detection (SimHash, Levenshtein distance)
- Preserves the most complete metadata when merging duplicates

</details>

<details>
<summary><b>💾 Performance Optimized</b></summary>

- LRU caching for repeated operations
- Parallel processing with configurable workers
- Lazy initialization of ML components

</details>

---

## 🎯 Target Users

| User | Use Case | Recommended Setup |
|------|----------|-------------------|
| **Individual Users** | Personal bookmark maintenance | `pipx install cleanbook`, customize categories in config |
| **Team Maintainers** | Unified team bookmark standards | Share config.json + taxonomy YAML files, CI pipeline |
| **Developers** | Study bookmark processing pipelines | Fork repo, explore `/specs`, extend classifier plugins |

---

## 🔬 Performance

```
┌─────────────────────┬────────────┐
│ Metric              │ Value      │
├─────────────────────┼────────────┤
│ Classification Acc  │ 91.4%      │
│ Processing Speed    │ ~50+ /sec  │
│ Cache Hit Rate      │ 87-92%     │
│ Memory (baseline)   │ ~45MB      │
│ Memory (1K bookmarks│ ~125MB     │
└─────────────────────┴────────────┘
```

Benchmarked on: Intel i7-1165G7, Python 3.11, scikit-learn 1.4.2

---

## ❓ FAQ

<details>
<summary><b>Which browsers are supported?</b></summary>

CleanBook supports bookmarks exported from:
- **Chrome** / **Edge** / **Brave** / **Opera** (HTML format)
- **Firefox** (HTML format)
- **Safari** (File → Export → Bookmarks)

Just export your bookmarks to HTML and process with `cleanbook -i bookmarks.html`.
</details>

<details>
<summary><b>Do I need to download ML models separately?</b></summary>

**No.** All ML models are bundled with the package. The first run may take slightly longer as models load into memory, but no separate downloads are needed. The system works offline out of the box.
</details>

<details>
<summary><b>How do I use the LLM feature?</b></summary>

LLM is optional. To enable it:

1. Get an API key from OpenAI or compatible provider
2. Set environment variable: `export OPENAI_API_KEY="your-key"`
3. Enable in `config.json`: `"llm": { "enable": true, "model": "gpt-4o-mini" }`

If LLM is unavailable, the system automatically falls back to other classification layers.
</details>

<details>
<summary><b>What if I run out of memory with large bookmark collections?</b></summary>

Try these options:
- Use `--no-ml` flag to disable ML components (saves ~80MB)
- Reduce workers: `--workers 2` (default is 4)
- Process in batches: `--limit 500` to process 500 at a time
- Close other memory-intensive applications

With `--no-ml`, you can process 10,000+ bookmarks using under 100MB RAM.
</details>

<details>
<summary><b>The classification isn't accurate enough. How can I improve it?</b></summary>

1. **Customize rules** in `config.json` - add domain/title patterns for your specific interests
2. **Adjust threshold** - lower `--threshold` to catch more items, raise it for higher precision
3. **Enable LLM** - provides the best accuracy but requires API key
4. **Train on your data** - use `--train` flag with pre-tagged bookmarks

See [Best Practices](https://lessup.github.io/bookmarks-cleaner/en/guide/best-practices) for detailed tuning guide.
</details>

<details>
<summary><b>Does it support incremental processing?</b></summary>

**Partially.** The system caches feature embeddings to speed up re-processing. For true incremental updates (only processing new bookmarks), you can:
- Export only new bookmarks from your browser
- Process them separately and merge results

We plan to add full incremental mode in a future release.
</details>

<details>
<summary><b>Will my original bookmarks be modified?</b></summary>

**No.** CleanBook never modifies your input file. It creates new files in the output directory:
- `bookmarks_clean.html` - organized bookmarks to import back
- `bookmarks_data.json` - structured data for other uses
- `report.md` - classification report

Keep your original export as a backup.
</details>

<details>
<summary><b>Can I contribute custom classification rules?</b></summary>

Absolutely! Check the `config.json` structure and submit PRs with new rules. Popular categories we welcome:
- Emerging tech topics (AI frameworks, new languages)
- Regional domains (country-specific resources)
- Professional fields (medicine, law, finance)

See [Contributing Guide](CONTRIBUTING.md) for details.
</details>

---

## 🗺️ Roadmap

### Short-term (Next 3 months)
- [ ] Incremental processing mode (only new bookmarks)
- [ ] Browser extension for one-click export & import
- [ ] Additional export formats (Obsidian, Notion API)
- [ ] GUI desktop app (Electron/Tauri)

### Long-term Vision
- [ ] Self-hosted web UI
- [ ] Team/collaborative bookmark management
- [ ] Auto-tagging with custom taxonomy
- [ ] Bookmark archival (save page snapshots)

Have a feature request? [Open an issue](https://github.com/LessUp/bookmarks-cleaner/issues/new) or upvote existing ones!

---

## 📚 Documentation

| Resource | Link |
|----------|------|
| **Homepage** | [lessup.github.io/bookmarks-cleaner](https://lessup.github.io/bookmarks-cleaner/) |
| **Quick Start** | [/en/quickstart](https://lessup.github.io/bookmarks-cleaner/en/quickstart) |
| **Best Practices** | [/en/guide/best-practices](https://lessup.github.io/bookmarks-cleaner/en/guide/best-practices) |
| **Architecture** | [/en/design/architecture](https://lessup.github.io/bookmarks-cleaner/en/design/architecture) |
| **LLM Templates** | [/en/reference/llm-templates](https://lessup.github.io/bookmarks-cleaner/en/reference/llm-templates) |
| **Changelog** | [CHANGELOG.md](./CHANGELOG.md) |
| **Releases** | [GitHub Releases](https://github.com/LessUp/bookmarks-cleaner/releases) |

---

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/LessUp/bookmarks-cleaner.git
cd bookmarks-cleaner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

See [Development Guide](https://lessup.github.io/bookmarks-cleaner/en/guide/development) for details.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

This project follows **Spec-Driven Development (SDD)**. Before writing any code, review the specification documents in the `/specs` directory. See [AGENTS.md](AGENTS.md) for the complete AI agent workflow.

### Community

- 💬 [GitHub Discussions](https://github.com/LessUp/bookmarks-cleaner/discussions) - Ask questions, share ideas
- 🐛 [Issue Tracker](https://github.com/LessUp/bookmarks-cleaner/issues) - Report bugs, request features
- 📧 Contact: github@lessup.dev

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- Inspired by the need for efficient personal knowledge management
- Built with [scikit-learn](https://scikit-learn.org/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/), and [Rich](https://github.com/Textualize/rich)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/LessUp">LessUp</a>
</p>
