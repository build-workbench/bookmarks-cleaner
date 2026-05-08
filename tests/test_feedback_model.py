"""测试反馈增量模型"""

import pytest
from src.services.feedback_model import FeedbackIncrementalModel


def test_initialization():
    """测试模型初始化"""
    model = FeedbackIncrementalModel()

    assert model.classes_ == []
    assert model._label_by_signature == {}
    assert model._label_counts == {}


def test_partial_fit():
    """测试增量训练"""
    model = FeedbackIncrementalModel()
    features = [{"url": "https://example.com", "title": "Example"}]
    labels = ["技术"]

    result = model.partial_fit(features, labels)

    assert result is model  # 支持链式调用
    assert "技术" in model.classes_
    assert model._label_counts["技术"] == 1


def test_partial_fit_with_multiple_labels():
    """测试多标签训练"""
    model = FeedbackIncrementalModel()
    features = [
        {"url": "https://example.com", "title": "Example"},
        {"url": "https://python.org", "title": "Python"},
    ]
    labels = ["技术", "编程"]

    model.partial_fit(features, labels)

    assert "技术" in model.classes_
    assert "编程" in model.classes_
    assert len(model.classes_) == 2


def test_predict():
    """测试预测"""
    model = FeedbackIncrementalModel()
    features = [{"url": "https://example.com", "title": "Example"}]
    labels = ["技术"]
    model.partial_fit(features, labels)

    predictions = model.predict(features)

    assert len(predictions) == 1
    assert predictions[0] == "技术"


def test_predict_unknown():
    """测试未知特征的预测"""
    model = FeedbackIncrementalModel()
    features = [{"url": "https://example.com", "title": "Example"}]
    labels = ["技术"]
    model.partial_fit(features, labels)

    # 预测未见过的特征
    unknown_features = [{"url": "https://unknown.com", "title": "Unknown"}]
    predictions = model.predict(unknown_features)

    assert len(predictions) == 1
    assert predictions[0] == "技术"  # 返回默认标签（最常见的）


def test_signature_generation():
    """测试特征签名生成"""
    model = FeedbackIncrementalModel()

    sig1 = model._signature(
        {"url": "https://www.example.com/path", "title": " Example "}
    )
    sig2 = model._signature({"url": "https://example.com/other", "title": "Example"})
    sig3 = model._signature({"url": "https://Example.Com/", "title": "EXAMPLE"})
    sig4 = model._signature({"url": "https://example.com/", "title": "Different"})

    # 相同域名和标题应该生成相同的签名（忽略www、大小写、空格）
    assert sig1 == sig2  # " Example " 和 "Example" 标准化后相同
    assert sig2 == sig3  # 大小写不敏感
    # 不同标题生成不同签名
    assert sig2 != sig4


def test_get_label_counts():
    """测试获取标签计数"""
    model = FeedbackIncrementalModel()
    features = [
        {"url": "https://example.com", "title": "Example"},
        {"url": "https://python.org", "title": "Python"},
        {"url": "https://example.com", "title": "Example"},  # 重复特征
    ]
    labels = ["技术", "编程", "技术"]

    model.partial_fit(features, labels)
    counts = model.get_label_counts()

    assert counts["技术"] == 2
    assert counts["编程"] == 1


def test_clear():
    """测试清空模型"""
    model = FeedbackIncrementalModel()
    features = [{"url": "https://example.com", "title": "Example"}]
    labels = ["技术"]

    model.partial_fit(features, labels)
    model.clear()

    assert model.classes_ == []
    assert model._label_by_signature == {}
    assert model._label_counts == {}


def test_empty_predict():
    """测试空模型预测"""
    model = FeedbackIncrementalModel()
    features = [{"url": "https://example.com", "title": "Example"}]

    predictions = model.predict(features)

    assert len(predictions) == 1
    assert predictions[0] == "未分类"  # 默认标签


def test_incremental_learning():
    """测试增量学习"""
    model = FeedbackIncrementalModel()

    # 第一次训练
    features1 = [{"url": "https://example.com", "title": "Example"}]
    labels1 = ["技术"]
    model.partial_fit(features1, labels1)

    # 第二次训练
    features2 = [{"url": "https://python.org", "title": "Python"}]
    labels2 = ["编程"]
    model.partial_fit(features2, labels2)

    # 验证两次训练都生效
    assert "技术" in model.classes_
    assert "编程" in model.classes_
    assert model._label_counts["技术"] == 1
    assert model._label_counts["编程"] == 1
