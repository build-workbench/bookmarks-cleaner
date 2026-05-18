# Technical Whitepaper

> **Bookmarks Cleaner** is documented here as a local-first systems artifact, not a feature page: the focus is on architecture boundaries, classifier cooperation, and the evidence chain behind these choices.

## Abstract

Bookmarks Cleaner is an offline-first CLI for bookmark cleaning, deduplication, classification, and export. Its core thesis is not "pile on AI as much as possible", but "keep the main path rules-driven and interpretable, then apply probabilistic intelligence only to the difficult samples that justify the cost." Therefore, the system baseline is always deterministic rule-based classification; ML, semantic analysis, and optional LLM cooperation are enhancement layers, not replacements for the entire runtime.

## System Thesis

The project rests on three claims:

1. **For personal bookmark archives, offline-first beats hosted convenience.** The input data contains research trajectories, project traces, and browsing intent — treating it as a cloud workload by default makes little sense.
2. **Rules should own the main path.** Deterministic matching on known domains and patterns is still the fastest, cheapest, and most interpretable decision mechanism.
3. **Fusion is a coordination problem, not a labeling problem.** What matters is not "having multiple classifiers" but how to combine their confidence scores, priorities, and optionality into an operable final result.<CiteReference id="1" authors="Kuncheva, L. I." title="Combining Pattern Classifiers: Methods and Algorithms" venue="Wiley-Interscience" year="2004" />

## Runtime Boundary

The maintained system boundary is deliberately narrow:

| Surface | In scope | Engineering significance |
|---------|----------|--------------------------|
| Input | Browser bookmark export files, primarily local HTML | Tool starts from files the user already controls |
| Processing | Deduplication, classification, organization, export | All value created inside the local runtime |
| Output | Cleaned bookmark HTML, JSON data, Markdown reports | Outputs must be portable and auditable |
| Optional integrations | ML models, semantic analysis, local/remote LLM providers | Intelligence layers are additive, not prerequisites |
| Out of scope | Hosted account sync, central database, telemetry pipelines | These expand the ops surface and privacy boundary |

This boundary explains most of the design decisions that follow. The project can support stronger intelligence layers, but it cannot reshape a personal bookmark archive into a service-oriented problem.

## Architecture Model

The runtime is organized into a set of explicitly named layers:

1. **Entry surface**: CLI and thin Python entry points.
2. **Facade and composition root**: `BookmarkProcessor` and the container that assembles dependencies.
3. **Orchestration layer**: The runtime control layer that schedules processing stages.
4. **Pipeline layer**: Load, deduplicate, classify, organize, export.
5. **Intelligence layer**: Rule engine, ML classifier, semantic analyzer, optional LLM, and final fusion layer.

The value of this structure lies in separating "the parts that change frequently" from "the parts that should stay stable." The CLI contract can converge while classifier implementations keep evolving; the facade can stay thin while the orchestration layer absorbs complexity; the Pipeline can swap stage internals without forcing all contributors to re-learn the whole system.

<ArchitectureMatrix />

## Fusion and Confidence

The final classification step uses weighted voting, not a retrained stacked meta-model. This choice is pragmatic:

- The engines participating in fusion are heterogeneous. Rule results are discrete and high-authority; ML, semantic, and LLM outputs are probabilistic or confidence-shaped.
- Introducing a second learning layer would require additional training data and weaken the answer to "why did this bookmark land in this directory."<CiteReference id="2" authors="Wolpert, D. H." title="Stacked Generalization" venue="Neural Networks" year="1992" url="https://doi.org/10.1016/S0893-6080(05)80023-1" />
- Weighted voting lets the system preserve a strong rules-first stance while absorbing supplementary signals from other classifiers.

Confidence calibration matters because raw scores from different classifiers are not directly comparable. The project therefore treats "confidence" as an engineering interface, not a decorative number.<CiteReference id="3" authors="Zadrozny, B.; Elkan, C." title="Obtaining Calibrated Probability Estimates from Decision Trees and Naive Bayesian Classifiers" venue="ICML" year="2001" />

### Fusion Decision Formula

The fusion layer computes the following score for each candidate category $c \in C$:

$$
S(c) = \sum_{i=1}^{n} w_i \cdot \mathbb{1}_{[y_i = c]} \cdot \text{conf}_i, \quad \forall c \in C
$$

Final prediction:

$$
\hat{c} = \arg\max_{c \in C} S(c)
$$

The rule engine holds the highest prior weight ($w_{\text{rule}} = 0.50$) because its accuracy boundary is deterministic. ML, semantic, and LLM classifier weights decrease in order, reflecting the trade-off between cost and uncertainty.

## Performance Methodology

The performance numbers on this site should be read as a **measurement envelope**, not an absolute guarantee for all machine environments.

<PerformanceChart />

### Observation Dimensions

