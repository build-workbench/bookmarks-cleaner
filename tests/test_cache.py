"""缓存管理器测试"""

from cleanbook.cache import CacheManager


class TestCacheManager:
    def test_put_get(self):
        cache = CacheManager(max_size=3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_miss(self):
        cache = CacheManager(max_size=3)
        assert cache.get("missing") is None

    def test_lru_eviction(self):
        cache = CacheManager(max_size=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # a is now recent
        cache.put("c", 3)  # b should be evicted
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_get_or_compute(self):
        cache = CacheManager(max_size=3)
        result = cache.get_or_compute("key", lambda: 42)
        assert result == 42
        # second call should hit cache
        result2 = cache.get_or_compute("key", lambda: 99)
        assert result2 == 42

    def test_invalidate(self):
        cache = CacheManager(max_size=3)
        cache.put("a", 1)
        assert cache.invalidate("a") is True
        assert cache.get("a") is None
        assert cache.invalidate("missing") is False

    def test_stats(self):
        cache = CacheManager(max_size=3)
        cache.put("a", 1)
        cache.get("a")
        cache.get("miss")
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
