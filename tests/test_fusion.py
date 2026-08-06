"""融合引擎测试"""

from cleanbook.fusion import FusionEngine
from cleanbook.models import BookmarkFeatures, ClassificationResult


class TestFusionEngine:
    def test_empty_results(self):
        engine = FusionEngine()
        result = engine.fuse([])
        assert result.category == "未分类"
        assert result.method == "fallback"

    def test_single_result(self):
        engine = FusionEngine()
        r = ClassificationResult(category="编程", confidence=0.9, method="rule_engine")
        result = engine.fuse([r])
        assert result.category == "编程"
        assert result.confidence == 0.9

    def test_weighted_voting(self):
        engine = FusionEngine()
        r1 = ClassificationResult(category="编程", confidence=0.9, method="rule_engine")
        r2 = ClassificationResult(category="AI", confidence=0.5, method="llm")
        result = engine.fuse([r1, r2], confidence_threshold=0.3)
        assert result.category == "编程"

    def test_low_confidence_fallback(self):
        engine = FusionEngine()
        r = ClassificationResult(category="编程", confidence=0.1, method="rule_engine")
        result = engine.fuse([r], confidence_threshold=0.7)
        assert result.category == "未分类"

    def test_merge_facets(self):
        engine = FusionEngine()
        r1 = ClassificationResult(category="编程", confidence=0.9, method="rule_engine", facets={"resource_type_hint": "code_repository"})
        r2 = ClassificationResult(category="编程", confidence=0.8, method="llm", facets={"priority": "high"})
        result = engine.fuse([r1, r2])
        assert result.facets["resource_type_hint"] == "code_repository"
        assert result.facets["priority"] == "high"

    def test_update_weight(self):
        engine = FusionEngine()
        engine.update_weight("rule_engine", 0.9)
        assert engine.get_weights()["rule_engine"] == 0.9
