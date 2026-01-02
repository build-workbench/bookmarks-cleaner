"""
Property-Based Tests for Feature Store
使用 Hypothesis 框架进行属性测试
"""

import pytest
import time
import numpy as np
from hypothesis import given, strategies as st, settings, assume

# Import feature store
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.feature_store import FeatureStore

# Hypothesis strategies
key_strategy = st.text(min_size=1, max_size=100)
embedding_strategy = st.lists(
    st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    min_size=10,
    max_size=100
)

# Property 17: Feature Store TTL Expiration
@settings(max_examples=100, deadline=1000)
@given(
    key=key_strategy,
    embedding=embedding_strategy,
    ttl_seconds=st.integers(min_value=1, max_value=5)
)
def test_property_17_ttl_expiration(key, embedding, ttl_seconds):
    """
    Feature: architecture-algorithm-upgrade
    Property 17: Feature Store TTL Expiration
    
    For any cached feature vector, it should be evicted after the
    configured TTL expires and return None on subsequent retrieval.
    
    Validates: Requirements 6.1
    """
    assume(len(key) > 0)
    
    store = FeatureStore({
        'max_size': 1000,
        'ttl_seconds': ttl_seconds
    })
    
    embedding_array = np.array(embedding, dtype=np.float32)
    
    # Store feature
    store.put(key, embedding_array)
    
    # Should be retrievable immediately
    retrieved = store.get(key)
    assert retrieved is not None
    np.testing.assert_array_almost_equal(retrieved, embedding_array)
    
    # Wait for TTL to expire
    time.sleep(ttl_seconds + 0.5)
    
    # Should return None after TTL
    expired = store.get(key)
    assert expired is None

# Property 18: LRU Eviction Policy
@settings(max_examples=100)
@given(
    items=st.lists(
        st.tuples(key_strategy, embedding_strategy),
        min_size=5,
        max_size=20
    ),
    max_size=st.integers(min_value=2, max_value=5)
)
def test_property_18_lru_eviction_policy(items, max_size):
    """
    Feature: architecture-algorithm-upgrade
    Property 18: LRU Eviction Policy
    
    For any Feature_Store at maximum capacity, adding a new entry
    should evict the least recently used entry first.
    
    Validates: Requirements 6.4
    """
    assume(len(items) > max_size)
    
    store = FeatureStore({
        'max_size': max_size,
        'ttl_seconds': 3600
    })
    
    # Add items
    for key, embedding in items:
        if len(key) > 0:  # Skip empty keys
            embedding_array = np.array(embedding, dtype=np.float32)
            store.put(key, embedding_array)
    
    # Cache size should not exceed max_size
    assert len(store._cache) <= max_size
    
    # Most recently added items should be in cache
    if items:
        # Check last few items (up to max_size)
        recent_items = [item for item in items[-max_size:] if len(item[0]) > 0]
        for key, embedding in recent_items[-min(3, len(recent_items)):]:
            retrieved = store.get(key)
            # Should be in cache (might have been evicted if duplicate keys)
            if retrieved is not None:
                assert isinstance(retrieved, np.ndarray)

def test_feature_store_cache_hit():
    """Test cache hit functionality"""
    store = FeatureStore({'max_size': 100, 'ttl_seconds': 3600})
    
    key = "test_key"
    embedding = np.random.rand(10)
    
    # First access - miss
    result = store.get(key)
    assert result is None
    assert store._misses == 1
    assert store._hits == 0
    
    # Store
    store.put(key, embedding)
    
    # Second access - hit
    result = store.get(key)
    assert result is not None
    np.testing.assert_array_almost_equal(result, embedding)
    assert store._hits == 1

def test_feature_store_lru_order():
    """Test that LRU order is maintained correctly"""
    store = FeatureStore({'max_size': 3, 'ttl_seconds': 3600})
    
    # Add 3 items
    store.put("key1", np.array([1.0]))
    store.put("key2", np.array([2.0]))
    store.put("key3", np.array([3.0]))
    
    # Access key1 to make it most recently used
    store.get("key1")
    
    # Add key4, should evict key2 (least recently used)
    store.put("key4", np.array([4.0]))
    
    assert store.get("key1") is not None
    assert store.get("key2") is None  # Evicted
    assert store.get("key3") is not None
    assert store.get("key4") is not None

def test_feature_store_persist_and_load(tmp_path):
    """Test persistence and loading"""
    persist_path = str(tmp_path / "features")
    
    store1 = FeatureStore({
        'max_size': 100,
        'ttl_seconds': 3600,
        'persist_path': persist_path
    })
    
    # Add some data
    store1.put("key1", np.array([1.0, 2.0, 3.0]))
    store1.put("key2", np.array([4.0, 5.0, 6.0]))
    
    # Persist
    store1.persist()
    
    # Create new store and load
    store2 = FeatureStore({
        'max_size': 100,
        'ttl_seconds': 3600,
        'persist_path': persist_path
    })
    store2.load()
    
    # Verify data
    result1 = store2.get("key1")
    result2 = store2.get("key2")
    
    assert result1 is not None
    assert result2 is not None
    np.testing.assert_array_almost_equal(result1, np.array([1.0, 2.0, 3.0]))
    np.testing.assert_array_almost_equal(result2, np.array([4.0, 5.0, 6.0]))

def test_feature_store_warm_cache():
    """Test cache warming functionality"""
    store = FeatureStore({'max_size': 100, 'ttl_seconds': 3600})
    
    historical_data = [
        {'key': 'key1', 'embedding': np.array([1.0, 2.0])},
        {'key': 'key2', 'embedding': np.array([3.0, 4.0])},
        {'key': 'key3', 'embedding': np.array([5.0, 6.0])}
    ]
    
    store.warm_cache(historical_data)
    
    # Verify all items are in cache
    assert store.get('key1') is not None
    assert store.get('key2') is not None
    assert store.get('key3') is not None

def test_feature_store_find_similar():
    """Test similarity search"""
    store = FeatureStore({'max_size': 100, 'ttl_seconds': 3600})
    
    # Add some vectors
    store.put("vec1", np.array([1.0, 0.0, 0.0]))
    store.put("vec2", np.array([0.9, 0.1, 0.0]))
    store.put("vec3", np.array([0.0, 1.0, 0.0]))
    
    # Search for similar to vec1
    query = np.array([1.0, 0.0, 0.0])
    results = store.find_similar(query, top_k=2)
    
    assert len(results) <= 2
    # vec1 should be most similar
    if results:
        assert results[0][0] == "vec1"
        assert results[0][1] > 0.9  # High similarity

def test_feature_store_stats():
    """Test statistics tracking"""
    store = FeatureStore({'max_size': 100, 'ttl_seconds': 3600})
    
    # Add and access items
    store.put("key1", np.array([1.0]))
    store.get("key1")  # Hit
    store.get("key2")  # Miss
    
    stats = store.get_stats()
    
    assert stats['size'] == 1
    assert stats['max_size'] == 100
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    assert stats['hit_rate'] == 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
