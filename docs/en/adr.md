# Architecture Decision Records (ADR)

This document records key architectural decisions and their trade-offs in the design and implementation of Bookmarks Cleaner. Each decision follows the standard ADR format: Context, Decision, Consequences.

## ADR-001: Pipeline Architecture vs. DAG

**Status**: Adopted | **Date**: 2025-03

### Context

Bookmark processing is fundamentally a linear transformation sequence: Load → Deduplicate → Classify → Organize → Export. During early design, the team considered a more general DAG execution engine to support future non-linear processing (branching, conditional jumps).

### Decision

Adopt a **five-stage linear Pipeline** instead of a DAG engine.

### Rationale

1. **Cognitive complexity**: DAG configuration is too complex for CLI users; linear Pipeline semantics are self-evident
2. **Performance**: Linear execution avoids DAG scheduler topological sorting and dynamic dispatch overhead
3. **Testability**: Linear pipeline input/output contracts are clear; each stage is independently unit-testable
4. **YAGNI**: Current and foreseeable requirements are all linear; DAG would be over-engineering

### Consequences

- **Positive**: Code volume reduced by ~40%, maintenance cost significantly lowered
- **Negative**: If conditional branching is needed in the future (e.g., "enable LLM only when confidence is low"), it must be implemented inside the Pipeline rather than through topological scheduling

---

## ADR-002: ThreadPool vs. Asyncio

**Status**: Adopted | **Date**: 2025-03

### Context

Concurrency is key to performance optimization. Python offers two main concurrency models: `asyncio` (coroutines) and `ThreadPoolExecutor` (multithreading).

### Decision

Use `ThreadPoolExecutor` for concurrent classification.

### Rationale

1. **Library compatibility**: Core dependencies like scikit-learn and sentence-transformers lack native async/await support
2. **CPU-bound nature**: Bookmark classification is dominated by text feature extraction and model inference, which are CPU-bound; the GIL is not a bottleneck
3. **Debugging cost**: Thread exception stacks are straightforward; asyncio call chain tracing is difficult in complex scenarios
4. **API simplicity**: `concurrent.futures` is easier to use than asyncio

### Consequences

- **Positive**: Seamless integration with existing ML ecosystem, no async adapter layer needed
- **Negative**: In I/O-intensive scenarios (e.g., large-scale LLM API calls), coroutines offer higher resource efficiency

---

## ADR-003: Protocol Interfaces vs. Abstract Base Classes

**Status**: Adopted | **Date**: 2025-04

### Context

Python offers two ways to define interfaces: `abc.ABC` (abstract base classes) and `typing.Protocol` (structural subtyping). The project needed contracts for classifiers, pipelines, and coordinators.

### Decision

Use `typing.Protocol` for all core interfaces.

### Rationale

1. **Non-intrusive**: Protocol does not require implementing classes to explicitly inherit, avoiding inheritance coupling
2. **Duck typing**: Any class implementing the protocol methods automatically satisfies the interface, without modifying existing code
3. **Type checker support**: mypy has mature Protocol support for static type checking
4. **Pythonic**: Aligns with the "if it walks like a duck..." Python philosophy

### Consequences

- **Positive**: Third-party extensions need not inherit internal project classes, lowering integration barriers
- **Negative**: Runtime checking requires additional implementation (`isinstance` + Protocol works in Python 3.8+ but with slightly different behavior)

---

## ADR-004: Weighted Voting Fusion vs. Stacking

**Status**: Adopted | **Date**: 2025-04

### Context

Common multi-classifier fusion methods include:
- **Bagging**: Homogeneous classifiers in parallel, majority voting
- **Boosting**: Serial training, focusing on misclassified samples
- **Stacking**: Meta-learner fuses classifier outputs
- **Weighted voting**: Simple linear combination

### Decision

Use **weighted voting** as the default fusion strategy, with Stacking as a pluggable extension.

### Rationale

1. **Heterogeneous output space**: Rule engine outputs discrete categories (confidence=1.0), while ML/LLM outputs probability distributions. A Stacking meta-learner struggles with this heterogeneity
2. **Cold start**: Weighted voting requires no training data; Stacking needs an additional hold-out set to train the meta-model
3. **Interpretability**: Weighted voting's decision process is fully transparent; each classifier's contribution is precisely calculable
4. **Computational cost**: Weighted voting is O(n); Stacking is O(n) + meta-inference overhead

### Consequences

- **Positive**: Users get good fusion results with zero configuration
- **Negative**: When the number of classifiers grows (>10) and complex interactions exist, Stacking may capture non-linear combination patterns

---

## ADR-005: dataclass DI Container vs. Framework

**Status**: Adopted | **Date**: 2025-04

### Context

Component management considered introducing a dependency injection framework (e.g., `dependency-injector`, `inject`) versus manually implementing a container.

### Decision

Use the standard library `dataclasses.dataclass` to implement a lightweight DI container `ProcessorContainer`.

### Rationale

1. **Zero dependencies**: No third-party DI framework, keeping the project lightweight
2. **Lazy creation**: Components initialized lazily through properties
3. **Injectability**: All component fields prefixed with `_` support direct mock injection during testing
4. **Type safety**: dataclass field declarations carry type annotations

```python
@dataclass
class ProcessorContainer:
    config: Dict[str, Any]
    _coordinator: Optional["ICoordinator"] = field(default=None, repr=False)
```

### Consequences

- **Positive**: Code is self-contained, no external dependency risks
- **Negative**: Lifecycle management (singleton/scope) must be manually implemented, less complete than professional frameworks

---

## ADR-006: Facade Pattern for God Class Refactoring

**Status**: Adopted | **Date**: 2025-04

### Context

The original implementation had `BookmarkProcessor` as a 1,148-line "god class" handling loading, deduplication, classification, organization, export, LLM integration, and health checks.

### Decision

Refactor `BookmarkProcessor` into a **Facade class (~350 lines)**, delegating core logic to `BookmarkProcessorCoordinator` and five Pipelines.

### Rationale

1. **Single responsibility**: Each class does one thing, following SOLID principles
2. **Testability**: The Facade can be unit-tested by injecting a mock Container without constructing a full dependency tree
3. **Replaceability**: Any Pipeline can be replaced with a custom implementation without affecting other stages
4. **Cognitive load**: Developers only need to understand the Pipeline they are modifying, rather than reading through 1,148 lines

### Consequences

- **Positive**: Code maintainability significantly improved, new feature development cycle shortened
- **Negative**: Increased class and file count, slight navigation cost increase (offset by IDE jump-to-definition)

---

## ADR-007: Confidence Calibration Enabled by Default

**Status**: Adopted | **Date**: 2025-05

### Context

Raw confidence from ML models and semantic analyzers often exhibits systematic bias (e.g., neural networks tend toward over-confidence).

### Decision

Enable Platt Scaling calibration by default; users can switch to Isotonic Regression or disable via configuration.

### Rationale

1. **Accuracy**: Calibrated confidence is closer to true probability, improving fusion engine decision quality
2. **Low overhead**: Platt Scaling only needs to fit two parameters (a, b), computation cost is negligible
3. **Configurable**: Preserves flexibility, allowing advanced users to choose alternative calibration strategies

### Consequences

- **Positive**: Post-fusion classification accuracy improved by ~3-5%
- **Negative**: Requires collecting a certain amount of feedback data to fit optimal calibration parameters (reverts to identity mapping at cold start)
