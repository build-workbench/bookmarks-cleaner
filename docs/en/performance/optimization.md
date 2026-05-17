# Optimization Tips

This document summarizes performance optimization tips for Bookmarks Cleaner.

## Quick Optimization Checklist

| Item | Expected Improvement | Difficulty |
|------|---------------------|------------|
| Increase worker threads | 2-4x | Low |
| Enable caching | 20-50% | Low |
| Disable ML/LLM | 10x+ | Low |
| Batch processing | 30% | Low |

## Concurrency Optimization

```bash
# Adjust based on CPU cores
cleanbook -i bookmarks.html --workers 8
```

**Recommended values**:
- 2 cores: 2-4 threads
- 4 cores: 4-8 threads
- 8+ cores: 8-16 threads

## Speed Comparison

| Configuration | 1000 Bookmarks Time |
|--------------|---------------------|
| Full features | 45s |
| No ML | 8s |
| Rules only | 2s |

## Best Practice Configuration

```json
{
  "max_workers": 4,
  "ai_settings": {
    "use_ml": true,
    "use_llm": false
  },
  "cache": {
    "enabled": true
  }
}
```

## Related Docs

- [Concurrency](/en/performance/concurrency) - Concurrency model
- [Caching](/en/performance/caching) - Cache system
