# Semantic Analyzer

The semantic analyzer extracts **semantic features** using TF-IDF or Sentence Transformers for similarity computation and classification enhancement.

## Vectorization Methods

### TF-IDF

Traditional term frequency statistics:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),
)
```

**Pros**: Fast, interpretable, no GPU needed  
**Cons**: Cannot capture word order and semantics

### Sentence Transformers

Pretrained model-based semantic vectorization:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts)
```

| Model | Dimensions | Speed | Quality |
|-------|------------|-------|---------|
| all-MiniLM-L6-v2 | 384 | Fast | Good |
| all-mpnet-base-v2 | 768 | Medium | Very Good |

## Related Docs

- [ML Classifier](/en/algorithms/ml-classifier) - ML classification
- [Fusion Algorithm](/en/algorithms/fusion) - Multi-classifier fusion
