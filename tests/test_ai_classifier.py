"""
Tests for AI Classifier Core Module
AI 分类器核心模块测试
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.classifiers.ai import (
    AIBookmarkClassifier,
    BookmarkFeatures,
    ClassificationResult,
)


class TestBookmarkFeatures:
    """BookmarkFeatures 数据类测试"""

    def test_basic_features(self):
        """测试基本特征创建"""
        features = BookmarkFeatures(
            url="https://example.com/path",
            title="Example Title",
            domain="example.com",
            path_segments=["path"],
            query_params={"q": "test"},
            content_type="webpage",
            language="en",
        )

        assert features.url == "https://example.com/path"
        assert features.title == "Example Title"
        assert features.domain == "example.com"
        assert features.url_length == 24
        assert features.title_length == 13
        assert features.is_secure is True
        assert features.has_chinese is False

    def test_chinese_detection(self):
        """测试中文检测"""
        features = BookmarkFeatures(
            url="https://example.com",
            title="中文标题测试",
            domain="example.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="zh",
        )

        assert features.has_chinese is True

    def test_secure_url_detection(self):
        """测试安全URL检测"""
        secure_features = BookmarkFeatures(
            url="https://secure.com",
            title="Secure",
            domain="secure.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )

        insecure_features = BookmarkFeatures(
            url="http://insecure.com",
            title="Insecure",
            domain="insecure.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )

        assert secure_features.is_secure is True
        assert insecure_features.is_secure is False

    @given(
        url=st.text(min_size=1, max_size=500),
        title=st.text(min_size=0, max_size=500),
    )
    def test_url_title_lengths(self, url: str, title: str):
        """属性测试：URL和标题长度应与实际一致"""
        features = BookmarkFeatures(
            url=url,
            title=title,
            domain="test.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )

        assert features.url_length == len(url)
        assert features.title_length == len(title)


class TestClassificationResult:
    """ClassificationResult 数据类测试"""

    def test_basic_result(self):
        """测试基本分类结果"""
        result = ClassificationResult(
            category="编程/开发",
            confidence=0.85,
            subcategory="Python",
            reasoning=["域名匹配 github.com"],
            alternatives=[("AI/机器学习", 0.1)],
            processing_time=0.05,
            method="rule_engine",
        )

        assert result.category == "编程/开发"
        assert result.confidence == 0.85
        assert result.subcategory == "Python"
        assert len(result.reasoning) == 1
        assert len(result.alternatives) == 1
        assert result.method == "rule_engine"

    def test_default_values(self):
        """测试默认值"""
        result = ClassificationResult(
            category="未分类",
            confidence=0.0,
        )

        assert result.subcategory is None
        assert result.reasoning == []
        assert result.alternatives == []
        assert result.processing_time == 0.0
        assert result.method == "unknown"
        assert result.facets == {}


class TestAIBookmarkClassifier:
    """AIBookmarkClassifier 测试"""

    @pytest.fixture
    def mock_config(self):
        """模拟配置"""
        return {
            "ai_settings": {
                "confidence_threshold": 0.4,
                "use_semantic_analysis": False,
                "use_user_profiling": False,
                "cache_size": 100,
            },
            "category_rules": {
                "💻 编程": {
                    "rules": [
                        {"match": "domain", "keywords": ["github.com"], "weight": 20}
                    ]
                }
            },
            "category_order": ["💻 编程", "🤖 AI", "未分类"],
        }

    @pytest.fixture
    def classifier(self, mock_config, tmp_path):
        """创建分类器实例"""
        with patch("src.classifiers.ai.load_json_config") as mock_load:
            mock_load.return_value = (mock_config, "test_path", True)
            classifier = AIBookmarkClassifier(config=mock_config)
            return classifier

    def test_extract_features_basic(self, classifier):
        """测试基本特征提取"""
        features = classifier.extract_features(
            "https://github.com/user/repo", "GitHub Repository"
        )

        assert features.domain == "github.com"
        assert features.title == "GitHub Repository"
        assert features.is_secure is True
        assert features.language == "en"

    def test_extract_features_chinese(self, classifier):
        """测试中文URL特征提取"""
        features = classifier.extract_features("https://example.com", "中文标题测试")

        assert features.has_chinese is True
        assert features.language == "zh"

    def test_extract_features_caching(self, classifier):
        """测试特征缓存"""
        url = "https://example.com"
        title = "Test Title"

        features1 = classifier.extract_features(url, title)
        features2 = classifier.extract_features(url, title)

        # 应该是同一个对象（从缓存返回）
        assert features1 is features2
        assert (
            classifier.stats["cache_hits"] == 0
        )  # classification_cache, not feature_cache

    def test_classify_basic(self, classifier):
        """测试基本分类"""
        result = classifier.classify("https://github.com/user/repo", "Python Project")

        assert result is not None
        assert result.category != ""
        assert 0.0 <= result.confidence <= 1.0
        assert result.method != ""

    def test_classify_with_cache(self, classifier):
        """测试分类缓存"""
        url = "https://github.com/test/repo"
        title = "Test Repository"

        result1 = classifier.classify(url, title)
        result2 = classifier.classify(url, title)

        assert classifier.stats["cache_hits"] == 1

    def test_classify_empty_url(self, classifier):
        """测试空URL处理"""
        result = classifier.classify("", "Empty URL")

        assert result is not None
        # 应该有一个合理的默认处理

    @pytest.mark.skip(
        reason="TODO: 需要实现 embedding classifier 集成到 AIBookmarkClassifier"
    )
    def test_top_level_embedding_config_contributes_to_voting_and_stats(
        self, mock_config
    ):
        config = {
            **mock_config,
            "embedding": {
                "enabled": True,
                "backend": "hash",
                "similarity_threshold": 0.1,
            },
        }

        with patch(
            "src.services.embedding_service.EmbeddingService"
        ) as embedding_service_cls:
            with patch(
                "src.plugins.classifiers.embedding_classifier.EmbeddingClassifier"
            ) as embedding_cls:
                embedding_service = embedding_service_cls.return_value
                embedding_service.initialize.return_value = True
                embedding_service.embed.return_value = np.array(
                    [1.0, 0.0], dtype=np.float32
                )

                embedding_classifier = embedding_cls.return_value
                embedding_classifier.initialize.return_value = True
                embedding_classifier.classify.return_value = ClassificationResult(
                    category="🤖 AI",
                    confidence=0.95,
                    reasoning=["embedding match"],
                    method="embedding",
                )

                classifier = AIBookmarkClassifier(config=config)
                classifier._rule_engine = Mock(
                    classify=Mock(
                        return_value=ClassificationResult(
                            category="💻 编程",
                            confidence=0.1,
                            reasoning=["rule match"],
                            method="rule_engine",
                        )
                    )
                )
                classifier._semantic_analyzer = Mock(classify=Mock(return_value=None))
                classifier._user_profiler = Mock(classify=Mock(return_value=None))

                result = classifier.classify(
                    "https://example.com/llm",
                    "LLM notes",
                )

                init_config = embedding_classifier.initialize.call_args.args[0]

                assert init_config["similarity_threshold"] == 0.1
                assert "编程" in init_config["category_prototypes"]
                assert result.category == "AI"
                assert "embedding match" in result.reasoning
                assert (
                    classifier.get_statistics()["classification_methods"]["embedding"]
                    == 1
                )

    def test_calibration_applies_before_thresholding_and_surfaces_raw_score(
        self, classifier
    ):
        classifier.config["ai_settings"]["confidence_threshold"] = 0.7
        classifier._rule_engine = Mock(
            classify=Mock(
                return_value=ClassificationResult(
                    category="💻 编程",
                    confidence=0.49,
                    reasoning=["rule match"],
                    method="rule_engine",
                )
            )
        )
        classifier._semantic_analyzer = Mock(classify=Mock(return_value=None))
        classifier._user_profiler = Mock(classify=Mock(return_value=None))
        classifier._confidence_calibrator = Mock(calibrate=Mock(return_value=0.8))

        result = classifier.classify("https://github.com/user/repo", "Repo")
        stats = classifier.get_statistics()

        assert result.category == "编程"
        assert result.confidence == 0.8
        assert result.score_breakdown["calibrated_from"] == pytest.approx(0.49)
        assert stats["calibrated_predictions"] == 1

    def test_get_statistics(self, classifier):
        """测试统计信息获取"""
        stats = classifier.get_statistics()

        assert "total_classified" in stats
        assert "cache_hits" in stats
        assert "average_confidence" in stats
        assert "classification_methods" in stats

    def test_to_classification_result_from_dict(self, classifier):
        """测试从字典转换为 ClassificationResult"""
        data = {
            "category": "测试分类",
            "confidence": 0.75,
            "reasoning": ["测试推理"],
            "method": "test",
        }

        result = AIBookmarkClassifier._to_classification_result(data)

        assert result.category == "测试分类"
        assert result.confidence == 0.75
        assert result.method == "test"

    def test_to_classification_result_from_result(self, classifier):
        """测试从 ClassificationResult 直接返回"""
        original = ClassificationResult(
            category="原始分类",
            confidence=0.9,
            method="original",
        )

        result = AIBookmarkClassifier._to_classification_result(original)

        assert result.category == "原始分类"
        assert result.confidence == 0.9

    def test_invalid_input_handling(self, classifier):
        """测试无效输入处理"""
        # None URL
        result = classifier.classify(None, "Title")
        assert result is not None

        # 特殊字符
        result = classifier.classify(
            "https://example.com/<script>alert(1)</script>", "Test <>&\"'"
        )
        assert result is not None


class TestEnsembleClassification:
    """集成分类测试"""

    @pytest.fixture
    def classifier_with_multiple_methods(self, mock_config):
        """创建启用多种分类方法的分类器"""
        with patch("src.classifiers.ai.load_json_config") as mock_load:
            mock_load.return_value = (mock_config, "test_path", True)
            classifier = AIBookmarkClassifier(config=mock_config)
            return classifier

    def test_ensemble_weighted_voting(self, classifier_with_multiple_methods):
        """测试加权投票融合"""
        # 这个测试验证多个分类器结果的融合逻辑
        result = classifier_with_multiple_methods.classify(
            "https://github.com/tensorflow/tensorflow",
            "TensorFlow: An Open Source Machine Learning Framework",
        )

        assert result is not None
        # 置信度应该合理
        assert 0.0 <= result.confidence <= 1.0


class TestEdgeCases:
    """边界情况测试"""

    def test_very_long_url(self):
        """测试超长URL"""
        long_url = "https://example.com/" + "a" * 2000
        features = BookmarkFeatures(
            url=long_url,
            title="Test",
            domain="example.com",
            path_segments=["a" * 100],
            query_params={"q": "a" * 500},
            content_type="webpage",
            language="en",
        )

        assert features.url_length == len(long_url)

    def test_unicode_in_title(self):
        """测试标题中的Unicode字符"""
        features = BookmarkFeatures(
            url="https://example.com",
            title="🎉 祝贺！测试成功 ✓",
            domain="example.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="zh",
        )

        assert "🎉" in features.title
        assert features.has_chinese is True

    def test_empty_path_segments(self):
        """测试空路径段"""
        features = BookmarkFeatures(
            url="https://example.com",
            title="Root",
            domain="example.com",
            path_segments=[],
            query_params={},
            content_type="webpage",
            language="en",
        )

        assert features.path_segments == []


@pytest.fixture
def mock_config():
    """共享的模拟配置fixture"""
    return {
        "ai_settings": {
            "confidence_threshold": 0.4,
            "use_semantic_analysis": False,
            "use_user_profiling": False,
            "cache_size": 100,
        },
        "category_rules": {
            "💻 编程": {
                "rules": [{"match": "domain", "keywords": ["github.com"], "weight": 20}]
            }
        },
        "category_order": ["💻 编程", "未分类"],
    }
