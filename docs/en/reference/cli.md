# CLI Reference

<CbBadge text="Command Line" type="info" />

CleanBook's command-line tool `cleanbook` provides a complete bookmark processing pipeline.

## Basic Usage

```bash
cleanbook -i bookmarks.html -o output/
```

## Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-V, --version` | flag | — | Show version and exit |
| `-i, --input` | file[] | — | Input HTML bookmark files; supports multiple files and glob patterns |
| `-o, --output` | dir | `output` | Output directory |
| `-c, --config` | file | built-in | Config file path; uses built-in config by default |
| `--workers` | int | 4 | Number of parallel workers |
| `--threshold` | float | 0.7 | Classification confidence threshold |
| `--no-ml` | flag | — | Disable machine learning features |
| `--log-level` | enum | `INFO` | Log level: `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--limit` | int | 0 | Limit number of bookmarks to process (for debugging, 0 = unlimited) |

## Processing Modes

### Standard Processing

Basic processing mode using rule engine:

```bash
cleanbook -i bookmarks.html -o output/
```

### Interactive Mode

Launch interactive wizard for guided operation:

```bash
cleanbook --interactive
```

### ML Training Mode

Downloads and trains ML model on first use; subsequent runs use it automatically:

```bash
cleanbook -i bookmarks.html --train
```

### Health Check

Verify system dependencies and configuration:

```bash
cleanbook --health-check
```

## Feedback Pipeline

CleanBook provides an offline feedback pipeline for incremental quality improvement.

### Export for Review

Export low-confidence results as review queue JSON:

```bash
cleanbook -i bookmarks.html -o output/ --export-review-queue review.json
```

### Apply Feedback

Import offline feedback JSON and apply to local feedback pipeline:

```bash
cleanbook --apply-feedback feedback.json
```

### Train with Feedback

Trigger incremental training using offline feedback JSON:

```bash
cleanbook --train-feedback feedback.json
```

### Audit Feedback

Audit feedback JSON data quality:

```bash
cleanbook --audit-feedback feedback.json --audit-output audit.json
```

| Option | Description |
|--------|-------------|
| `--export-review-queue` | Export low-confidence results as JSON |
| `--apply-feedback` | Apply feedback file |
| `--train-feedback` | Incremental training with feedback data |
| `--audit-feedback` | Audit feedback data quality |
| `--audit-output` | Audit result output path |

## Common Command Examples

### Basic Processing

```bash
# Simplest usage
cleanbook -i bookmarks.html -o output/

# Use custom config
cleanbook -i bookmarks.html -o output/ -c ./config.json

# Disable ML, rule-only mode
cleanbook -i bookmarks.html -o output/ --no-ml
```

### Batch Processing

```bash
# Process multiple files
cleanbook -i file1.html file2.html -o output/

# Use glob patterns
cleanbook -i "bookmarks/*.html" -o output/

# Specify parallel workers
cleanbook -i bookmarks.html --workers 8
```

### Debugging & Tuning

```bash
# Limit processing count (quick test)
cleanbook -i bookmarks.html --limit 50

# Enable debug logging
cleanbook -i bookmarks.html --log-level DEBUG

# Adjust confidence threshold
cleanbook -i bookmarks.html --threshold 0.5
```

### Complete Workflow

```bash
# 1. Health check
cleanbook --health-check

# 2. First processing + training
cleanbook -i bookmarks.html -o output/ --train

# 3. Export low-confidence results for manual review
cleanbook -i bookmarks.html -o output/ --export-review-queue review.json

# 4. Apply feedback after manual review
cleanbook --apply-feedback reviewed.json

# 5. Incremental training with feedback
cleanbook --train-feedback reviewed.json
```

## Output Files

After processing, the output directory contains:

| File | Description |
|------|-------------|
| `bookmarks_clean.html` | Cleaned bookmarks (can be imported to browser) |
| `bookmarks_data.json` | Structured data (for further analysis) |
| `bookmarks_summary.md` | Classification report |
| `taxonomy_summary.yaml` | Taxonomy summary |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Interrupted or execution failed |
| 2 | Configuration or resource error |
| 3 | Missing dependencies |

## Next Steps

- [Installation Guide](/en/guide/installation) — Detailed installation options
- [Configuration Reference](/en/reference/config) — Deep customization
- [Advanced Usage](/en/guide/advanced) — ML, batch processing, and feedback pipeline
