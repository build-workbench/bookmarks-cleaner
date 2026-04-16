# ML 设计文档

## 项目背景与目标

### 当前系统的现状与挑战

CleanBook 主流程采用基于 `config.json` 的规则引擎，可选叠加本地 ML 与 LLM。该引擎通过关键词匹配、域名判断和加权评分等方式对书签进行分类。

**优点：**
- **确定性强**: 规则明确，分类结果可预测、可解释
- **配置灵活**: 用户可以通过修改 JSON 文件自定义分类逻辑，无需改动代码

**挑战：**
- **规则维护成本高**: 随着书签增多，需要不断调整关键词、权重和排除项
- **泛化能力弱**: 无法处理未在规则中定义的新内容
- **处理模糊性能力差**: 对于可归入多个分类的书签，规则系统通常只能"一刀切"

### 核心目标

引入机器学习模型，将书签分类从"手动规则驱动"升级为"数据驱动"：

- **提升分类准确率**: 利用 AI 模型的学习能力，做出更精准的分类判断
- **降低维护成本**: 将维护工作从"编写复杂规则"转变为"标注高质量数据"
- **增强系统适应性**: 模型能够从新数据中持续学习
- **保留规则系统的优点**: 采用**"规则 + AI"**的混合策略

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      数据准备阶段                                  │
│  运行现有脚本 → 人工校对 → 生成 labeled_bookmarks.csv            │
└─────────────────────────────────┬───────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      模型训练阶段                                  │
│  train_model.py → 特征提取(TF-IDF) → 训练分类器 → 保存模型        │
└─────────────────────────────────┬───────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      集成应用阶段                                  │
│  加载模型 → 混合分类策略 → 高优先级规则 → ML预测 → LLM兜底        │
└─────────────────────────────────────────────────────────────────┘
```

## 核心算法

### 集成学习模型

系统集成了 6 种机器学习算法，并通过集成学习提升整体性能：

| 算法 | 准确率 | 训练时间 | 预测时间 | 特点 |
|------|--------|----------|----------|------|
| Random Forest | 78.4% | 2.3s | 0.8ms | 抗过拟合，处理高维特征好 |
| SVM | 73.3% | 15.2s | 1.2ms | 处理非线性问题效果好 |
| Logistic Regression | 88.8% | 1.8s | 0.3ms | 计算效率高，可解释性强 |
| Naive Bayes | 88.8% | 0.5s | 0.2ms | 文本分类效果好，训练快 |
| Gradient Boosting | 85.3% | 8.7s | 0.9ms | 预测精度高，复杂关系处理 |
| SGD | 88.8% | 1.2s | 0.4ms | 支持在线学习，大规模数据 |

### 特征工程

#### 文本特征提取（TF-IDF）

```python
TfidfVectorizer(
    max_features=500,      # 最大特征数
    ngram_range=(1, 2),    # 1-2 元语法
    min_df=1,             # 最小文档频率
    lowercase=True,       # 小写转换
    stop_words=None       # 不使用停用词
)
```

#### 数值特征

- URL 长度
- 标题长度
- 域名深度
- 路径深度
- HTTPS 标识
- 数字标识
- 中文标识

#### 分类特征编码

- 内容类型编码
- 语言类型编码
- 域名特征编码

### 投票分类器

```python
VotingClassifier(
    estimators=[
        ('rf', RandomForestClassifier),
        ('lr', LogisticRegression),
        ('nb', MultinomialNB)
    ],
    voting='soft'          # 软投票，基于概率
)
```

**准确率**: 91.4%

## 训练流程

```
原始数据 (CSV)
    │
    ▼
数据预处理
- 数据清洗
- 标签编码
    │
    ▼
特征工程
- 合并 URL + 标题
- TF-IDF 向量化
- 特征选择
    │
    ▼
数据拆分
- 训练集 (80%)
- 测试集 (20%)
    │
    ▼
模型训练
- 多算法并行训练
-  Grid Search 调参
    │
    ▼
模型评估
- 准确率
- 精确率
- 召回率
- F1 分数
    │
    ▼
模型集成
- VotingClassifier
- 权重优化
    │
    ▼
模型持久化
- joblib.dump
- bookmark_classifier.joblib
```

## 在线学习机制

### 增量学习

```python
class MLClassifier:
    def __init__(self):
        self.online_buffer = {'data': [], 'labels': []}
        self.online_buffer_size = 1000
        
    def learn_from_feedback(self, url: str, title: str, correct_category: str):
        """从反馈中学习"""
        self.online_buffer['data'].append((url, title))
        self.online_buffer['labels'].append(correct_category)
        
        if len(self.online_buffer['data']) >= self.online_buffer_size:
            self._incremental_train()
```

### 模型更新策略

| 触发条件 | 操作 |
|----------|------|
| 缓冲区满 | 执行增量训练 |
| 定期任务 | 每周自动重训练 |
| 准确率下降 | 触发完整重训练 |

## 性能指标与基准测试

### 训练数据规模影响

```
样本数    准确率
───────   ──────
50        65%
100       78%
200       84%
300       87%
400       89%
500       90%
576       91.4%
```

### 处理速度

| 数据规模 | 数量 | 处理时间 | 吞吐量 |
|----------|------|----------|--------|
| small | 100 | 2.3s | 43/s |
| medium | 1000 | 18.7s | 53/s |
| large | 5000 | 89.2s | 56/s |
| extra_large | 10000 | 178.5s | 56/s |

## 未来发展方向

### 深度学习集成

- **BERT/RoBERTa**: 用于文本特征提取和语义理解
- **Sentence-BERT**: 句子相似度计算
- **轻量级 transformer**: 适合本地部署

### 主动学习 (Active Learning)

对于模型预测不确定的书签，主动提示用户进行标注，最高效地扩充训练数据集。

### 模型漂移检测

```python
class ModelDriftDetector:
    def detect_drift(self, recent_results: List[ClassificationResult]) -> bool:
        """检测模型漂移"""
        recent_accuracy = self._calculate_accuracy(recent_results)
        if abs(recent_accuracy - self.baseline_accuracy) > threshold:
            return True
        return False
```

当检测到模型性能下降时，自动触发重训练流程。
