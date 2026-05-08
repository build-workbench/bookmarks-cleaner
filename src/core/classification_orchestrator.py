"""
Classification Orchestrator - 分类编排器

负责协调多个分类器的执行，融合结果，管理缓存。
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from src.classifiers.ai import AIBookmarkClassifier, ClassificationResult


class ClassificationOrchestrator:
    """分类编排器

    深度: 高（简单接口，复杂的分类管道编排）
    接口: classify(bookmarks) -> List[ClassifiedBookmark]
    """

    def __init__(
        self,
        classifier: AIBookmarkClassifier,
        max_workers: int = 4,
        use_cache: bool = True,
    ):
        self.classifier = classifier
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.logger = logging.getLogger(__name__)

        # 分类缓存
        self._cache: Dict[str, ClassificationResult] = {}
        self._cache_lock = None  # 延迟初始化

        # 统计信息
        self.stats = {
            "total_classified": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
        }

    def classify(
        self,
        bookmarks: List[Dict],
        confidence_threshold: Optional[float] = None,
    ) -> List[Dict]:
        """批量分类书签

        Args:
            bookmarks: 书签列表
            confidence_threshold: 置信度阈值

        Returns:
            分类后的书签列表
        """
        import threading

        if self._cache_lock is None:
            self._cache_lock = threading.Lock()

        classified = []
        total = len(bookmarks)

        self.logger.info(f"开始分类 {total} 个书签...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._classify_single, bookmark, confidence_threshold
                ): bookmark
                for bookmark in bookmarks
            }

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    result = future.result()
                    if result:
                        classified.append(result)

                    if i % 100 == 0:
                        self.logger.info(f"已分类 {i}/{total} 个书签")
                except Exception as e:
                    self.logger.error(f"分类失败: {e}")
                    self.stats["errors"] += 1

        self.stats["total_classified"] = len(classified)
        self.logger.info(
            f"分类完成: {len(classified)}/{total} 成功, "
            f"缓存命中率: {self._get_cache_hit_rate():.1%}"
        )

        return classified

    def _classify_single(
        self,
        bookmark: Dict,
        confidence_threshold: Optional[float],
    ) -> Optional[Dict]:
        """分类单个书签（带缓存）"""
        url = bookmark.get("url", "")
        title = bookmark.get("title", "")

        # 检查缓存
        if self.use_cache and url:
            cache_key = self._get_cache_key(url, title)
            with self._cache_lock:
                if cache_key in self._cache:
                    self.stats["cache_hits"] += 1
                    result = self._cache[cache_key]
                    return self._apply_result(bookmark, result, from_cache=True)

        self.stats["cache_misses"] += 1

        # 执行分类
        try:
            result = self.classifier.classify(url, title)
            if result:
                # 存入缓存
                if self.use_cache and url:
                    cache_key = self._get_cache_key(url, title)
                    with self._cache_lock:
                        self._cache[cache_key] = result

                return self._apply_result(bookmark, result, from_cache=False)
        except Exception as e:
            self.logger.debug(f"分类失败 [{url}]: {e}")

        return None

    def _apply_result(
        self,
        bookmark: Dict,
        result: ClassificationResult,
        from_cache: bool = False,
    ) -> Dict:
        """应用分类结果到书签"""
        classified = bookmark.copy()
        classified.update(
            {
                "category": result.category,
                "confidence": result.confidence,
                "subcategory": result.subcategory,
                "reasoning": result.reasoning,
                "method": result.method,
                "from_cache": from_cache,
                "classification_time": time.time(),
            }
        )
        return classified

    def _get_cache_key(self, url: str, title: str) -> str:
        """生成缓存键"""
        return f"{url}::{title}"

    def _get_cache_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.stats["cache_hits"] + self.stats["cache_misses"]
        if total == 0:
            return 0.0
        return self.stats["cache_hits"] / total

    def clear_cache(self):
        """清空分类缓存"""
        if self._cache_lock:
            with self._cache_lock:
                self._cache.clear()
        else:
            self._cache.clear()
        self.logger.info("分类缓存已清空")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            "cache_size": len(self._cache),
            "cache_hit_rate": self._get_cache_hit_rate(),
        }
