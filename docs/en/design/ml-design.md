# ML Design Document

## Project Background and Goals

### Current System Status and Challenges

CleanBook's main flow uses a rule-based engine from `config.json`, with optional local ML and LLM叠加. The engine classifies bookmarks through keyword matching, domain detection, and weighted scoring.

**Advantages:**
- **High certainty**: Rules are clear, classification results are predictable and explainable
- **Flexible configuration**: Users can customize classification logic by modifying JSON without changing code

**Challenges:**
- **High rule maintenance cost**: As bookmarks increase, keywords, weights, and exclusions need constant adjustment
- **Weak generalization**: Cannot handle new content not defined in rules
- **Poor ambiguity handling**: For bookmarks that could fit multiple categories, rule systems often make arbitrary choices

### Core Goals

Introduce machine learning models to upgrade bookmark classification from "manual rule-driven" to "data-driven":

- **Improve classification accuracy**: Leverage AI model learning capabilities for more precise judgments
- **Reduce maintenance costs**: Shift maintenance from "writing complex rules" to "annotating high-quality data"
- **Enhance system adaptability**: Models can continuously learn from new data
- **Preserve rule system advantages**: Adopt **"Rules + AI"** hybrid strategy

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Preparation Phase                      │
│  Run existing script → Manual review → Generate labeled_bookmarks.csv │
└─────────────────────────────────┬───────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Model Training Phase                        │
│  train_model.py → Feature Extraction (TF-IDF) → Train Classifier → Save Model │
└─────────────────────────────────┬───────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Integration Phase                           │
│  Load model → Hybrid strategy → High-priority rules → ML predict → LLM fallback │
└─────────────────────────────────────────────────────────────────┘
```

## Core Algorithms

### Ensemble Learning Model

The system integrates 6 machine learning algorithms, using ensemble learning to improve overall performance:

| Algorithm | Accuracy | Training Time | Prediction Time | Characteristics |
|-----------|----------|---------------|-----------------|-----------------|
| Random Forest | 78.4% | 2.3s | 0.8ms | Anti-overfitting, good for high-dim features |
| SVM | 73.3% | 15.2s | 1.2ms | Good for nonlinear problems |
| Logistic Regression | 88.8% | 1.8s | 0.3ms | High efficiency, explainable |
| Naive Bayes | 88.8% | 0.5s | 0.2ms | Good for text classification, fast training |
| Gradient Boosting | 85.3% | 8.7s | 0.9ms | High precision, complex relationships |
| SGD | 88.8% | 1.2s | 0.4ms | Online learning support, large-scale data |

### Feature Engineering

#### Text Feature Extraction (TF-IDF)

```python
TfidfVectorizer(
    max_features=500,      # Maximum features
    ngram_range=(1, 2),    # 1-2 grams
    min_df=1,             # Minimum document frequency
    lowercase=True,       # Lowercase conversion
    stop_words=None       # No stop words
)
```

#### Numerical Features

- URL length
- Title length
- Domain depth
- Path depth
- HTTPS indicator
- Number indicator
- Chinese indicator

#### Categorical Feature Encoding

- Content type encoding
- Language type encoding
- Domain feature encoding

### Voting Classifier

```python
VotingClassifier(
    estimators=[
        ('rf', RandomForestClassifier),
        ('lr', LogisticRegression),
        ('nb', MultinomialNB)
    ],
    voting='soft'          # Soft voting, based on probability
)
```

**Accuracy**: 91.4%

## Training Flow

```
Raw Data (CSV)
    │
    ▼
Data Preprocessing
- Data cleaning
- Label encoding
    │
    ▼
Feature Engineering
- Merge URL + Title
- TF-IDF vectorization
- Feature selection
    │
    ▼
Data Split
- Training set (80%)
- Test set (20%)
    │
    ▼
Model Training
- Multi-algorithm parallel training
- Grid Search parameter tuning
    │
    ▼
Model Evaluation
- Accuracy
- Precision
- Recall
- F1 Score
    │
    ▼
Model Ensemble
- VotingClassifier
- Weight optimization
    │
    ▼
Model Persistence
- joblib.dump
- bookmark_classifier.joblib
```

## Online Learning Mechanism

### Incremental Learning

```python
class MLClassifier:
    def __init__(self):
        self.online_buffer = {'data': [], 'labels': []}
        self.online_buffer_size = 1000
        
    def learn_from_feedback(self, url: str, title: str, correct_category: str):
        """Learn from feedback"""
        self.online_buffer['data'].append((url, title))
        self.online_buffer['labels'].append(correct_category)
        
        if len(self.online_buffer['data']) >= self.online_buffer_size:
            self._incremental_train()
```

### Model Update Strategy

| Trigger Condition | Action |
|-------------------|--------|
| Buffer full | Execute incremental training |
| Scheduled task | Weekly automatic retraining |
| Accuracy drop | Trigger full retraining |

## Performance Metrics and Benchmarks

### Training Data Scale Impact

```
Samples    Accuracy
───────    ──────
50         65%
100        78%
200        84%
300        87%
400        89%
500        90%
576        91.4%
```

### Processing Speed

| Data Scale | Count | Processing Time | Throughput |
|------------|-------|-----------------|------------|
| small | 100 | 2.3s | 43/s |
| medium | 1000 | 18.7s | 53/s |
| large | 5000 | 89.2s | 56/s |
| extra_large | 10000 | 178.5s | 56/s |

## Future Directions

### Deep Learning Integration

- **BERT/RoBERTa**: For text feature extraction and semantic understanding
- **Sentence-BERT**: Sentence similarity calculation
- **Lightweight transformers**: Suitable for local deployment

### Active Learning

For bookmarks where the model is uncertain in its prediction, proactively prompt users for annotation to most efficiently expand the training dataset.

### Model Drift Detection

```python
class ModelDriftDetector:
    def detect_drift(self, recent_results: List[ClassificationResult]) -> bool:
        """Detect model drift"""
        recent_accuracy = self._calculate_accuracy(recent_results)
        if abs(recent_accuracy - self.baseline_accuracy) > threshold:
            return True
        return False
```

When model performance degradation is detected, automatically trigger the retraining flow.
