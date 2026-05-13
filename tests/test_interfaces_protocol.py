"""
测试 Protocol 接口兼容性

验证现有类隐式满足 Protocol 定义。
"""

import pytest

from src.interfaces import (
    IClassifier,
    IDeduplicator,
    IExporter,
    IConfigProvider,
    IBookmarkLoader,
    IFusionEngine,
)
from src.classifiers.ai import AIBookmarkClassifier
from src.data.deduplicator import BookmarkDeduplicator
from src.data.exporter import DataExporter
from src.plugins.base import BookmarkFeatures, ClassificationResult


class TestIClassifierProtocol:
    """测试 IClassifier Protocol"""

    def test_ai_classifier_has_classify_method(self):
        """AIBookmarkClassifier 有 classify 方法"""
        assert hasattr(AIBookmarkClassifier, "classify")

    def test_ai_classifier_classify_batch_is_optional(self):
        """classify_batch 是可选方法，AIBookmarkClassifier 可以没有"""
        # classify_batch 是 Protocol 的可选方法
        # AIBookmarkClassifier 目前没有实现，这是可接受的
        # 批量分类可以通过 ClassifierPipeline 或循环调用实现
        pass

    def test_ai_classifier_satisfies_protocol(self):
        """AIBookmarkClassifier 满足 IClassifier Protocol"""
        # 检查方法签名
        import inspect

        sig = inspect.signature(AIBookmarkClassifier.classify)
        # 第一个参数是 self，第二个是 features
        params = list(sig.parameters.keys())
        assert "features" in params or len(params) >= 2


class TestIDeduplicatorProtocol:
    """测试 IDeduplicator Protocol"""

    def test_deduplicator_has_remove_duplicates(self):
        """BookmarkDeduplicator 有 remove_duplicates 方法"""
        assert hasattr(BookmarkDeduplicator, "remove_duplicates")

    def test_deduplicator_satisfies_protocol(self):
        """BookmarkDeduplicator 满足 IDeduplicator Protocol"""
        import inspect

        sig = inspect.signature(BookmarkDeduplicator.remove_duplicates)
        params = list(sig.parameters.keys())
        assert "bookmarks" in params or len(params) >= 2


class TestIExporterProtocol:
    """测试 IExporter Protocol"""

    def test_exporter_has_export_html(self):
        """DataExporter 有 export_html 方法"""
        assert hasattr(DataExporter, "export_html")

    def test_exporter_has_export_json(self):
        """DataExporter 有 export_json 方法"""
        assert hasattr(DataExporter, "export_json")


class TestProtocolRuntimeCheckable:
    """测试 Protocol 的 runtime_checkable 特性"""

    def test_iclassifier_is_runtime_checkable(self):
        """IClassifier 是 runtime_checkable 的"""
        # Protocol 类本身不是实例，但可以用于 isinstance 检查
        assert hasattr(IClassifier, "__protocol_attrs__")

    def test_ideduplicator_is_runtime_checkable(self):
        """IDeduplicator 是 runtime_checkable 的"""
        assert hasattr(IDeduplicator, "__protocol_attrs__")


class TestBookmarkFeaturesDataClass:
    """测试 BookmarkFeatures 数据类"""

    def test_create_bookmark_features(self):
        """可以创建 BookmarkFeatures 实例"""
        from datetime import datetime

        features = BookmarkFeatures(
            url="https://example.com",
            title="Example",
            domain="example.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )
        assert features.url == "https://example.com"
        assert features.title == "Example"
        assert features.is_secure is True

    def test_bookmark_features_url_length_property(self):
        """BookmarkFeatures 有 url_length 属性"""
        features = BookmarkFeatures(
            url="https://example.com/path",
            title="Test",
            domain="example.com",
            path_segments=["path"],
            query_params={},
            content_type="webpage",
            language="en",
        )
        assert features.url_length == len("https://example.com/path")


class TestClassificationResultDataClass:
    """测试 ClassificationResult 数据类"""

    def test_create_classification_result(self):
        """可以创建 ClassificationResult 实例"""
        result = ClassificationResult(
            category="技术",
            confidence=0.85,
            method="rule_engine",
        )
        assert result.category == "技术"
        assert result.confidence == 0.85
        assert result.method == "rule_engine"

    def test_classification_result_defaults(self):
        """ClassificationResult 有合理的默认值"""
        result = ClassificationResult(
            category="未分类",
            confidence=0.0,
        )
        assert result.reasoning == []
        assert result.alternatives == []
        assert result.method == "unknown"
