# Related Projects

This document lists open source projects related to Bookmarks Cleaner for reference and comparison.

## Bookmark Management Tools

### linkding

> **GitHub**: [sissbruecker/linkding](https://github.com/sissbruecker/linkding)
> **Stars**: 6k+ | **License**: MIT

**Features**:
- Self-hosted bookmark management service
- Tag and category support
- REST API
- Browser extension

**Comparison**:
| Feature | linkding | Bookmarks Cleaner |
|---------|----------|-------------------|
| Deployment | Server | CLI Tool |
| Data storage | Database | Local files |
| Offline | Needs deployment | ✅ Fully offline |
| ML Classification | ❌ | ✅ |

### Shaarli

> **GitHub**: [shaarli/Shaarli](https://github.com/shaarli/Shaarli)
> **Stars**: 3k+ | **License**: Zlib

**Features**:
- Personal bookmark manager
- PHP, lightweight
- Plugin extension support

## Text Classification Tools

### FastText

> **GitHub**: [facebookresearch/fastText](https://github.com/facebookresearch/fastText)
> **Stars**: 26k+ | **License**: MIT

**Application**: Bookmarks Cleaner's ML classifier references FastText's text processing methods.

### scikit-learn

> **GitHub**: [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)
> **Stars**: 60k+ | **License**: BSD

**Application**: Bookmarks Cleaner uses scikit-learn for ML classifier implementation.

## Semantic Analysis Tools

### Sentence Transformers

> **GitHub**: [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)
> **Stars**: 15k+ | **License**: Apache 2.0

**Application**: Used for semantic analyzer implementation.

## LLM Tools

### Ollama

> **GitHub**: [ollama/ollama](https://github.com/ollama/ollama)
> **Stars**: 80k+ | **License**: MIT

**Application**: Bookmarks Cleaner supports local LLM via Ollama.

## Comparison Summary

| Project | Type | Offline | ML | LLM | CLI |
|---------|------|---------|----|----|-----|
| Bookmarks Cleaner | CLI Tool | ✅ | ✅ | ✅ | ✅ |
| linkding | Web Service | ❌ | ❌ | ❌ | ❌ |
| Shaarli | Web Service | ❌ | ❌ | ❌ | ❌ |

## Contribute

If you find other related projects, welcome to submit PR to update this list.
