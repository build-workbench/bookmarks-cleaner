"""
Feedback Incremental Model - 反馈增量模型
用于离线反馈训练与版本化
"""

from typing import Dict, List
from urllib.parse import urlparse


class FeedbackIncrementalModel:
    """
    轻量级反馈增量模型

    基于特征签名进行增量学习和预测，支持在线更新。

    Attributes:
        classes_: 已知类别列表
        _label_by_signature: 特征签名到标签的映射
        _label_counts: 每个标签的出现次数
    """

    def __init__(self):
        """初始化反馈增量模型"""
        self.classes_: List[str] = []
        self._label_by_signature: Dict[str, str] = {}
        self._label_counts: Dict[str, int] = {}

    def partial_fit(self, X, y, classes=None):
        """
        增量训练模型

        Args:
            X: 特征列表，每个特征是包含 'url' 和 'title' 的字典
            y: 标签列表
            classes: 可选的完整类别列表

        Returns:
            self，支持链式调用
        """
        if classes:
            merged = set(self.classes_) | set(classes)
            self.classes_ = sorted(str(label) for label in merged)

        for features, label in zip(X, y):
            label = str(label)
            signature = self._signature(features)
            self._label_by_signature[signature] = label
            self._label_counts[label] = self._label_counts.get(label, 0) + 1

            # 将标签添加到 classes_（如果没有 classes 参数）
            if classes is None and label not in self.classes_:
                self.classes_.append(label)
                self.classes_.sort()

        return self

    def predict(self, X):
        """
        预测标签

        Args:
            X: 特征列表，每个特征是包含 'url' 和 'title' 的字典

        Returns:
            预测标签列表
        """
        default_label = max(
            self._label_counts,
            key=self._label_counts.get,
            default="未分类",
        )
        return [
            self._label_by_signature.get(self._signature(features), default_label)
            for features in X
        ]

    def _signature(self, features: Dict) -> str:
        """
        生成特征签名

        Args:
            features: 特征字典，包含 'url' 和 'title'

        Returns:
            特征签名字符串
        """
        url = str(features.get("url", ""))
        title = str(features.get("title", "")).strip().lower()
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return f"{domain}::{title}"

    def get_label_counts(self) -> Dict[str, int]:
        """
        获取标签计数

        Returns:
            标签到计数的映射字典
        """
        return dict(self._label_counts)

    def clear(self):
        """清空模型"""
        self.classes_ = []
        self._label_by_signature = {}
        self._label_counts = {}
