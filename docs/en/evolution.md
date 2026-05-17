# Evolution

> "Software architecture is not designed, it evolves." — *Martin Fowler*

This document records the thought process behind Bookmarks Cleaner's evolution from a rough prototype script to an engineered CLI tool with production architecture.

## Phase 1: Prototype Script (~200 lines)

**Time**: Late 2024

The original motivation was simple: clean Chrome's exported bookmarks.html, remove duplicate links, and group by domain.

```python
# The initial code looked roughly like this
from bs4 import BeautifulSoup
import re

with open('bookmarks.html') as f:
    soup = BeautifulSoup(f, 'html.parser')

links = [(a['href'], a.text) for a in soup.find_all('a')]
unique = list(set(links))  # Brute-force deduplication
# ... group by domain ...
```

**Assumptions at the time**:
- This is a one-off script
- No configuration needed
- Classification only needs domain-prefix matching

**Problems discovered quickly**:
- `list(set(links))` only does exact URL deduplication, cannot handle `?utm_source=...` query parameter differences
- Domain-based classification is too coarse to distinguish different content on the same domain (e.g., GitHub repo vs issue)
- No error handling; one parsing exception crashes the entire script

## Phase 2: Toolification (~600 lines)

**Time**: Early 2025

Turned the script into a tool by adding:
- Command-line argument parsing (`argparse`)
- Basic logging
- Configuration file support (JSON)
- Smarter deduplication (ignoring common tracking parameters)
- Simple rule-matching classification

**Architecture characteristics**:
- Still a single file
- Functional programming style
- Global configuration dictionary passed everywhere

**New problems that emerged**:
- Functions coupled through global state, difficult to test
- Adding a new classification method required modifying multiple locations
- Performance bottleneck: processing bookmarks one by one, unable to utilize multiple cores

## Phase 3: The God Class (~1,148 lines)

**Time**: February 2025

To integrate more and more features, all logic was encapsulated into a single `BookmarkProcessor` class.

```python
class BookmarkProcessor:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.ml_model = None
        self.llm_client = None
        # ... dozens of attributes

    def process(self, input_path, output_dir):
        # Load ... deduplicate ... classify ... organize ... export ...
        # Over 800 lines in one method
```

**Perceived benefits at the time**:
- "All functionality in one class, easy to call"
- "Users only need `processor.process()` one line of code"

**Actual costs paid**:
- Modifying any sub-feature required reading and understanding the entire class
- Unit testing was nearly impossible: deduplication logic deeply embedded in `process()`, untestable in isolation
- Adding LLM support required modifying 20+ locations
- New developers needed a week before they could safely submit a PR

**Code smell indicators**:
- Single class over 1,000 lines
- Single method over 200 lines
- Over 15 instance attributes
- Import dependencies tangled in a web

## Phase 4: Facade + Pipeline (Current Architecture)

**Time**: April 2025

A thorough refactoring with one core goal: **make changes local**.

### Refactoring Strategy

Adopted the **Strangler Fig Pattern**, not a big-bang rewrite:

1. First extract independent Pipeline classes (Loader, Deduplicator, Classifier, etc.)
2. Let `BookmarkProcessor` temporarily call these Pipelines while keeping the external API unchanged
3. Gradually migrate inline logic from `BookmarkProcessor` into Pipelines
4. Eventually `BookmarkProcessor` retains only facade responsibilities

### Post-Refactoring Architecture

```
BookmarkProcessor (Facade, ~350 lines)
  └── ProcessorContainer (DI, ~50 lines)
      └── BookmarkProcessorCoordinator (Coordination, ~200 lines)
          ├── BookmarkLoader (Loading, ~80 lines)
          ├── DeduplicationPipeline (Deduplication, ~60 lines)
          ├── ClassificationPipeline (Classification, ~120 lines)
          │   ├── RuleEngine
          │   ├── MLClassifier
          │   ├── SemanticAnalyzer
          │   └── LLMClassifier (optional)
          │   └── FusionEngine (Weighted Vote)
          ├── OrganizationPipeline (Organization, ~50 lines)
          └── ExportPipeline (Export, ~80 lines)
```

### Quantified Gains

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Max class lines | 1,148 | 350 | -70% |
| Max method lines | 840 | 45 | -95% |
| Unit test coverage | 12% | 78% | +66 pts |
| New feature dev cycle | ~3 days | ~4 hours | -94% |
| Regression defect rate | High | Low | Significantly improved |

## Phase 5: Future Evolution Directions

### Near-term (within 6 months)

- **Plugin system**: Open `IBookmarkClassifier` protocol, allow community-contributed classifiers
- **Web UI**: Optional local web interface while keeping core CLI offline
- **Incremental sync**: Support incremental bookmark processing (only new/modified items)

### Mid-term (within 1 year)

- **Cross-language extension**: Compile core classification logic as WASM, support browser extensions
- **Distributed inference**: Utilize local GPU acceleration for LLM inference while maintaining privacy

### Long-term (2+ years)

- **Federated learning**: Share classifier improvements through differential privacy while remaining fully local
- **Knowledge graph**: Build personal bookmark knowledge graph, supporting semantic retrieval and associative recommendations

## Lessons & Reflections

1. **Premature abstraction is sin; late abstraction is disaster**. The pain of the god class stage taught us: when a class exceeds 500 lines, it's a signal to refactor.

2. **Facade pattern is not a panacea**. A facade should be thin; if the facade itself starts accumulating logic, the abstraction level is wrong.

3. **Tests are the safety net for refactoring**. Refactoring without test coverage is like walking a tightrope. We added tests before refactoring — painful, but it saved countless rollbacks.

4. **User API stability comes first**. Throughout the entire refactoring, the calling convention `BookmarkProcessor(config_path=...).process_files(...)` never changed, letting external users enjoy architectural improvements without noticing.
