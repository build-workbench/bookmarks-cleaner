# Concurrency

Bookmarks Cleaner uses **ThreadPoolExecutor** for concurrent processing, significantly improving batch processing speed.

## Concurrency Model

```mermaid
flowchart TB
    subgraph Input["Input Queue"]
        B1[Bookmark 1]
        B2[Bookmark 2]
        B3[Bookmark 3]
        BN[Bookmark N]
    end
    
    subgraph ThreadPool["Thread Pool (4 workers)"]
        W1[Worker 1]
        W2[Worker 2]
        W3[Worker 3]
        W4[Worker 4]
    end
    
    subgraph Output["Output Queue"]
        R1[Result 1]
        R2[Result 2]
        R3[Result 3]
        RN[Result N]
    end
    
    B1 --> W1 --> R1
    B2 --> W2 --> R2
    B3 --> W3 --> R3
    BN --> W4 --> RN
```

## Performance Benchmarks

| Threads | Speed (bookmarks/sec) | CPU Usage | Memory Increase |
|---------|----------------------|-----------|-----------------|
| 1 | 120 | 25% | baseline |
| 2 | 230 | 45% | +5% |
| 4 | 420 | 80% | +10% |
| 8 | 650 | 95% | +20% |
| 16 | 720 | 99% | +35% |

**Conclusion**: 4-8 threads offer the best price-performance ratio.

## Configuration

```json
{
  "concurrency": {
    "max_workers": 4,
    "batch_size": 100,
    "task_timeout": 30,
    "retry_count": 3
  }
}
```

## Related Docs

- [Caching](/en/performance/caching) - Cache optimization
- [Optimization](/en/performance/optimization) - Performance tuning
