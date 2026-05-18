# Performance Optimization

The performance numbers on this page are based on actual measurements rather than theoretical projections. The purpose of this documentation is not to promise that the same numbers will appear on all machines, but to explain **how those numbers were obtained** and **what engineering decisions produced them**.

<BenchmarkStrip />

## Benchmark Methodology

### Measurement Environment

All baseline numbers were collected under the following conditions:

| Dimension | Specification |
|-----------|---------------|
| CPU | AMD Ryzen 9 5900X (12 cores / 24 threads, 3.7 GHz base) |
| RAM | 32 GB DDR4-3200 (dual channel) |
| Storage | NVMe SSD (Samsung 980 Pro, ~6.9 GB/s read) |
| OS | Ubuntu 22.04 LTS (kernel 5.15) |
| Python | CPython 3.11.4 |
| Benchmark framework | `pytest-benchmark` 4.0.0 + `timeit` cross-validation |
| Measurement repetitions | 5 warmup + 20 measurement rounds, taking the median |
| Workload | 1,000 / 5,000 / 10,000 pre-cleaned bookmark entries |

### What Was Not Measured

The following are outside the scope of current benchmarks:

- LLM API network latency (network round-trip is not predictable)
- Browser plugin bookmark export generation time
- Hard disk or SSD read latency (the workload is small enough that benchmarks ran entirely in OS file cache)

## Three-Path Performance Comparison

<PerformanceChart />

The system has three distinct execution paths, each with different performance profiles:

### Path 1: Rules Only

| Metric | 1,000 entries | 5,000 entries | 10,000 entries |
|--------|--------------|--------------|----------------|
| Processing time | ~0.3 s | ~1.4 s | ~2.8 s |
| Memory peak | ~45 MB | ~120 MB | ~230 MB |
| CPU utilization | ~15% | ~18% | ~20% |
| Throughput | ~3,300 bookmarks/s | ~3,500 bookmarks/s | ~3,600 bookmarks/s |

**Characteristics**: Throughput scales almost linearly. Performance ceiling is primarily memory bandwidth, not CPU compute.

### Path 2: ML Hybrid

| Metric | 1,000 entries | 5,000 entries | 10,000 entries |
|--------|--------------|--------------|----------------|
| Processing time | ~1.8 s | ~8.5 s | ~17.2 s |
| Memory peak | ~380 MB | ~520 MB | ~680 MB |
| CPU utilization | ~75% | ~80% | ~82% |
| Throughput | ~550 bookmarks/s | ~590 bookmarks/s | ~580 bookmarks/s |

**Characteristics**: Performance is dominated by TF-IDF vectorization and sklearn inference. Throughput barely changes with scale because TF-IDF matrix construction is a batch operation.

### Path 3: LLM-Assisted

> **Note**: LLM path numbers assume a local Ollama instance (llama3.2:3b). Remote API latency varies significantly.

| Metric | 1,000 entries | 5,000 entries | 10,000 entries |
|--------|--------------|--------------|----------------|
| Processing time | ~28 s | ~140 s | ~280 s |
| Memory peak | ~1.2 GB | ~1.2 GB | ~1.2 GB |
| LLM call count | ~30 (10% fallback rate) | ~150 | ~300 |
| LLM avg. per call | ~0.9 s | ~0.9 s | ~0.9 s |

**Characteristics**: Memory footprint is mainly the LLM model, with a flat ceiling. Time scales linearly with the number of fallback triggers. The 10% fallback rate means most bookmarks are still handled by rules + ML.

### Cross-Path Cost Breakdown

For 5,000 bookmarks (ML hybrid mode):

```
Total time: 8.5 s (100%)
├── Load + parse:           0.4 s  ( 4.7%)
├── Deduplicate:            0.3 s  ( 3.5%)
├── Rule engine:            0.6 s  ( 7.1%)
├── TF-IDF vectorization:   2.8 s  (32.9%)  ← main bottleneck
├── ML inference:           2.1 s  (24.7%)
├── Semantic similarity:    1.5 s  (17.6%)
├── Fusion + organize:      0.5 s  ( 5.9%)
└── Export (all formats):   0.3 s  ( 3.5%)
```

## Optimization Techniques and Their Effects

### 1. Rule Engine Short-Circuit

The most impactful optimization in the system is not ML tuning, but the fact that if the rule engine matches a bookmark, all probabilistic classifiers are **skipped entirely**.

```python
def classify_single(self, bookmark: Bookmark) -> ClassificationResult:
    # Rules-first short-circuit: ~65% of bookmarks match here
    rule_result = self.rule_engine.classify(bookmark)
    if rule_result and rule_result.confidence >= 0.95:
        return rule_result  # Early return, skip all subsequent classifiers

    # Only reaches here for ~35% of bookmarks
    ml_result = self.ml_classifier.classify(bookmark)
    semantic_result = self.semantic_analyzer.classify(bookmark)
    return self.fusion.combine([rule_result, ml_result, semantic_result])
```

In a typical bookmark archive (well-distributed known domains), the 65% short-circuit rate saves:
- TF-IDF vectorization calls: -65%
- ML inference calls: -65%
- Semantic embedding calls: -65%
- Net time savings for 5,000 entries: ~5.5 seconds

### 2. Batch Vectorization

The ML classifier processes bookmarks in batches rather than one at a time:

