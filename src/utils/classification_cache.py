"""
Classification Cache - 分类缓存统一接口

统一管理分类结果的缓存，解决以下问题：
1. 缓存键生成策略统一
2. 命中率统计集中管理
3. 多层缓存去重

深度: 高（简单接口，统一的缓存键策略和统计）
接口: get(url, title) -> Optional[ClassificationResult]
      put(url, title, result) -> None
      get_stats() -> Dict
"""

from __future__ import annotations

import hashlib
import logging
import threading
from typing import Dict, Optional, TYPE_CHECKING

from src.utils.cache_manager import CacheManager

if TYPE_CHECKING:
    from src.plugins.base import ClassificationResult


class ClassificationCache:
    """分类缓存统一接口

    统一管理分类结果的缓存，提供一致的缓存键生成策略。

    示例:
        cache = ClassificationCache(max_size=10000)

        # 缓存分类结果
        cache.put(url, title, result)

        # 获取缓存
        result = cache.get(url, title)

        # 获取统计
        stats = cache.get_stats()
        print(f"命中率: {stats['hit_rate']:.2%}")
    """

    # 默认缓存大小
    DEFAULT_SIZE = 10000

    def __init__(
        self,
        max_size: int = DEFAULT_SIZE,
        enable_stats: bool = True,
    ):
        """初始化分类缓存

        Args:
            max_size: 最大缓存项数量
            enable_stats: 是否启用统计
        """
        self._cache: CacheManager[Dict] = CacheManager(
            max_size=max_size, strategy="lru", thread_safe=True
        )
        self._enable_stats = enable_stats
        self._lock = threading.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
        }
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def generate_key(url: str, title: str) -> str:
        """生成统一的缓存键

        使用 SHA256 哈希确保键的一致性和固定长度。

        Args:
            url: 书签 URL
            title: 书签标题

        Returns:
            缓存键字符串
        """
        # 使用 :: 作为分隔符，避免与 URL 中的 | 冲突
        combined = f"{url}::{title}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]

    def get(self, url: str, title: str) -> Optional[Dict]:
        """获取缓存的分类结果

        Args:
            url: 书签 URL
            title: 书签标题

        Returns:
            缓存的分类结果字典，如果不存在返回 None
        """
        key = self.generate_key(url, title)

        if self._enable_stats:
            with self._lock:
                self._stats["total_requests"] += 1

        result = self._cache.get(key)

        if result is not None:
            if self._enable_stats:
                with self._lock:
                    self._stats["hits"] += 1
            return result

        if self._enable_stats:
            with self._lock:
                self._stats["misses"] += 1

        return None

    def put(self, url: str, title: str, result: Dict) -> None:
        """缓存分类结果

        Args:
            url: 书签 URL
            title: 书签标题
            result: 分类结果字典
        """
        key = self.generate_key(url, title)
        self._cache.put(key, result)

    def invalidate(self, url: str, title: str) -> bool:
        """使指定缓存项失效

        Args:
            url: 书签 URL
            title: 书签标题

        Returns:
            是否成功使缓存项失效
        """
        key = self.generate_key(url, title)
        # CacheManager 没有 invalidate 方法，使用 get + None 的方式
        # 这里我们假设 CacheManager 有 delete 方法，如果没有则需要添加
        # 暂时使用 put None 的方式
        try:
            self._cache.put(key, None)  # type: ignore
            return True
        except Exception:
            return False

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "total_requests": 0,
            }
        self.logger.info("分类缓存已清空")

    def get_stats(self) -> Dict:
        """获取缓存统计信息

        Returns:
            包含 hits, misses, hit_rate, size 等字段的统计字典
        """
        with self._lock:
            total = self._stats["total_requests"]
            hits = self._stats["hits"]
            hit_rate = hits / total if total > 0 else 0.0

        cache_stats = self._cache.get_stats()

        return {
            "hits": hits,
            "misses": self._stats["misses"],
            "total_requests": total,
            "hit_rate": hit_rate,
            "size": cache_stats.get("size", 0),
            "max_size": self._cache.max_size,
            "evictions": cache_stats.get("evictions", 0),
        }

    def get_hit_rate(self) -> float:
        """获取缓存命中率

        Returns:
            命中率 (0.0 - 1.0)
        """
        stats = self.get_stats()
        return stats["hit_rate"]

    @property
    def max_size(self) -> int:
        """最大缓存大小"""
        return self._cache.max_size
