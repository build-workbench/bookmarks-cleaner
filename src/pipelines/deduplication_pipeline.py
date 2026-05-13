"""
DeduplicationPipeline - 去重处理管道

编排快速 URL 去重和高级去重，提供统一的去重接口。

特性：
- 两阶段去重：快速 URL 去重 + 高级相似度去重
- 详细的去重统计
- 可配置的去重策略
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from src.data.deduplicator import BookmarkDeduplicator


class DeduplicationPipeline:
    """去重处理管道

    深度: 高（简单接口，复杂的两阶段去重逻辑）
    接口: deduplicate(bookmarks) -> (unique_bookmarks, duplicates, stats)

    示例:
        pipeline = DeduplicationPipeline()

        # 执行去重
        unique, duplicates, stats = pipeline.deduplicate(bookmarks)
        print(f"移除了 {stats['duplicates_removed']} 个重复书签")
    """

    def __init__(
        self,
        similarity_threshold: float = 0.85,
        enable_fast_dedup: bool = True,
        enable_advanced_dedup: bool = True,
    ):
        """初始化去重管道

        Args:
            similarity_threshold: 高级去重的相似度阈值
            enable_fast_dedup: 是否启用快速 URL 去重
            enable_advanced_dedup: 是否启用高级相似度去重
        """
        self.similarity_threshold = similarity_threshold
        self.enable_fast_dedup = enable_fast_dedup
        self.enable_advanced_dedup = enable_advanced_dedup
        self.logger = logging.getLogger(__name__)

        # 初始化高级去重器
        self._deduplicator: BookmarkDeduplicator = None

        # 统计信息
        self.stats = {
            "input_count": 0,
            "output_count": 0,
            "duplicates_removed": 0,
            "fast_duplicates_removed": 0,
            "advanced_duplicates_removed": 0,
        }

    @property
    def deduplicator(self) -> BookmarkDeduplicator:
        """延迟初始化高级去重器"""
        if self._deduplicator is None:
            self._deduplicator = BookmarkDeduplicator(
                similarity_threshold=self.similarity_threshold
            )
        return self._deduplicator

    def deduplicate(self, bookmarks: List[Dict]) -> Tuple[List[Dict], List[Dict], Dict]:
        """执行两阶段去重

        Args:
            bookmarks: 原始书签列表

        Returns:
            (unique_bookmarks, duplicates, stats) 元组
        """
        self._reset_stats()
        self.stats["input_count"] = len(bookmarks)

        if not bookmarks:
            return [], [], self.stats.copy()

        current_bookmarks = bookmarks
        all_duplicates: List[Dict] = []

        # 第一阶段：快速 URL 去重
        if self.enable_fast_dedup:
            current_bookmarks, fast_duplicates = self._fast_url_dedup(current_bookmarks)
            all_duplicates.extend(fast_duplicates)
            self.stats["fast_duplicates_removed"] = len(fast_duplicates)
            self.logger.info(f"快速去重移除了 {len(fast_duplicates)} 个重复书签")

        # 第二阶段：高级相似度去重
        if self.enable_advanced_dedup and current_bookmarks:
            current_bookmarks, advanced_duplicates = (
                self.deduplicator.remove_duplicates(current_bookmarks)
            )
            all_duplicates.extend(advanced_duplicates)
            self.stats["advanced_duplicates_removed"] = len(advanced_duplicates)
            self.logger.info(f"高级去重移除了 {len(advanced_duplicates)} 个重复书签")

        # 更新统计
        self.stats["output_count"] = len(current_bookmarks)
        self.stats["duplicates_removed"] = len(all_duplicates)

        return current_bookmarks, all_duplicates, self.stats.copy()

    def _fast_url_dedup(self, bookmarks: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """快速 URL 去重

        使用 URL 精确匹配进行快速去重，保留第一个出现的书签。

        Args:
            bookmarks: 书签列表

        Returns:
            (unique_bookmarks, duplicates) 元组
        """
        seen_urls = set()
        unique: List[Dict] = []
        duplicates: List[Dict] = []

        for bookmark in bookmarks:
            url = bookmark.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(bookmark)
            else:
                duplicates.append(bookmark)

        return unique, duplicates

    def _reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "input_count": 0,
            "output_count": 0,
            "duplicates_removed": 0,
            "fast_duplicates_removed": 0,
            "advanced_duplicates_removed": 0,
        }

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
