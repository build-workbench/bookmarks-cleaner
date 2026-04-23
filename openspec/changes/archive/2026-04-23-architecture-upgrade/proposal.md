# Proposal: Architecture Algorithm Upgrade

## Why

The existing system uses a layered architecture with hard-coded classifiers that are difficult to extend. Key limitations include:

- No unified plugin management mechanism
- Feature extraction and classification are coupled
- Lacks active learning and incremental update capabilities
- Limited extensibility for new classification methods

## What Changes

Evolve from a monolithic architecture to a modular, extensible plugin-based architecture, while introducing advanced classification algorithms (Transformer embeddings, active learning, incremental learning) to improve classification accuracy and system performance.

## Capabilities

### New Capabilities

- `plugin-architecture`: Hot-pluggable classifiers, exporters, and feature extractors
- `embedding-service`: Transformer embeddings for semantic similarity
- `active-learning`: User feedback integration for model improvement
- `incremental-training`: Online learning without full retraining
- `feature-store`: Caching and management of feature vectors
- `performance-monitor`: Comprehensive metrics tracking

### Modified Capabilities

- `bookmark-classifier`: Enhanced with multi-method fusion and plugin pipeline

## Impact

### Code
- New `src/plugins/` directory for plugin system
- New `src/services/` directory for supporting services
- Refactored `src/ai_classifier.py` as orchestrator

### Dependencies
- Added: sentence-transformers (optional)
- Added: joblib (optional, for model persistence)

### Performance
- Improved classification accuracy through ensemble methods
- Reduced latency through feature caching
- Lower memory footprint via lazy initialization

## Non-Goals

- REST API implementation (deferred)
- Database persistence (deferred)
- Real-time classification (not required)
