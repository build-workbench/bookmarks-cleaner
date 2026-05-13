"""
CacheManager - 统一的缓存管理器

提供线程安全的 LRU 缓存实现，支持统计、淘汰策略等功能。
用于替换分散在多个模块中的缓存实现。
"""

from collections import OrderedDict
from typing import Callable, Generic, Hashable, Optional, TypeVar
import threading

T = TypeVar("T")


class CacheManager(Generic[T]):
    """统一的缓存管理器，支持 LRU 淘汰策略

    特性：
    - 线程安全
    - LRU 淘汰策略
    - 缓存统计（命中率、大小等）
    - 支持缓存未命中时自动计算

    示例：
        cache = CacheManager[str](max_size=1000)

        # 直接存取
        cache.put("key1", "value1")
        value = cache.get("key1")

        # 自动计算
        value = cache.get_or_compute("key2", lambda: expensive_computation())

        # 统计
        stats = cache.get_stats()
        print(f"命中率: {stats['hit_rate']:.2%}")
    """

    def __init__(
        self, max_size: int = 1000, strategy: str = "lru", thread_safe: bool = True
    ):
        """初始化缓存管理器

        Args:
            max_size: 最大缓存项数量
            strategy: 淘汰策略（目前只支持 'lru'）
            thread_safe: 是否启用线程安全
        """
        if strategy != "lru":
            raise ValueError(f"不支持的淘汰策略: {strategy}，目前只支持 'lru'")

        self.max_size = max_size
        self.strategy = strategy
        self._cache: OrderedDict[Hashable, T] = OrderedDict()
        self._lock = threading.Lock() if thread_safe else None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "put_count": 0,
            "get_count": 0,
        }

    def get(self, key: Hashable) -> Optional[T]:
        """获取缓存项

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在返回 None
        """
        if self._lock:
            with self._lock:
                return self._get_unsafe(key)
        return self._get_unsafe(key)

    def _get_unsafe(self, key: Hashable) -> Optional[T]:
        """非线程安全的获取（内部使用）"""
        self._stats["get_count"] += 1

        if key in self._cache:
            # LRU: 移到末尾表示最近使用
            self._cache.move_to_end(key)
            self._stats["hits"] += 1
            return self._cache[key]

        self._stats["misses"] += 1
        return None

    def get_or_compute(self, key: Hashable, factory: Callable[[], T]) -> T:
        """获取缓存项，若不存在则计算并缓存

        Args:
            key: 缓存键
            factory: 计算函数（在缓存未命中时调用）

        Returns:
            缓存值或计算结果
        """
        if self._lock:
            with self._lock:
                value = self._get_unsafe(key)
                if value is not None:
                    return value

                value = factory()
                self._put_unsafe(key, value)
                return value
        else:
            value = self._get_unsafe(key)
            if value is not None:
                return value

            value = factory()
            self._put_unsafe(key, value)
            return value

    def put(self, key: Hashable, value: T) -> None:
        """存入缓存项

        Args:
            key: 缓存键
            value: 缓存值
        """
        if self._lock:
            with self._lock:
                self._put_unsafe(key, value)
        else:
            self._put_unsafe(key, value)

    def _put_unsafe(self, key: Hashable, value: T) -> None:
        """非线程安全的存入（内部使用）"""
        self._stats["put_count"] += 1

        if key in self._cache:
            # 更新已存在的键
            self._cache.move_to_end(key)
            self._cache[key] = value
        else:
            # 添加新键
            self._cache[key] = value

            # 检查是否需要淘汰
            if len(self._cache) > self.max_size:
                # LRU: 删除最旧的项（第一个）
                self._cache.popitem(last=False)
                self._stats["evictions"] += 1

    def invalidate(self, key: Hashable) -> bool:
        """失效单个缓存项

        Args:
            key: 缓存键

        Returns:
            是否成功失效（True 表示键存在并已删除）
        """
        if self._lock:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    return True
                return False
        else:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空缓存"""
        if self._lock:
            with self._lock:
                self._cache.clear()
        else:
            self._cache.clear()

    def get_stats(self) -> dict:
        """获取缓存统计

        Returns:
            包含以下字段的字典：
            - hits: 缓存命中次数
            - misses: 缓存未命中次数
            - evictions: 淘汰次数
            - size: 当前缓存大小
            - max_size: 最大缓存大小
            - hit_rate: 缓存命中率（0.0-1.0）
            - put_count: put 操作次数
            - get_count: get 操作次数
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            **self._stats,
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": hit_rate,
        }

    def __len__(self) -> int:
        """返回当前缓存大小"""
        return len(self._cache)

    def __contains__(self, key: Hashable) -> bool:
        """检查键是否在缓存中"""
        if self._lock:
            with self._lock:
                return key in self._cache
        return key in self._cache

    def __repr__(self) -> str:
        return (
            f"CacheManager(max_size={self.max_size}, "
            f"size={len(self._cache)}, "
            f"hit_rate={self.get_stats()['hit_rate']:.2%})"
        )
