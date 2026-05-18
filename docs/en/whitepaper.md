# Technical Whitepaper

> **Bookmarks Cleaner** is presented here as a local-first systems artifact: a bookmark cleanup CLI whose value comes from architecture shape, classifier cooperation, and evidence-backed trade-offs.

## Abstract

Bookmarks Cleaner is an offline-first CLI for bookmark cleanup, deduplication, classification, and export. Its design thesis is not "add as much AI as possible", but "keep the dominant path deterministic, then layer probabilistic intelligence only where it earns its cost". The result is a system whose baseline remains rules-driven and inspectable, while ML, semantic search, and optional LLM assistance enrich the hard cases rather than redefine the whole runtime.

## System Thesis

Three claims define the project:

1. **Local-first beats hosted convenience for personal bookmark archives.** The input contains browsing intent, project history, and research trails. Treating that corpus as a cloud-default workload would violate the user's trust boundary.
2. **Rules should own the common path.** Deterministic matches for known domains remain the fastest, cheapest, and most interpretable decision mechanism. They also establish a stable backbone for fallback behavior.
3. **Fusion is a coordination problem, not a branding label.** The interesting part is not that multiple classifiers exist, but how their confidence, ordering, and optionality are combined into one operational result.<CiteReference id="1" authors="Kuncheva, L. I." title="Combining Pattern Classifiers: Methods and Algorithms" venue="Wiley-Interscience" year="2004" />

## Runtime Boundary

The maintained system boundary is intentionally narrow:

| Surface | In scope | Why it matters |
|---------|----------|----------------|
| Input | Browser bookmark exports, primarily HTML and related local formats | The tool starts from files the user already controls |
| Processing | Deduplication, classification, organization, export | Everything important happens inside the local runtime |
| Output | Cleaned bookmark HTML, JSON data, Markdown reports | Outputs must remain portable and auditable |
| Optional integrations | ML models, semantic analysis, local or remote LLM providers | Intelligence is additive, not a prerequisite |
| Out of scope | Hosted account sync, central database, telemetry pipeline | These would enlarge operational burden and privacy risk |

This boundary explains many later choices. The project can support richer intelligence, but not at the cost of turning the bookmark archive into a service-shaped problem.

## Architecture Model

The runtime is organized as a sequence of explicitly named layers:

1. **Entry surfaces**: CLI and thin Python entry points.
2. **Facade and composition root**: `BookmarkProcessor` plus the container that wires dependencies.
3. **Coordinator**: the runtime control layer that sequences each stage.
4. **Pipelines**: load, deduplicate, classify, organize, export.
5. **Intelligence modules**: rule engine, ML classifier, semantic analyzer, optional LLM, then fusion.

This structure is valuable because it separates *what changes often* from *what should remain stable*. The CLI contract can stay narrow while classifier internals evolve. The facade can stay shallow while orchestration changes. The pipeline can change stage internals without re-teaching the entire repository to new contributors.

## Fusion and Confidence

The project uses weighted voting rather than a stacked meta-model for the final classification step. That choice is pragmatic:

- The participating engines are heterogeneous. Rule matches are discrete and authoritative, while ML, semantic, and LLM outputs are probabilistic or confidence-shaped.
- A second learned layer would require extra calibration data and would reduce the transparency of why one bookmark landed in one folder rather than another.<CiteReference id="2" authors="Wolpert, D. H." title="Stacked Generalization" venue="Neural Networks" year="1992" url="https://doi.org/10.1016/S0893-6080(05)80023-1" />
- Weighted voting lets the system preserve a strong rules-first stance while still absorbing signal from other engines.

Confidence calibration matters because raw classifier scores are not directly comparable. The system therefore treats confidence as an engineered interface, not a cosmetic number.<CiteReference id="3" authors="Zadrozny, B.; Elkan, C." title="Obtaining Calibrated Probability Estimates from Decision Trees and Naive Bayesian Classifiers" venue="ICML" year="2001" />

## Performance Methodology

Performance numbers on this site should be read as *measurement envelopes*, not universal promises.

### Measurement dimensions

| Dimension | Why it matters |
|-----------|----------------|
| Cold start | Measures the cost of entering the runtime before heavy dependencies load |
| Throughput | Captures steady-state bookmark processing once the pipeline is active |
| Mode selection | Rules-only, hybrid ML, and optional LLM modes have very different cost profiles |
| Memory footprint | Practical limit for large local bookmark archives |
| Concurrency behavior | Indicates how much benefit the current workload extracts from thread-level parallelism |

### Interpretation

- **Rules-only paths** represent the minimum latency, highest determinism path.
- **Hybrid paths** trade more CPU and model initialization cost for better recovery on weak or ambiguous bookmarks.
- **LLM-assisted paths** should be understood as selective escalation, not the default execution mode.

The key architectural point is that performance is a consequence of the system boundary: local execution, delayed heavy initialization, and a rules-dominant common path.

## Failure Modes and Fallbacks

The runtime is intentionally designed to degrade, not collapse:

| Failure mode | Expected behavior |
|--------------|-------------------|
| Bookmark export is malformed | Loading fails early with a visible parsing boundary, before later stages run |
| Rule match is absent | The bookmark flows into probabilistic classification instead of producing an empty result |
| ML or semantic dependencies are unavailable | The system can still execute a narrower rules-first path |
| LLM integration is unavailable or disabled | The main classification flow remains intact because LLM is optional |
| Confidence is weak or conflicting | Fusion surfaces a lower-certainty outcome rather than fabricating certainty |

This is the main reason the architecture avoids making the most expensive intelligence layer the most central one.

## Reference Trail

- [Pipeline Architecture](/en/architecture/pipeline) explains the stage-level runtime.
- [Performance Methodology](/en/performance/optimization) frames how published numbers should be interpreted.
- [References](/en/resources/references) collects the literature behind fusion, calibration, and architecture choices.
- [Related Projects](/en/resources/related-projects) compares adjacent tools and enabling stacks.
- [Evolution](/en/evolution) explains how the current structure emerged from earlier code shapes.