| Dimension | Engineering significance |
|-----------|--------------------------|
| Cold start | Cost of entering the runtime before heavy dependencies are loaded |
| Throughput | Bookmark processing speed once the pipeline reaches steady state |
| Mode selection | Cost difference between rules-only, ML hybrid, and optional LLM paths |
| Memory footprint | Determines the processable ceiling for large local bookmark archives |
| Concurrency | How much thread-level parallelism actually benefits the current workload |

### Interpretation

- **Rules-only path** represents the lowest-latency, highest-certainty execution path.
- **Hybrid path** trades more CPU and model initialization cost for recovery on weak and ambiguous samples.
- **LLM-assisted path** should be understood as a selective upgrade, not a default execution mode.

The key insight is that performance is not an isolated trick but a consequence of system boundaries: local execution, deferred initialization, and a rules-dominant common path.

## System Complexity Analysis

### Time Complexity

For a bookmark corpus of size $N$:

| Stage | Time complexity | Notes |
|-------|----------------|-------|
| Load | $O(N)$ | Linear parsing |
| Deduplicate | $O(N \log N)$ | Sort-based hashing |
| Rule classification | $O(N \cdot R)$ | $R$ = rule count, $R \ll N$ in practice |
| ML classification | $O(N \cdot d)$ | $d$ = feature dimension (TF-IDF ≈ 5,000) |
| Fusion | $O(N \cdot K)$ | $K$ = classifier count, $K \leq 5$ |
| Organize | $O(N \log N)$ | Sorted tree construction |
| Export | $O(N)$ | Linear serialization |

Overall time complexity is $O(N \log N + N \cdot d)$, degrading to $O(N \log N)$ in the rules-only path.

### Space Complexity

| Component | Memory estimate |
|-----------|----------------|
| Bookmark object (each) | ~1–2 KB |
| TF-IDF matrix (5,000 bookmarks) | ~50–200 MB (sparse) |
| Sentence Transformer model | ~80–400 MB (by model variant) |
| LLM context window | Per-call, not resident memory |

Rules mode (no ML) on 100K bookmarks has a resident memory footprint of roughly 200–400 MB.

## Security Boundary

### Privacy Model

CleanBook's privacy claims are architectural, not policy-based:

- **No data exfiltration path**: All processing happens on the user's machine unless the user explicitly configures a remote LLM endpoint.
- **No telemetry code**: There is no telemetry or usage statistics collection anywhere in the project.
- **Input format boundary**: The tool accepts local file paths only, not URL lists or web crawling tasks.

### Input Validation

The load stage performs strict format boundary checks on bookmark export files:

```python
# Pseudocode: defensive boundary in load stage
def load(path: str) -> list[Bookmark]:
    if not path.endswith(('.html', '.json')):
        raise UnsupportedFormatError(path)
    content = Path(path).read_text(encoding='utf-8', errors='replace')
    return parse_bookmarks(content)  # HTML parser with tag allowlist
```

The parse layer uses an HTML tag allowlist and does not execute scripts or render external resources.

## Scalability Design Considerations

### Vertical Scaling (single machine)

The vertical scaling ceiling for the current architecture is constrained by:

1. **GIL limitation**: Python's GIL makes it hard for CPU-intensive ML inference to fully utilize multiple cores. `ThreadPoolExecutor` is still effective when there is significant I/O waiting, but yields limited gains for pure CPU tasks.
2. **Memory pressure**: TF-IDF matrices for large bookmark archives (>100K entries) may exceed available memory.

Potential scaling paths:
- Use `multiprocessing.Pool` instead of `ThreadPoolExecutor` for the ML inference segment
- Introduce chunk-wise loading mode to reduce peak memory

### Plugin Extension Points

Each Pipeline stage implements a `Protocol` interface, allowing users to inject custom classifiers:

```python
from bookmarks_cleaner.protocols import ClassifierProtocol

class MyClassifier:
    def classify(self, bookmark: Bookmark) -> ClassificationResult:
        ...  # Custom classification logic
```

## Failure Modes and Fallback Strategy

The system is designed to "degrade gracefully" rather than "fail completely on any error":

| Failure mode | Expected behavior |
|-------------|-------------------|
| Malformed bookmark export file | Fail early at load stage; don't propagate errors downstream |
| No rule match | Bookmark flows to probabilistic classifiers, not directly to empty result |
| ML or semantic dependency unavailable | System degrades to narrower rules-only path |
| LLM integration unavailable or disabled | Main classification flow stays intact (LLM is an optional layer) |
| Low or conflicting confidence scores | Fusion layer exposes lower-certainty results, not fabricated certainty |
| Out of memory | Load stage fails early, prompting user to reduce input size |

## Reference Chain

- [Pipeline Architecture](/en/architecture/pipeline) explains the stage-level runtime.
- [Performance Methodology](/en/performance/optimization) explains how to read the numbers on this site.
- [References](/en/resources/references) collects the literature behind fusion, calibration, and architecture design.
- [Related Projects](/en/resources/related-projects) compares against neighboring tools and capability stacks.
- [Evolution Notes](/en/evolution) explains how the current structure evolved from earlier code patterns.
