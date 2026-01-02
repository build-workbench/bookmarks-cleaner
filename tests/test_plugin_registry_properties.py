"""
Property-Based Tests for Plugin Registry
使用 Hypothesis 框架进行属性测试
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Import plugin system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plugins.base import ClassifierPlugin, PluginMetadata
from plugins.registry import PluginRegistry

# Mock BookmarkFeatures and ClassificationResult for testing
@dataclass
class MockBookmarkFeatures:
    url: str
    title: str
    domain: str

@dataclass
class MockClassificationResult:
    category: str
    confidence: float

# Mock plugin implementation
class MockPlugin(ClassifierPlugin):
    def __init__(self, name: str, version: str, priority: int = 100):
        self._metadata = PluginMetadata(
            name=name,
            version=version,
            capabilities=["classification"],
            priority=priority
        )
        self._initialized = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def classify(self, features) -> Optional[MockClassificationResult]:
        if not self._initialized:
            return None
        return MockClassificationResult(category="test", confidence=0.8)
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._initialized = True
        return True
    
    def shutdown(self) -> None:
        self._initialized = False

# Hypothesis strategies
plugin_name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'), 
    whitelist_characters='_-'
))

version_strategy = st.text(min_size=1, max_size=20, alphabet=st.characters(
    whitelist_categories=('Nd',),
    whitelist_characters='.'
))

priority_strategy = st.integers(min_value=0, max_value=1000)

# Property 1: Plugin Registration Consistency
@settings(max_examples=100)
@given(
    name=plugin_name_strategy,
    version=version_strategy,
    priority=priority_strategy
)
def test_property_1_plugin_registration_consistency(name, version, priority):
    """
    Feature: architecture-algorithm-upgrade
    Property 1: Plugin Registration Consistency
    
    For any valid plugin implementing the ClassifierPlugin interface,
    registering it with Plugin_Registry should succeed and the plugin
    should be retrievable with identical metadata.
    
    Validates: Requirements 1.1, 1.2
    """
    assume(len(name) > 0 and len(version) > 0)
    
    registry = PluginRegistry()
    plugin = MockPlugin(name, version, priority)
    
    # Register plugin
    result = registry.register(plugin)
    assert result is True, "Plugin registration should succeed"
    
    # Retrieve plugin
    retrieved = registry.get_plugin(name)
    assert retrieved is not None, "Registered plugin should be retrievable"
    
    # Verify metadata consistency
    assert retrieved.metadata.name == name
    assert retrieved.metadata.version == version
    assert retrieved.metadata.priority == priority

# Property 2: Plugin Invocation Order
@settings(max_examples=100)
@given(
    priorities=st.lists(
        st.integers(min_value=0, max_value=100),
        min_size=2,
        max_size=10,
        unique=False
    )
)
def test_property_2_plugin_invocation_order(priorities):
    """
    Feature: architecture-algorithm-upgrade
    Property 2: Plugin Invocation Order
    
    For any set of enabled plugins with configured priorities,
    when classifying a bookmark, the Classifier_Pipeline should
    invoke plugins in ascending priority order (lower number = higher priority).
    
    Validates: Requirements 1.4
    """
    registry = PluginRegistry()
    
    # Register and enable plugins with different priorities
    for i, priority in enumerate(priorities):
        plugin = MockPlugin(f"plugin_{i}", "1.0", priority)
        plugin.initialize({})
        registry.register(plugin)
        registry.enable(f"plugin_{i}")
    
    # Get enabled plugins
    enabled_plugins = registry.get_enabled_plugins()
    
    # Verify they are sorted by priority (ascending)
    plugin_priorities = [p.metadata.priority for p in enabled_plugins]
    assert plugin_priorities == sorted(plugin_priorities), \
        "Plugins should be ordered by ascending priority"

# Property 4: Runtime Plugin Toggle
@settings(max_examples=100)
@given(
    name=plugin_name_strategy,
    version=version_strategy
)
def test_property_4_runtime_plugin_toggle(name, version):
    """
    Feature: architecture-algorithm-upgrade
    Property 4: Runtime Plugin Toggle
    
    For any registered plugin, enabling or disabling it at runtime
    should take effect immediately without requiring system restart,
    and subsequent classifications should reflect the change.
    
    Validates: Requirements 1.6
    """
    assume(len(name) > 0 and len(version) > 0)
    
    registry = PluginRegistry()
    plugin = MockPlugin(name, version)
    plugin.initialize({})
    
    # Register plugin
    registry.register(plugin)
    
    # Initially not enabled
    assert not registry.is_enabled(name)
    assert len(registry.get_enabled_plugins()) == 0
    
    # Enable plugin
    result = registry.enable(name)
    assert result is True
    assert registry.is_enabled(name)
    assert len(registry.get_enabled_plugins()) == 1
    
    # Disable plugin
    result = registry.disable(name)
    assert result is True
    assert not registry.is_enabled(name)
    assert len(registry.get_enabled_plugins()) == 0
    
    # Re-enable plugin
    result = registry.enable(name)
    assert result is True
    assert registry.is_enabled(name)
    assert len(registry.get_enabled_plugins()) == 1

# Additional unit tests for edge cases
def test_plugin_registry_duplicate_registration():
    """Test that re-registering a plugin replaces the old one"""
    registry = PluginRegistry()
    
    plugin1 = MockPlugin("test", "1.0", priority=100)
    plugin2 = MockPlugin("test", "2.0", priority=50)
    
    registry.register(plugin1)
    registry.register(plugin2)
    
    retrieved = registry.get_plugin("test")
    assert retrieved.metadata.version == "2.0"
    assert retrieved.metadata.priority == 50

def test_plugin_registry_unregister_nonexistent():
    """Test unregistering a non-existent plugin"""
    registry = PluginRegistry()
    result = registry.unregister("nonexistent")
    assert result is False

def test_plugin_registry_enable_nonexistent():
    """Test enabling a non-existent plugin"""
    registry = PluginRegistry()
    result = registry.enable("nonexistent")
    assert result is False

def test_plugin_registry_listeners():
    """Test event listener functionality"""
    registry = PluginRegistry()
    events = []
    
    def listener(event, plugin_name):
        events.append((event, plugin_name))
    
    registry.add_listener(listener)
    
    plugin = MockPlugin("test", "1.0")
    registry.register(plugin)
    registry.enable("test")
    registry.disable("test")
    registry.unregister("test")
    
    assert len(events) == 4
    assert events[0] == ('registered', 'test')
    assert events[1] == ('enabled', 'test')
    assert events[2] == ('disabled', 'test')
    assert events[3] == ('unregistered', 'test')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
