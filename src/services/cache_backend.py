"""
Cache Backend - 缓存后端抽象

定义缓存后端的统一接口，支持多种实现。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import numpy as np


class CacheBackend(ABC):
    """缓存后端抽象接口

    深度: 高（统一接口，多种后端实现）
    接口: get/set/delete，支持 TTL
    """

    @abstractmethod
    def get(self, key: str) -> Optional[np.ndarray]:
        """获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存的特征向量，不存在或过期返回 None
        """
        pass

    @abstractmethod
    def set(
        self, key: str, value: np.ndarray, ttl_seconds: Optional[int] = None
    ) -> None:
        """设置缓存值

        Args:
            key: 缓存键
            value: 特征向量
            ttl_seconds: 过期时间（秒），None 表示永不过期
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存项

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空所有缓存"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息

        Returns:
            包含 hits, misses, size 等信息的字典
        """
        pass


class InMemoryCache(CacheBackend):
    """内存缓存实现

    实现 LRU 淘汰策略和 TTL 过期机制。
    深度: 高（简单接口，复杂的缓存逻辑）
    """

    def __init__(
        self,
        max_size: int = 100000,
        default_ttl: int = 86400 * 7,  # 7天
    ):
        from collections import OrderedDict
        import threading

        self.max_size = max_size
        self.default_ttl = default_ttl

        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._ttl: Dict[str, int] = {}
        self._lock = threading.RLock()

        # 统计
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[np.ndarray]:
        import time

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            # 检查 TTL
            timestamp = self._timestamps.get(key, 0)
            ttl = self._ttl.get(key, self.default_ttl)

            if time.time() - timestamp > ttl:
                self._evict(key)
                self._misses += 1
                return None

            # LRU: 移到末尾
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]

    def set(
        self, key: str, value: np.ndarray, ttl_seconds: Optional[int] = None
    ) -> None:
        import time

        with self._lock:
            value = np.asarray(value, dtype=np.float32)

            # LRU 驱逐
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                self._evict(oldest_key)

            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._ttl[key] = (
                ttl_seconds if ttl_seconds is not None else self.default_ttl
            )

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                self._evict(key)
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._ttl.clear()
            self._hits = 0
            self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "size": len(self._cache),
                "max_size": self.max_size,
            }

    def _evict(self, key: str) -> None:
        """驱逐缓存项"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._ttl.pop(key, None)
