# Best Practices

Best practices for bookmark management and classification.

## Classification Strategy

### 1. From Wide to Strict

When starting out:
- Lower confidence threshold (0.5-0.6) for more classifications
- Adjust rules based on results to improve coverage
- Increase to standard threshold (0.7) when stable

### 2. Keep It Simple

- 8-12 main categories recommended
- Avoid overly granular subcategories
- Regularly merge similar categories

### 3. Naming Convention

- Use concise names
- Add emoji for visual recognition
- Consistent naming style

## Maintenance

### Regular Cleaning

```bash
# Add to crontab
0 2 * * 0 cleanbook -i ~/bookmarks.html -o ~/bookmarks-clean/ --train
```

### Version Backup

```bash
# Backup before cleaning
cp bookmarks.html bookmarks-$(date +%Y%m%d).html
```

## Performance Optimization

1. **First use**: Run with `--train` to build ML model
2. **Large batches**: Increase `--workers` count
3. **Memory constrained**: Use `--no-ml` and `--workers 1`