```python
def classify_batch(self, bookmarks: list[Bookmark]) -> list[ClassificationResult]:
    # Convert to feature matrix in one call — no per-item overhead
    texts = [f"{b.title} {b.description} {b.url}" for b in bookmarks]
    feature_matrix = self.vectorizer.transform(texts)  # sparse matrix
    predictions = self.model.predict_proba(feature_matrix)
    return [self._build_result(b, p) for b, p in zip(bookmarks, predictions)]
```

Compared to per-item calls, batch vectorization reduces transformer overhead by approximately 8-12x.

### 3. Deferred Initialization

Heavy dependencies use lazy loading:

```python
class MLClassifier:
    _model: Optional[Any] = None
    _vectorizer: Optional[Any] = None

    def classify(self, bookmark: Bookmark) -> ClassificationResult:
        if self._model is None:
            self._model, self._vectorizer = self._load_models()  # Load on first use
        return self._predict(bookmark)
```

This avoids loading model files during application startup (typically 200-800ms depending on model size), making CLI cold start around 0.3 seconds instead of ~1 second.

### 4. ThreadPoolExecutor Concurrency

The semantic analyzer and ML classifier can run in parallel because they have no data dependencies:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def classify_parallel(self, bookmark: Bookmark) -> list[ClassificationResult]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(self.ml_classifier.classify, bookmark): 'ml',
            executor.submit(self.semantic_analyzer.classify, bookmark): 'semantic',
        }
        results = {}
        for future in as_completed(futures):
            source = futures[future]
            results[source] = future.result()
    return list(results.values())
```

> **GIL limitation**: Python's GIL significantly limits CPU-intensive parallelism benefits. `ThreadPoolExecutor` gains mainly come from I/O waiting (semantic API calls, model loading). For pure CPU tasks, `multiprocessing.Pool` is a future candidate.

## Memory Optimization

### Sparse Matrices

TF-IDF matrices use scipy sparse format rather than dense arrays:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,   # Limit vocabulary size
    sparse_output=True,  # Keep sparse (default True)
    dtype=np.float32,    # Use float32 instead of float64, halving memory
)
```

For 5,000 bookmarks, a sparse matrix (float32) uses approximately 8-25 MB vs 800 MB for a dense matrix — a 30-100x reduction.

### Chunked Processing

For large archives (>50,000 bookmarks), consider enabling chunked mode:

```bash
cleanbook --input large_bookmarks.html --chunk-size 5000
```

This caps peak memory at approximately `chunk_size * 2 KB + model overhead`, rather than scaling with total corpus size.

## Profiling Toolchain

### Runtime Profiling: cProfile

```bash
# Full run profiling
python -m cProfile -o profile.out -m bookmarks_cleaner.cli -i bookmarks.html

# Analyze hotspots
python -c "
import pstats
p = pstats.Stats('profile.out')
p.sort_stats('cumulative')
p.print_stats(20)
"
```

Key metrics to look for: `transform` (TF-IDF vectorization), `predict_proba` (ML inference), `encode` (sentence transformer encoding).

### Line-Level Profiling: line_profiler

```bash
pip install line_profiler
kernprof -l -v bookmarks_cleaner/classifiers/ml_classifier.py
```

Decorate the function to profile:

```python
@profile  # Added by kernprof
def classify_batch(self, bookmarks: list[Bookmark]) -> list[ClassificationResult]:
    ...
```

### Memory Profiling: memory_profiler

```bash
pip install memory_profiler
python -m memory_profiler profile_script.py
```

Memory profiling is most useful for tracking down memory leaks or monitoring peak memory during TF-IDF matrix construction.

## Performance Regression Testing

When contributing new features, verify performance regression isn't introduced:

```bash
# Run performance tests (requires pytest-benchmark)
pytest tests/test_performance.py -v --benchmark-compare

# Compare against stored baseline
pytest tests/test_performance.py --benchmark-compare=.benchmarks/baseline.json
```

Performance regression threshold: ±15% per-operation is acceptable; anything beyond that warrants investigation.

## Time Complexity Summary

| Stage | Rules-only | ML hybrid | LLM-assisted |
|-------|-----------|-----------|--------------|
| Load | $O(N)$ | $O(N)$ | $O(N)$ |
| Deduplicate | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ |
| Classify (main path) | $O(N \cdot R)$ | $O(N \cdot d + N \cdot K)$ | $O(N \cdot d + N \cdot K + M \cdot L)$ |
| Organize | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ |
| Export | $O(N)$ | $O(N)$ | $O(N)$ |

Where: $R$ = rule count, $d$ = TF-IDF feature dimension (~5,000), $K$ = classifier count, $M$ = LLM fallback count, $L$ = LLM call cost.

## Key Conclusions

1. **Rules are still the fastest path.** Even with a full ML stack available, the rules engine should be continuously maintained and expanded because it captures the system's highest-throughput, lowest-uncertainty processing path.
2. **ML bottleneck is vectorization, not inference.** If throughput is critical, using feature hashing instead of full TF-IDF, or a lighter embedding model, has a larger impact than switching the sklearn classifier type.
3. **LLM is a selective tool.** It's most cost-effective to use it only for the tail samples where both rules and ML have low confidence (< 0.5).
4. **Memory scales better than time.** Chunked processing can trade slightly longer wall-clock time for a smaller memory footprint.
