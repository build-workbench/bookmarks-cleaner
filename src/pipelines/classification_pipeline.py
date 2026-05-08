"""
ClassificationPipeline - 分类处理管道

统一特征提取、分类、缓存和反馈学习。

特性：
- 并行分类处理
- 分类结果缓存
- ML 模型训练
- 详细的分类统计
"""

from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

from src.classifiers.ai import AIBookmarkClassifier
from src.utils.cache_manager import CacheManager
from src.utils.category import normalize_category_string


class ClassificationPipeline:
    """分类处理管道
    
    深度: 高（简单接口，复杂的并行分类和缓存逻辑）
    接口: classify_batch(bookmarks) -> (classified_bookmarks, stats)
    
    示例:
        pipeline = ClassificationPipeline(config, classifier)
        
        # 批量分类
        classified, stats = pipeline.classify_batch(bookmarks)
        print(f"分类了 {stats['classified_count']} 个书签")
    """
    
    def __init__(
        self,
        config: Dict,
        classifier: AIBookmarkClassifier,
        max_workers: int = 4,
        confidence_threshold: Optional[float] = None,
        cache_size: int = 10000,
    ):
        """初始化分类管道
        
        Args:
            config: 配置字典
            classifier: AI 分类器实例
            max_workers: 并行分类的最大线程数
            confidence_threshold: 置信度阈值
            cache_size: 分类缓存大小
        """
        self.config = config
        self.classifier = classifier
        self.max_workers = max_workers
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # 分类缓存
        self._classification_cache: CacheManager[Dict] = CacheManager(
            max_size=cache_size,
            strategy='lru',
            thread_safe=True
        )
        
        # 线程锁用于统计更新
        self._stats_lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            "classified_count": 0,
            "cache_hits": 0,
            "errors": 0,
            "processing_time": 0.0,
            "categories_found": {},
        }
    
    def classify_batch(
        self,
        bookmarks: List[Dict],
        batch_size: int = 100
    ) -> Tuple[List[Dict], Dict]:
        """批量分类书签
        
        Args:
            bookmarks: 书签字典列表
            batch_size: 批处理大小
            
        Returns:
            (classified_bookmarks, stats) 元组
        """
        self._reset_stats()
        
        if not bookmarks:
            return [], self.stats.copy()
        
        classified_bookmarks: List[Dict] = []
        import time
        start_time = time.time()
        
        # 复用同一个线程池
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(0, len(bookmarks), batch_size):
                batch = bookmarks[i:i + batch_size]
                
                # 提交分类任务
                future_to_bookmark = {
                    executor.submit(self._classify_single, bookmark): bookmark
                    for bookmark in batch
                }
                
                # 收集结果
                batch_results = []
                for future in as_completed(future_to_bookmark):
                    bookmark = future_to_bookmark[future]
                    
                    try:
                        result = future.result(timeout=30)
                        if result:
                            batch_results.append(result)
                    except Exception as e:
                        self.logger.error(
                            f"分类失败 {bookmark.get('url', 'unknown')}: {e}"
                        )
                        with self._stats_lock:
                            self.stats["errors"] += 1
                
                classified_bookmarks.extend(batch_results)
                
                # 显示进度
                completed = i + len(batch)
                progress = min(completed / len(bookmarks) * 100, 100)
                self.logger.info(
                    f"分类进度: {progress:.1f}% ({completed}/{len(bookmarks)})"
                )
        
        # 更新统计
        self.stats["classified_count"] = len(classified_bookmarks)
        self.stats["processing_time"] = time.time() - start_time
        
        return classified_bookmarks, self.stats.copy()
    
    def _classify_single(self, bookmark: Dict) -> Optional[Dict]:
        """分类单个书签（带缓存）"""
        try:
            url = bookmark["url"]
            title = bookmark["title"]
            
            # 创建缓存键
            cache_key = f"{url}|{title}"
            
            # 检查缓存
            cached_result = self._classification_cache.get(cache_key)
            if cached_result is not None:
                with self._stats_lock:
                    self.stats["cache_hits"] += 1
                return {**bookmark, **cached_result}
            
            # 使用 AI 分类器
            result = self.classifier.classify(url, title)
            
            # 处理分类结果
            if hasattr(result, "category"):
                # ClassificationResult 对象
                cached_data = {
                    "category": normalize_category_string(result.category),
                    "subcategory": result.subcategory if hasattr(result, "subcategory") else None,
                    "confidence": result.confidence,
                    "alternatives": result.alternatives if hasattr(result, "alternatives") else [],
                    "reasoning": result.reasoning if hasattr(result, "reasoning") else [],
                    "method": result.method if hasattr(result, "method") else "unknown",
                    "processing_time": result.processing_time if hasattr(result, "processing_time") else 0.0,
                    "facets": result.facets if hasattr(result, "facets") else {},
                    "score_breakdown": result.score_breakdown if hasattr(result, "score_breakdown") else {},
                }
            else:
                # 字典结果
                cached_data = {
                    "category": normalize_category_string(result.get("category", "未分类")),
                    "subcategory": result.get("subcategory"),
                    "confidence": result.get("confidence", 0.0),
                    "alternatives": result.get("alternatives", []),
                    "reasoning": result.get("reasoning", []),
                    "method": result.get("method", "unknown"),
                    "processing_time": result.get("processing_time", 0.0),
                    "facets": result.get("facets", {}),
                    "score_breakdown": result.get("score_breakdown", {}),
                }
            
            # 存入缓存
            self._classification_cache.put(cache_key, cached_data)
            
            # 更新分类统计
            category = cached_data.get("category", "未分类")
            with self._stats_lock:
                self.stats["categories_found"][category] = (
                    self.stats["categories_found"].get(category, 0) + 1
                )
            
            return {**bookmark, **cached_data}
            
        except Exception as e:
            self.logger.debug(f"分类失败 [{bookmark.get('url', 'unknown')}]: {e}")
            return None
    
    def train_models(self, classified_bookmarks: List[Dict]) -> bool:
        """训练 ML 模型
        
        Args:
            classified_bookmarks: 已分类的书签列表
            
        Returns:
            是否成功训练
        """
        if not self.classifier.ml_classifier:
            self.logger.warning("机器学习组件未启用，跳过训练")
            return False
        
        self.logger.info("开始训练机器学习模型...")
        
        # 准备训练数据
        samples_added = 0
        for bookmark in classified_bookmarks:
            if bookmark.get("confidence", 0.0) > 0.8:
                # 只使用高置信度的数据训练
                try:
                    features = self.classifier.extract_features(
                        bookmark["url"],
                        bookmark["title"]
                    )
                    self.classifier.ml_classifier.online_learn(
                        features,
                        bookmark["category"]
                    )
                    samples_added += 1
                except Exception as e:
                    self.logger.debug(f"训练样本添加失败: {e}")
        
        self.logger.info(f"训练完成: 添加了 {samples_added} 个样本")
        return samples_added > 0
    
    def _reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "classified_count": 0,
            "cache_hits": 0,
            "errors": 0,
            "processing_time": 0.0,
            "categories_found": {},
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def clear_cache(self) -> None:
        """清空分类缓存"""
        self._classification_cache.clear()
        self.logger.info("分类缓存已清空")
