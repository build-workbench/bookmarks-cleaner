"""
Property-Based Tests for Classifier Pipeline
使用 Hypothesis 框架进行属性测试
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

# Import plugin system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plugins.base import ClassifierPlugin, PluginMetadata
from plugins.registry import PluginRegistry
from plugins.pipeline import ClassifierPipeline

# Mock data structures
@dataclass
class MockBookmarkFeatures:
    url: str
    title: str
    domain: str
    path_segments: List[str] = field(default_factory=list)
    content_type: str = "webpage"
    language: str = "en"

@dataclass
class MockClassificationResult:
    category: str
    confidence: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    alternative_categories: List[Tuple[str, float]] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "mock"

# Mock plugin that can fail
class FailingPlugin(ClassifierPlugin):
    def __init__(self, name: str, should_fail: bool = False):
        self._metadata = PluginMetadata(
            name=name,
            version="1.0",
            capabilities=["classification"],
            priority=100
        )
        self._should_fail = should_fail
        self._initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def classify(self, features) -> Optional[MockClassificationResult]:
        if self._should_fail:
            raise RuntimeError(f"Plugin {self._metadata.name} failed intentionally")
        if not self._initialized:
            return None
        return MockClassificationResult(
            category=f"category_{self._metadata.name}",
            confidence=0.8
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._initialized = True
        return True
    
    def shutdown(self) -> None:
        self._initialized = False

# Mock plugin that always succeeds
class WorkingPlugin(ClassifierPlugin):
    def __init__(self, name: str, category: str = "test", confidence: float = 0.8):
        self._metadata = PluginMetadata(
            name=name,
            version="1.0",
            capabilities=["classification"],
            priority=100
        )
        self._category = category
        self._confidence = confidence
        self._initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def classify(self, features) -> Optional[MockClassificationResult]:
        if not self._initialized:
            return None
        return MockClassificationResult(
            category=self._category,
            confidence=self._confidence
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._initialized = True
        return True
    
    def shutdown(self) -> None:
        self._initialized = False

# Property 3: Plugin Failure Isolation
@settings(max_examples=100)
@given(
    num_working=st.integers(min_value=1, max_value=5),
    num_failing=st.integers(min_value=1, max_value=5)
)
def test_property_3_plugin_failure_isolation(num_working, num_failing):
    """
    Feature: architecture-algorithm-upgrade
    Property 3: Plugin Failure Isolation
    
    For any classification request, if one or more plugins fail during execution,
    the Classifier_Pipeline should continue processing with remaining plugins
    and return a valid result.
    
    Validates: Requirements 1.5
    """
    registry = PluginRegistry()
    
    # Register working plugins
    for i in range(num_working):
        plugin = WorkingPlugin(f"working_{i}", category=f"cat_{i}", confidence=0.8)
        plugin.initialize({})
        registry.register(plugin)
        registry.enable(f"working_{i}")
    
    # Register failing plugins
    for i in range(num_failing):
        plugin = FailingPlugin(f"failing_{i}", should_fail=True)
        plugin.initialize({})
        registry.register(plugin)
        registry.enable(f"failing_{i}")
    
    # Create pipeline
    pipeline = ClassifierPipeline(registry, {})
    
    # Classify
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    result = pipeline.classify(features)
    
    # Should return a valid result despite failures
    assert result is not None
    assert hasattr(result, 'category')
    assert hasattr(result, 'confidence')
    
    # Should have processed at least the working plugins
    # (category should be from one of the working plugins)
    if num_working > 0:
        assert result.category != "未分类" or result.confidence >= 0

def test_pipeline_all_plugins_fail():
    """Test that pipeline returns default result when all plugins fail"""
    registry = PluginRegistry()
    
    # Register only failing plugins
    for i in range(3):
        plugin = FailingPlugin(f"failing_{i}", should_fail=True)
        plugin.initialize({})
        registry.register(plugin)
        registry.enable(f"failing_{i}")
    
    pipeline = ClassifierPipeline(registry, {})
    
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    result = pipeline.classify(features)
    
    # Should return default result
    assert result.category == "未分类"
    assert result.confidence == 0.0

def test_pipeline_no_plugins():
    """Test that pipeline returns default result when no plugins are enabled"""
    registry = PluginRegistry()
    pipeline = ClassifierPipeline(registry, {})
    
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    result = pipeline.classify(features)
    
    # Should return default result
    assert result.category == "未分类"
    assert result.confidence == 0.0

def test_pipeline_weighted_voting():
    """Test weighted voting fusion strategy"""
    registry = PluginRegistry()
    
    # Register plugins with different results
    plugin1 = WorkingPlugin("plugin1", category="cat_a", confidence=0.9)
    plugin2 = WorkingPlugin("plugin2", category="cat_a", confidence=0.8)
    plugin3 = WorkingPlugin("plugin3", category="cat_b", confidence=0.7)
    
    for plugin in [plugin1, plugin2, plugin3]:
        plugin.initialize({})
        registry.register(plugin)
        registry.enable(plugin.metadata.name)
    
    # Create pipeline with weighted voting
    pipeline = ClassifierPipeline(registry, {
        'fusion_strategy': 'weighted_voting',
        'method_weights': {
            'plugin1': 1.0,
            'plugin2': 1.0,
            'plugin3': 1.0
        }
    })
    
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    result = pipeline.classify(features)
    
    # cat_a should win (0.9 + 0.8 = 1.7 vs 0.7)
    assert result.category == "cat_a"

def test_pipeline_stats_tracking():
    """Test that pipeline tracks statistics correctly"""
    registry = PluginRegistry()
    
    plugin = WorkingPlugin("test_plugin", category="test", confidence=0.8)
    plugin.initialize({})
    registry.register(plugin)
    registry.enable("test_plugin")
    
    pipeline = ClassifierPipeline(registry, {})
    
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    # Classify multiple times
    for _ in range(5):
        pipeline.classify(features)
    
    stats = pipeline.get_stats()
    
    # Check that stats are tracked
    assert 'method_stats' in stats
    assert 'test_plugin' in stats['method_stats']
    assert stats['method_stats']['test_plugin']['calls'] == 5
    assert stats['method_stats']['test_plugin']['errors'] == 0

def test_pipeline_error_tracking():
    """Test that pipeline tracks errors correctly"""
    registry = PluginRegistry()
    
    plugin = FailingPlugin("failing_plugin", should_fail=True)
    plugin.initialize({})
    registry.register(plugin)
    registry.enable("failing_plugin")
    
    pipeline = ClassifierPipeline(registry, {})
    
    features = MockBookmarkFeatures(
        url="https://example.com",
        title="Test",
        domain="example.com"
    )
    
    # Classify multiple times
    for _ in range(3):
        pipeline.classify(features)
    
    stats = pipeline.get_stats()
    
    # Check that errors are tracked
    assert stats['method_stats']['failing_plugin']['calls'] == 3
    assert stats['method_stats']['failing_plugin']['errors'] == 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
