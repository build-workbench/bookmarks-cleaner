# Quick Start

<CbBadge text="5 minutes" type="tip" />

This guide will get you up and running with CleanBook in 5 minutes.

## Installation

::: tip Recommended
Using [pipx](https://pipx.pypa.io/) ensures CleanBook runs in an isolated virtual environment without conflicts with other Python packages.
:::

::: code-group

```bash [pipx recommended]
# Install pipx (if not already installed)
pip install pipx
pipx ensurepath

# Install CleanBook
pipx install cleanbook
```

```bash [pip]
pip install cleanbook
```

```bash [uv]
uv tool install cleanbook
```

:::

Verify installation:

```bash
cleanbook --version
# cleanbook, version 2.0.0
```

## Export Your Bookmarks

### Chrome / Edge
1. Open Bookmark Manager: `chrome://bookmarks` or `edge://favorites`
2. Click menu (⋮) → "Export bookmarks"
3. Save as `bookmarks.html`

### Firefox
1. Open Library: `Ctrl+Shift+O`
2. Click "Import and Backup" → "Export Bookmarks to HTML"
3. Save as `bookmarks.html`

### Safari
1. File → Export → Bookmarks
2. Save as `bookmarks.html`

## Run Cleaning

Basic usage:

```bash
cleanbook -i bookmarks.html -o output/
```

Output files:

```
output/
├── bookmarks_clean.html    # Cleaned bookmarks (import to browser)
├── bookmarks_data.json     # Structured data for analysis
├── bookmarks_summary.md    # Classification report
└── taxonomy_summary.yaml   # Taxonomy summary
```

## Check Results

### Import to Browser

Open `output/bookmarks_clean.html`, then import using your browser's import function:

**Chrome**: Bookmarks → Import bookmarks and settings → Bookmarks HTML file

**Firefox**: Bookmarks → Manage Bookmarks → Import and Backup → Import Bookmarks from HTML

### View Report

```bash
cat output/bookmarks_summary.md
```

Example output:

```markdown
# CleanBook Processing Report

## Statistics
- Total bookmarks: 1,247
- Duplicates removed: 23
- Classified: 1,224 (91.4%)
- Unclassified: 0

## Category Distribution
| Category | Count | Percentage |
|----------|-------|------------|
| 💻 Programming | 456 | 37.3% |
| 🤖 AI/ML | 189 | 15.4% |
| 📚 Documentation | 234 | 19.1% |
| 🛠️ Tools | 167 | 13.7% |
| 📰 News | 178 | 14.5% |
```

## Advanced Usage

### Enable Machine Learning

First use of `--train` downloads and trains the ML model, then it's used automatically:

```bash
cleanbook -i bookmarks.html --train
```

### Interactive Wizard

```bash
cleanbook-wizard
```

The wizard guides you through:
1. Selecting input files
2. Choosing output formats
3. Adjusting classification thresholds
4. Previewing results

### Batch Processing

```bash
# Process multiple files
cleanbook -i file1.html file2.html -o output/

# Specify worker processes
cleanbook -i bookmarks.html --workers 8
```

## Configuration Basics

CleanBook's main configuration file is `config.json`:

```bash
# Generate default config
cleanbook --init-config

# Edit configuration
nano config.json
```

Key settings:

```json
{
  "ai_settings": {
    "confidence_threshold": 0.7,    // Classification confidence threshold
    "use_semantic_analysis": true,  // Enable semantic analysis
    "max_workers": 4                // Parallel processing count
  },
  "category_rules": {
    "Tech/Python": {
      "rules": [
        { "match": "domain", "keywords": ["python.org", "pypi.org"], "weight": 15 },
        { "match": "title", "keywords": ["django", "flask", "fastapi"], "weight": 10 }
      ]
    }
  }
}
```

See [Configuration Guide](./guide/configuration) for more options.

## FAQ

**Q: Out of memory when processing large bookmark files?**

```bash
# Limit parallel workers
cleanbook -i bookmarks.html --workers 1 --no-ml
```

**Q: How to improve classification accuracy?**

1. Customize `category_rules` for your domain
2. Enable ML (`--train`)
3. Adjust `confidence_threshold` (default 0.7, lower for more classifications)

**Q: What output formats are supported?**

```bash
cleanbook -i bookmarks.html -o output/ --format html,json,markdown
```

## Next Steps

- [Installation Guide](/en/guide/installation) — Detailed installation options
- [Configuration](/en/reference/config) — Deep customization of rules
- [Best Practices](./guide/best-practices) — Bookmark management methodology
