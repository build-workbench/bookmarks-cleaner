"""
测试 ClassificationCoordinator
"""

import pytest
from src.processing.classification_coordinator import ClassificationCoordinator
from src.plugins.base import BookmarkFeatures, ClassificationResult


class MockClassifier:
    """模拟分类器"""

    def classify(self, features: BookmarkFeatures) -> ClassificationResult:
        return ClassificationResult(
            category="技术",
            confidence=0.9,
            method="mock",
        )


class TestClassificationCoordinator:
    """测试 ClassificationCoordinator"""

    @pytest.fixture
    def coordinator(self):
        """创建协调器"""
        return ClassificationCoordinator(MockClassifier())

    @pytest.fixture
    def features(self):
        """创建测试特征"""
        return BookmarkFeatures(
            url="https://example.com",
            title="Example",
            domain="example.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )

    def test_classify_single(self, coordinator, features):
        """分类单个书签"""
        result = coordinator.classify_single(features)
        assert result.category == "技术"
        assert result.confidence == 0.9

    def test_classify_batch(self, coordinator):
        """批量分类"""
        features_list = [
            BookmarkFeatures(
                url=f"https://example{i}.com",
                title=f"Example {i}",
                domain=f"example{i}.com",
                path_segments=[],
                query_params={},
                content_type="webpage",
                language="en",
            )
            for i in range(3)
        ]
        results = coordinator.classify_batch(features_list)
        assert len(results) == 3
        assert all(r.category == "技术" for r in results)

    def test_classify_batch_empty(self, coordinator):
        """批量分类空列表"""
        results = coordinator.classify_batch([])
        assert results == []

    def test_satisfies_protocol(self):
        """ClassificationCoordinator 可与 IClassifier 协作"""
        from src.interfaces import IClassifier

        # MockClassifier 满足 IClassifier
        mock = MockClassifier()
        assert hasattr(mock, "classify")
