"""
Classification Coordinator - 分类协调器

协调多个分类器的执行，处理并行分类和结果收集。

深度: 高（简单接口，复杂的并行调度逻辑）
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from src.interfaces import IClassifier
    from src.plugins.base import BookmarkFeatures, ClassificationResult


class ClassificationCoordinator:
    """
    分类协调器

    协调分类器的执行，支持并行处理。

    示例:
        coordinator = ClassificationCoordinator(classifier)
        results = coordinator.classify_batch(features_list)
    """

    def __init__(
        self,
        classifier: "IClassifier",
        max_workers: int = 4,
    ):
        """
        初始化分类协调器

        Args:
            classifier: 分类器实例
            max_workers: 最大并行线程数
        """
        self.classifier = classifier
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    def classify_single(
        self,
        features: "BookmarkFeatures",
    ) -> "ClassificationResult":
        """
        分类单个书签

        Args:
            features: 书签特征

        Returns:
            分类结果
        """
        return self.classifier.classify(features)

    def classify_batch(
        self,
        features_list: List["BookmarkFeatures"],
        progress_callback: Optional[callable] = None,
    ) -> List["ClassificationResult"]:
        """
        批量分类书签

        Args:
            features_list: 书签特征列表
            progress_callback: 进度回调函数

        Returns:
            分类结果列表
        """
        if not features_list:
            return []

        results: List["ClassificationResult"] = [None] * len(features_list)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.classifier.classify, features): i
                for i, features in enumerate(features_list)
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    results[index] = result
                    if progress_callback:
                        progress_callback(index, result)
                except Exception as e:
                    self.logger.error(f"分类失败 (index {index}): {e}")
                    # 创建 fallback 结果
                    from src.plugins.base import ClassificationResult
                    results[index] = ClassificationResult(
                        category="未分类",
                        confidence=0.0,
                        reasoning=[f"分类失败: {e}"],
                        method="error",
                    )

        return results

    def classify_bookmarks(
        self,
        bookmarks: List[Dict[str, Any]],
        feature_extractor: callable,
    ) -> List[Dict[str, Any]]:
        """
        分类书签列表

        Args:
            bookmarks: 书签字典列表
            feature_extractor: 特征提取函数

        Returns:
            带有分类结果的书签列表
        """
        # 提取特征
        features_list = [
            feature_extractor(b.get("url", ""), b.get("title", ""))
            for b in bookmarks
        ]

        # 批量分类
        results = self.classify_batch(features_list)

        # 合并结果
        classified = []
        for bookmark, result in zip(bookmarks, results):
            classified_bookmark = dict(bookmark)
            classified_bookmark["category"] = result.category
            classified_bookmark["confidence"] = result.confidence
            classified_bookmark["method"] = result.method
            classified_bookmark["reasoning"] = result.reasoning
            classified_bookmark["alternatives"] = result.alternatives
            classified.append(classified_bookmark)

        return classified
