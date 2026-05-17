# ML Classifier

The ML classifier uses **machine learning models** for bookmark classification, complementing the rule engine for cases it cannot cover.

## Feature Engineering

### Text Features

Extract features from bookmark title, URL, and description:

```python
class BookmarkFeatures:
    def extract(self, bookmark: Bookmark) -> np.ndarray:
        features = []
        
        # 1. TF-IDF features
        text = f"{bookmark.title} {bookmark.url} {bookmark.description}"
        tfidf = self.tfidf_vectorizer.transform([text])
        features.append(tfidf.toarray())
        
        # 2. Domain features
        domain_features = self._extract_domain_features(bookmark.url)
        features.append(domain_features)
        
        return np.concatenate(features)
```

## Model Selection

| Model | Training Time | Inference Latency | Accuracy | Memory |
|-------|---------------|-------------------|----------|--------|
| Naive Bayes | 0.5s | 0.1ms | 82% | 5MB |
| Linear SVM | 2s | 0.2ms | 87% | 10MB |
| Random Forest | 10s | 1ms | 89% | 50MB |

## Incremental Learning

```python
class IncrementalTrainer:
    def partial_fit(self, X: np.ndarray, y: np.ndarray):
        """Incremental training"""
        self.model.partial_fit(X, y, classes=self.classes_)
```

## Related Docs

- [Rule Engine](/en/algorithms/rule-engine) - Rule classification
- [Fusion Algorithm](/en/algorithms/fusion) - Multi-classifier fusion
