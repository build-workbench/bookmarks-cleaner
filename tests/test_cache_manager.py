"""
CacheManager 单元测试

测试统一的缓存管理器功能。
"""

import pytest
from src.utils.cache_manager import CacheManager


class TestCacheManager:
    """CacheManager 测试套件"""
    
    def test_basic_put_get(self):
        """测试基本的存取操作"""
        cache = CacheManager[str](max_size=10)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        assert cache.get("nonexistent") is None
    
    def test_get_or_compute(self):
        """测试自动计算功能"""
        cache = CacheManager[int](max_size=10)
        call_count = [0]
        
        def factory():
            call_count[0] += 1
            return 42
        
        # 第一次调用应该执行 factory
        result1 = cache.get_or_compute("key1", factory)
        assert result1 == 42
        assert call_count[0] == 1
        
        # 第二次调用应该命中缓存，不执行 factory
        result2 = cache.get_or_compute("key1", factory)
        assert result2 == 42
        assert call_count[0] == 1  # 没有增加
    
    def test_lru_eviction(self):
        """测试 LRU 淘汰策略"""
        cache = CacheManager[int](max_size=3)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # 缓存已满，再添加应该淘汰最旧的 "a"
        cache.put("d", 4)
        
        assert cache.get("a") is None  # 被淘汰
        assert cache.get("b") == 2      # 保留
        assert cache.get("c") == 3      # 保留
        assert cache.get("d") == 4      # 新添加
    
    def test_lru_access_updates_order(self):
        """测试访问会更新 LRU 顺序"""
        cache = CacheManager[int](max_size=3)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # 访问 "a"，将其移到最近使用
        cache.get("a")
        
        # 添加新项，应该淘汰 "b"（最旧的）而不是 "a"
        cache.put("d", 4)
        
        assert cache.get("a") == 1      # 保留（被访问过）
        assert cache.get("b") is None   # 被淘汰
        assert cache.get("c") == 3      # 保留
        assert cache.get("d") == 4      # 新添加
    
    def test_invalidate(self):
        """测试失效单个缓存项"""
        cache = CacheManager[str](max_size=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        assert cache.invalidate("key1") is True
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        
        # 失效不存在的键应该返回 False
        assert cache.invalidate("nonexistent") is False
    
    def test_clear(self):
        """测试清空缓存"""
        cache = CacheManager[int](max_size=10)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        cache.clear()
        
        assert len(cache) == 0
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") is None
    
    def test_statistics(self):
        """测试缓存统计"""
        cache = CacheManager[int](max_size=3)
        
        # 初始状态
        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['size'] == 0
        assert stats['hit_rate'] == 0.0
        
        # 存入数据
        cache.put("a", 1)
        cache.put("b", 2)
        
        # 命中
        cache.get("a")
        cache.get("b")
        
        # 未命中
        cache.get("c")
        
        stats = cache.get_stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['size'] == 2
        assert stats['hit_rate'] == 2 / 3  # 2 hits / 3 requests
        
        # 触发淘汰
        cache.put("c", 3)
        cache.put("d", 4)  # 淘汰 "a"
        
        stats = cache.get_stats()
        assert stats['evictions'] == 1
    
    def test_contains_operator(self):
        """测试 in 操作符"""
        cache = CacheManager[int](max_size=10)
        
        cache.put("key1", 1)
        
        assert "key1" in cache
        assert "nonexistent" not in cache
    
    def test_len_operator(self):
        """测试 len() 操作符"""
        cache = CacheManager[int](max_size=10)
        
        assert len(cache) == 0
        
        cache.put("a", 1)
        assert len(cache) == 1
        
        cache.put("b", 2)
        assert len(cache) == 2
        
        cache.invalidate("a")
        assert len(cache) == 1
    
    def test_update_existing_key(self):
        """测试更新已存在的键"""
        cache = CacheManager[str](max_size=10)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # 更新值
        cache.put("key1", "value2")
        assert cache.get("key1") == "value2"
        assert len(cache) == 1  # 大小不变
    
    def test_thread_safety(self):
        """测试线程安全（基础测试）"""
        import threading
        
        cache = CacheManager[int](max_size=100, thread_safe=True)
        errors = []
        
        def worker(start: int):
            try:
                for i in range(start, start + 50):
                    cache.put(f"key{i}", i)
                    value = cache.get(f"key{i}")
                    assert value == i
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=worker, args=(i * 50,))
            for i in range(4)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
    
    def test_invalid_strategy(self):
        """测试不支持的淘汰策略"""
        with pytest.raises(ValueError, match="不支持的淘汰策略"):
            CacheManager[int](max_size=10, strategy='lfu')
    
    def test_repr(self):
        """测试字符串表示"""
        cache = CacheManager[int](max_size=100)
        cache.put("a", 1)
        cache.get("a")  # 命中一次
        
        repr_str = repr(cache)
        assert "CacheManager" in repr_str
        assert "max_size=100" in repr_str
        assert "size=1" in repr_str
        assert "100.00%" in repr_str  # 命中率 100%
