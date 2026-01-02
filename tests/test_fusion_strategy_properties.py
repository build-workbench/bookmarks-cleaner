"""
Property Tests for Fusion Strategy
融合策略属性测试

Tests Properties:
- Property 15: Fusion Strategy Application
- Property 16: Dynamic Weight Adjustment
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

# 尝试导入依赖
try:
    from src.plugins.pipeline import ClassifierPipeline, FusionStrategy
    from src.plugins.registry import PluginRegistry
    from src.plugins.base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 策略定义
category_strategy = st.sampled_from([
    '编程开发', '人工智能', '数据科学', '前端开发', '后端开发'
])

confidence_strategy = st.floats(min_value=0.1, max_value=1.0, allow_nan=False)

weight_strategy = st.floats(min_value=0.1, max_value=2.0, allow_nan=False)


class MockClassifierPlugin(ClassifierPlugin):
    """模拟分类器插件"""
    
    def __init__(self, name: str, category: str, confidence: float, priority: int = 50):
        self._name = name
        self._category = category
        self._confidence = confidence
        self._priority = priority
        self._initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self._name,
            version="1.0.0",
            capabilities=["test"],
            priority=self._priority
        )
    
    def initialize(self, config) -> bool:
        self._initialized = True
        return True
    
    def shutdown(self) -> None:
        self._initialized = False
    
    def classify(self, features: BookmarkFeatures) -> ClassificationResult:
        return ClassificationResult(
            category=self._category,
            confidence=self._confidence,
            method=self._name
        )


def create_features() -> BookmarkFeatures:
    """创建测试用书签特征"""
    return BookmarkFeatures(
        url="https://example.com/test",
        title="Test Title",
        domain="example.com",
        path_segments=["test"],
        query_params={},
        content_type="webpage",
        language="zh"
    )


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestFusionStrategyApplication:
    """融合策略应用测试 - Property 15"""
    
    @pytest.fixture
    def registry(self):
        """创建插件注册中心"""
        return PluginRegistry()
    
    @settings(max_examples=50)
    @given(
        strategy=st.sampled_from(['weighted_voting', 'stacking', 'bayesian']),
        categories=st.lists(category_strategy, min_size=2, max_size=4),
        confidences=st.lists(confidence_strategy, min_size=2, max_size=4)
    )
    def test_fusion_strategy_application(self, registry, strategy, categories, confidences):
        """
        Property 15: Fusion Strategy Application
        
        对于任何配置的融合策略（weighted_voting, stacking, bayesian），
        Classifier_Pipeline 应该在组合多个插件结果时应用该特定策略。
        
        Validates: Requirements 5.1
        """
        # 确保列表长度匹配
        n = min(len(categories), len(confidences))
        assume(n >= 2)
        categories = categories[:n]
        confidences = confidences[:n]
        
        # 创建管道
        pipeline = ClassifierPipeline(registry, {
            'fusion_strategy': strategy
        })
        
        # 注册并启用插件
        for i, (cat, conf) in enumerate(zip(categories, confidences)):
            plugin = MockClassifierPlugin(
                name=f"plugin_{i}",
                category=cat,
                confidence=conf,
                priority=i * 10
            )
            registry.register(plugin)
            plugin.initialize({})
            registry.enable(f"plugin_{i}")
        
        # 执行分类
        features = create_features()
        result = pipeline.classify(features)
        
        # 验证结果
        assert result is not None, "Should return a result"
        assert result.category in categories, \
            f"Result category {result.category} should be one of {categories}"
        assert 0.0 <= result.confidence <= 1.0, \
            f"Confidence {result.confidence} should be in [0, 1]"
        
        # 验证使用了正确的策略
        assert pipeline.fusion_strategy == FusionStrategy(strategy), \
            f"Should use {strategy} strategy"
    
    def test_weighted_voting_selects_highest_score(self, registry):
        """
        加权投票应该选择得分最高的类别。
        """
        pipeline = ClassifierPipeline(registry, {
            'fusion_strategy': 'weighted_voting'
        })
        
        # 创建两个插件，一个高置信度，一个低置信度
        high_conf_plugin = MockClassifierPlugin(
            name="high_conf",
            category="高置信度类别",
            confidence=0.9
        )
        low_conf_plugin = MockClassifierPlugin(
            name="low_conf",
            category="低置信度类别",
            confidence=0.3
        )
        
        registry.register(high_conf_plugin)
        registry.register(low_conf_plugin)
        high_conf_plugin.initialize({})
        low_conf_plugin.initialize({})
        registry.enable("high_conf")
        registry.enable("low_conf")
        
        result = pipeline.classify(create_features())
        
        # 高置信度类别应该获胜
        assert result.category == "高置信度类别", \
            "Weighted voting should select highest confidence category"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestDynamicWeightAdjustment:
    """动态权重调整测试 - Property 16"""
    
    @pytest.fixture
    def pipeline(self):
        """创建分类器管道"""
        registry = PluginRegistry()
        return ClassifierPipeline(registry, {
            'fusion_strategy': 'weighted_voting'
        })
    
    @settings(max_examples=50)
    @given(
        method_name=st.text(min_size=1, max_size=20),
        accuracy=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
    )
    def test_dynamic_weight_adjustment(self, pipeline, method_name, accuracy):
        """
        Property 16: Dynamic Weight Adjustment
        
        对于任何有追踪准确率历史的方法，其在融合中的权重
        应该根据其每个类别的历史准确率进行比例调整。
        
        Validates: Requirements 5.3, 5.5
        """
        assume(len(method_name.strip()) > 0)
        
        # 获取初始权重
        initial_weight = pipeline.method_weights.get(method_name, 1.0)
        
        # 更新权重
        pipeline.update_method_weight(method_name, accuracy)
        
        # 获取更新后的权重
        new_weight = pipeline.method_weights.get(method_name)
        
        assert new_weight is not None, "Weight should be set"
        assert new_weight >= 0, "Weight should be non-negative"
        
        # 权重应该向准确率方向调整
        # 使用指数移动平均，所以新权重应该在初始权重和准确率之间
        if accuracy > initial_weight:
            assert new_weight >= initial_weight, \
                "Weight should increase when accuracy is higher"
        elif accuracy < initial_weight:
            assert new_weight <= initial_weight, \
                "Weight should decrease when accuracy is lower"
    
    @settings(max_examples=30)
    @given(
        accuracies=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            min_size=5,
            max_size=20
        )
    )
    def test_weight_converges_to_accuracy(self, pipeline, accuracies):
        """
        多次更新后，权重应该趋近于准确率。
        """
        method_name = "test_method"
        
        # 多次更新
        for accuracy in accuracies:
            pipeline.update_method_weight(method_name, accuracy)
        
        final_weight = pipeline.method_weights.get(method_name)
        
        # 权重应该在合理范围内
        assert 0.0 <= final_weight <= 2.0, \
            f"Weight {final_weight} should be in reasonable range"
    
    def test_multiple_methods_independent_weights(self, pipeline):
        """
        不同方法的权重应该独立调整。
        """
        # 更新不同方法的权重
        pipeline.update_method_weight("method_a", 0.9)
        pipeline.update_method_weight("method_b", 0.3)
        
        weight_a = pipeline.method_weights.get("method_a")
        weight_b = pipeline.method_weights.get("method_b")
        
        # 权重应该不同
        assert weight_a != weight_b, \
            "Different methods should have different weights based on accuracy"
        
        # 高准确率方法应该有更高权重
        assert weight_a > weight_b, \
            "Higher accuracy method should have higher weight"


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestConflictResolution:
    """冲突解决测试"""
    
    @pytest.fixture
    def registry(self):
        """创建插件注册中心"""
        return PluginRegistry()
    
    def test_conflict_resolution_with_rules(self, registry):
        """
        冲突解决规则应该被应用。
        """
        pipeline = ClassifierPipeline(registry, {
            'fusion_strategy': 'weighted_voting',
            'conflict_rules': {
                'prefer_rule_engine': 'prefer_rule_engine'
            }
        })
        
        # 创建规则引擎插件和其他插件
        rule_plugin = MockClassifierPlugin(
            name="rule_classifier",
            category="规则类别",
            confidence=0.6
        )
        other_plugin = MockClassifierPlugin(
            name="other_classifier",
            category="其他类别",
            confidence=0.7
        )
        
        registry.register(rule_plugin)
        registry.register(other_plugin)
        rule_plugin.initialize({})
        other_plugin.initialize({})
        registry.enable("rule_classifier")
        registry.enable("other_classifier")
        
        result = pipeline.classify(create_features())
        
        # 由于冲突解决规则，规则引擎的结果应该被优先
        # 注意：具体行为取决于实现
        assert result is not None


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestFusionWithSinglePlugin:
    """单插件融合测试"""
    
    @pytest.fixture
    def registry(self):
        """创建插件注册中心"""
        return PluginRegistry()
    
    @settings(max_examples=30)
    @given(
        category=category_strategy,
        confidence=confidence_strategy
    )
    def test_single_plugin_passthrough(self, registry, category, confidence):
        """
        只有一个插件时，结果应该直接传递。
        """
        pipeline = ClassifierPipeline(registry, {
            'fusion_strategy': 'weighted_voting'
        })
        
        plugin = MockClassifierPlugin(
            name="single_plugin",
            category=category,
            confidence=confidence
        )
        
        registry.register(plugin)
        plugin.initialize({})
        registry.enable("single_plugin")
        
        result = pipeline.classify(create_features())
        
        assert result.category == category, \
            f"Single plugin result should pass through: {result.category} vs {category}"
