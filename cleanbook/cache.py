"""线程安全的 LRU 缓存"""

from collections import OrderedDict
from typing import Callable, Generic, Hashable, Optional, TypeVar
import threading

T = TypeVar("T")


class CacheManager(Generic[T]):
    """LRU 缓存管理器"""

    def __init__(self, max_size: int = 1000, strategy: str = "lru", thread_safe: bool = True):
        if strategy != "lru":
            raise ValueError(f"不支持的淘汰策略: {strategy}，目前只支持 'lru'")
        self.max_size = max_size
        self.strategy = strategy
        self._cache: OrderedDict[Hashable, T] = OrderedDict()
        self._lock = threading.Lock() if thread_safe else None
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "put_count": 0, "get_count": 0}

    def get(self, key: Hashable) -> Optional[T]:
        if self._lock:
            with self._lock:
                return self._get_unsafe(key)
        return self._get_unsafe(key)

    def _get_unsafe(self, key: Hashable) -> Optional[T]:
        self._stats["get_count"] += 1
        if key in self._cache:
            self._cache.move_to_end(key)
            self._stats["hits"] += 1
            return self._cache[key]
        self._stats["misses"] += 1
        return None

    def get_or_compute(self, key: Hashable, factory: Callable[[], T]) -> T:
        if self._lock:
            with self._lock:
                value = self._get_unsafe(key)
                if value is not None:
                    return value
                value = factory()
                self._put_unsafe(key, value)
                return value
        value = self._get_unsafe(key)
        if value is not None:
            return value
        value = factory()
        self._put_unsafe(key, value)
        return value

    def put(self, key: Hashable, value: T) -> None:
        if self._lock:
            with self._lock:
                self._put_unsafe(key, value)
        else:
            self._put_unsafe(key, value)

    def _put_unsafe(self, key: Hashable, value: T) -> None:
        self._stats["put_count"] += 1
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = value
        else:
            self._cache[key] = value
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
                self._stats["evictions"] += 1

    def invalidate(self, key: Hashable) -> bool:
        if self._lock:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    return True
                return False
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        if self._lock:
            with self._lock:
                self._cache.clear()
        else:
            self._cache.clear()

    def get_stats(self) -> dict:
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        return {**self._stats, "size": len(self._cache), "max_size": self.max_size, "hit_rate": hit_rate}

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: Hashable) -> bool:
        if self._lock:
            with self._lock:
                return key in self._cache
        return key in self._cache
