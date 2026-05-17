# Fusion Algorithm

The Fusion Engine is the core of Bookmarks Cleaner's classification system, responsible for weighted fusion of multiple classifier results.

## Problem Statement

Each classifier has its strengths and weaknesses:

| Classifier | Strength | Weakness |
|------------|----------|----------|
| Rule Engine | Fast, deterministic | Limited coverage |
| ML Classifier | Good generalization | Requires training data |
| Semantic Analyzer | Understands semantics | High computational cost |
| LLM | Intelligent understanding | High cost, latency |

**Fusion Goal**: Combine classifier strengths to improve overall accuracy.

## Weighted Voting Algorithm

### Basic Formula

$$S(c) = \sum_{i=1}^{n} w_i \cdot \mathbb{1}_{y_i = c} \cdot conf_i$$

Where:
- $S(c)$ is the total score for category $c$
- $w_i$ is the weight of classifier $i$
- $y_i$ is the predicted category of classifier $i$
- $conf_i$ is the confidence of classifier $i$

### Implementation

```python
class FusionEngine:
    """Fusion Engine"""
    
    DEFAULT_WEIGHTS = {
        "rule": 0.35,
        "ml": 0.25,
        "semantic": 0.20,
        "llm": 0.20,
    }
    
    def fuse(self, results: List[ClassificationResult]) -> ClassificationResult:
        """Fuse multiple classification results"""
        scores = self._calculate_scores(results)
        best_category = max(scores, key=scores.get)
        confidence = self._calculate_confidence(scores, best_category)
        
        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            source="fusion",
        )
```

## Performance Benchmarks

| Fusion Strategy | Accuracy | Recall | F1 |
|-----------------|----------|--------|-----|
| Single Rule | 72% | 65% | 0.68 |
| Single ML | 78% | 82% | 0.80 |
| Rule + ML | 85% | 83% | 0.84 |
| Full Fusion | **91%** | **88%** | **0.89** |

## Related Docs

- [Rule Engine](/en/algorithms/rule-engine) - Rule classification
- [ML Classifier](/en/algorithms/ml-classifier) - ML classification
- [LLM Integration](/en/algorithms/llm-integration) - LLM integration
