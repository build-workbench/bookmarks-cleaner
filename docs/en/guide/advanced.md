# Advanced Usage

<CbBadge text="Advanced Features" type="warning" />

This guide covers advanced features and workflows of CleanBook.

## Enable Machine Learning

CleanBook supports optional ML-enhanced classification. First use of `--train` downloads and trains the ML model, then it's used automatically:

```bash
cleanbook -i bookmarks.html --train
```

### ML Model Notes

- Model is automatically downloaded to local cache on first run
- Subsequent runs automatically load the trained model
- Delete cache and run `--train` again to retrain

### Disable ML

For pure rules mode (faster, more stable):

```bash
cleanbook -i bookmarks.html -o output/ --no-ml
```

## Interactive Wizard

CleanBook provides an interactive wizard for step-by-step guidance:

```bash
cleanbook --interactive
```

Or use the standalone command:

```bash
cleanbook-wizard
```

The wizard guides you through:

1. Selecting input files
2. Choosing output formats
3. Adjusting classification thresholds
4. Previewing results

## Batch Processing

### Process Multiple Files

```bash
# Specify multiple files
cleanbook -i file1.html file2.html -o output/

# Use glob patterns
cleanbook -i "bookmarks/*.html" -o output/
```

### Parallel Processing

```bash
# Specify number of worker processes
cleanbook -i bookmarks.html --workers 8
```

### Resource Control

Memory optimization when processing large bookmark collections:

```bash
# Limit parallel workers
cleanbook -i bookmarks.html --workers 1 --no-ml
```

## Feedback Pipeline

CleanBook provides an offline feedback pipeline for incrementally improving classification quality.

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

### Related Commands

| Command | Description |
|---------|-------------|
| `--export-review-queue` | Export low-confidence results as JSON |
| `--apply-feedback` | Apply feedback file to local pipeline |
| `--train-feedback` | Incremental training with feedback |
| `--audit-feedback` | Audit feedback data quality |

## Debugging & Tuning

### Debug Mode

```bash
# Enable debug logging
cleanbook -i bookmarks.html --log-level DEBUG

# Limit processing count (quick testing)
cleanbook -i bookmarks.html --limit 50
```

### Adjust Confidence

```bash
# Lower threshold for more classifications
cleanbook -i bookmarks.html --threshold 0.5

# Raise threshold for more precise classifications
cleanbook -i bookmarks.html --threshold 0.8
```

### Audit Feedback Data

```bash
cleanbook --audit-feedback feedback.json --audit-output audit.json
```

## Improve Classification Accuracy

1. **Custom Rules** - Customize `category_rules` for your domain
2. **Enable ML** - Use `--train` for ML-enhanced classification
3. **Adjust Threshold** - Tune `confidence_threshold` (default 0.7)
4. **Use Feedback Pipeline** - Improve through manual review

## Next Steps

- [CLI Reference](/en/reference/cli) — Complete command-line options
- [Configuration](/en/reference/config) — Deep customization of rules
- [Configuration Guide](/en/guide/configuration) — Understand the config file
