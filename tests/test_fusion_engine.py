"""
测试 FusionEngine 融合引擎
"""

import pytest

from src.services.fusion_engine import FusionEngine, get_default_fusion_engine
from src.plugins.base import ClassificationResult, BookmarkFeatures


class TestFusionEngine:
    """测试 FusionEngine"""

    @pytest.fixture
    def engine(self):
        """创建默认融合引擎"""
        return FusionEngine()

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

    def test_fuse_empty_results(self, engine, features):
        """空结果返回 fallback"""
        result = engine.fuse([], features)
        assert result.category == "未分类"
        assert result.confidence == 0.0
        assert result.method == "fallback"

    def test_fuse_single_result(self, engine, features):
        """单个结果直接返回"""
        single = ClassificationResult(
            category="技术",
            confidence=0.9,
            method="rule_engine",
        )
        result = engine.fuse([single], features)
        assert result.category == "技术"
        assert result.confidence == 0.9

    def test_fuse_multiple_results(self, engine, features):
        """多个结果加权融合"""
        results = [
            ClassificationResult(category="技术", confidence=0.9, method="rule_engine"),
            ClassificationResult(
                category="技术", confidence=0.7, method="machine_learning"
            ),
            ClassificationResult(
                category="科学", confidence=0.8, method="semantic_analyzer"
            ),
        ]
        result = engine.fuse(results, features)
        # rule_engine 权重最高 (0.5)，技术应该胜出
        assert result.category == "技术"
        assert result.confidence > 0

    def test_fuse_with_custom_weights(self, features):
        """自定义权重"""
        engine = FusionEngine(method_weights={"rule_engine": 0.1, "llm": 0.9})
        results = [
            ClassificationResult(category="技术", confidence=0.9, method="rule_engine"),
            ClassificationResult(category="科学", confidence=0.8, method="llm"),
        ]
        result = engine.fuse(results, features)
        # llm 权重高，科学应该胜出
        assert result.category == "科学"

    def test_fuse_below_threshold(self, engine, features):
        """低于阈值标记为未分类"""
        results = [
            ClassificationResult(category="技术", confidence=0.5, method="rule_engine"),
        ]
        result = engine.fuse(results, features, confidence_threshold=0.7)
        assert result.category == "未分类"
        assert "低于阈值" in result.reasoning[-1]

    def test_fuse_merges_facets(self, engine, features):
        """合并 facets"""
        results = [
            ClassificationResult(
                category="技术",
                confidence=0.9,
                method="rule_engine",
                facets={"domain": "github.com"},
            ),
            ClassificationResult(
                category="技术",
                confidence=0.8,
                method="ml",
                facets={"type": "repository"},
            ),
        ]
        result = engine.fuse(results, features)
        assert result.facets.get("domain") == "github.com"
        assert result.facets.get("type") == "repository"

    def test_fuse_with_category_normalizer(self, features):
        """使用分类名称标准化"""

        def normalizer(cat: str) -> str:
            return cat.lower().strip()

        engine = FusionEngine(category_normalizer=normalizer)
        results = [
            ClassificationResult(
                category="  技术  ", confidence=0.9, method="rule_engine"
            ),
        ]
        result = engine.fuse(results, features)
        assert result.category == "技术"

    def test_default_weights(self, engine):
        """默认权重包含所有方法"""
        weights = engine.get_weights()
        assert "rule_engine" in weights
        assert "machine_learning" in weights
        assert "semantic_analyzer" in weights
        assert "user_profiler" in weights
        assert "llm" in weights

    def test_update_weight(self, engine):
        """更新权重"""
        engine.update_weight("rule_engine", 0.8)
        assert engine.get_weights()["rule_engine"] == 0.8


class TestDefaultFusionEngine:
    """测试默认融合引擎单例"""

    def test_singleton(self):
        """单例模式"""
        engine1 = get_default_fusion_engine()
        engine2 = get_default_fusion_engine()
        assert engine1 is engine2


class TestFusionEngineIntegration:
    """FusionEngine 集成测试"""

    def test_ai_classifier_uses_fusion_engine(self):
        """AIBookmarkClassifier 使用 FusionEngine"""
        from src.classifiers.ai import AIBookmarkClassifier

        classifier = AIBookmarkClassifier.__new__(AIBookmarkClassifier)
        classifier._fusion_engine = None
        classifier._config = {"ai_settings": {}}
        classifier._confidence_calibrator = None

        # 获取融合引擎
        engine = classifier.fusion_engine
        assert engine is not None
        assert isinstance(engine, FusionEngine)

    def test_orchestrator_uses_fusion_engine(self):
        """ClassifierOrchestrator 使用 FusionEngine"""
        from src.classifiers.orchestrator import ClassifierOrchestrator

        orchestrator = ClassifierOrchestrator()
        assert orchestrator.fusion_engine is not None
        assert isinstance(orchestrator.fusion_engine, FusionEngine)

    def test_pipeline_uses_fusion_engine(self):
        """ClassifierPipeline 使用 FusionEngine"""
        from src.plugins.pipeline import ClassifierPipeline
        from src.plugins.registry import PluginRegistry

        pipeline = ClassifierPipeline(PluginRegistry(), {})
        assert pipeline.fusion_engine is not None
        assert isinstance(pipeline.fusion_engine, FusionEngine)
