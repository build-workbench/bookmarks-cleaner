# Basic Usage Examples

Common usage scenarios for CleanBook.

## Scenario 1: First-time Cleaning

Clean bookmarks exported from your browser:

```bash
# Basic cleaning (recommended)
cleanbook -i ~/Downloads/bookmarks.html -o ~/clean-bookmarks/

# With ML (higher accuracy, slower first run)
cleanbook -i ~/Downloads/bookmarks.html -o ~/clean-bookmarks/ --train
```

## Scenario 2: Batch Processing

Process multiple bookmark files:

```bash
# Process multiple files
cleanbook -i work.html personal.html -o output/

# Process entire directory
cleanbook -i ./bookmark-backup/ -o output/
```

## Scenario 3: Custom Output

```bash
# Only HTML output
cleanbook -i bookmarks.html -o output/ --format html

# Only JSON (for data analysis)
cleanbook -i bookmarks.html -o output/ --format json

# All formats
cleanbook -i bookmarks.html -o output/ --format html,json,markdown
```

## Scenario 4: Adjust Classification Strictness

```bash
# Relaxed classification (more bookmarks get classified)
cleanbook -i bookmarks.html -o output/ --threshold 0.5

# Strict classification (only high confidence)
cleanbook -i bookmarks.html -o output/ --threshold 0.9
```

## Scenario 5: Resource Limits

```bash
# Single-thread processing (low memory)
cleanbook -i bookmarks.html -o output/ --workers 1

# Disable ML (faster but slightly less accurate)
cleanbook -i bookmarks.html -o output/ --no-ml
```

## Scenario 6: Interactive Wizard

Perfect for first-time users:

```bash
cleanbook-wizard
```

## Scenario 7: Automated Script

```bash
#!/bin/bash
# clean-bookmarks.sh

EXPORT_DIR="$HOME/bookmark-exports"
OUTPUT_DIR="$HOME/clean-bookmarks/$(date +%Y-%m-%d)"
LOG_FILE="$OUTPUT_DIR/clean.log"

mkdir -p "$OUTPUT_DIR"

for file in "$EXPORT_DIR"/*.html; do
    echo "Processing: $file"
    cleanbook -i "$file" -o "$OUTPUT_DIR" --train 2>&1 | tee -a "$LOG_FILE"
done

echo "Done! Results in: $OUTPUT_DIR"
```

Add to crontab for regular execution:

```cron
# Run every Sunday at 2 AM
0 2 * * 0 /home/user/clean-bookmarks.sh
```

## Next Steps

- [Custom Rules](./custom-rules) — Write your own classification rules
- [Team Setup](/en/examples/team) — Share configuration in teams
