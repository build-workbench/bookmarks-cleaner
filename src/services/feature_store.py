"""
Feature Store - 特征存储与缓存
缓存和管理提取的书签特征向量
"""

import os
import pickle
import time
import threading
import logging
from typing import Optional, Dict, Any, List, Tuple
from collections import OrderedDict
import numpy as np

class FeatureStore:
    """特征存储与缓存"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化特征存储
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.max_size = config.get('max_size', 100000)
        self.ttl_seconds = config.get('ttl_seconds', 86400 * 7)  # 7天
        self.persist_path = config.get('persist_path', 'cache/features')
        self.hit_rate_threshold = config.get('hit_rate_threshold', 0.5)
        
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        
        # 统计
        self._hits = 0
        self._misses = 0
        
        # ANN 索引（可选）
        self._ann_index = None
        
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """
        获取缓存的特征
        
        Args:
            key: 缓存键
            
        Returns:
            特征向量，如果不存在或已过期则返回 None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                self._check_hit_rate()
                return None
            
            # 检查 TTL
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                self._evict(key)
                self._misses += 1
                return None
            
            # LRU: 移到末尾
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def put(self, key: str, value: np.ndarray):
        """
        存储特征
        
        Args:
            key: 缓存键
            value: 特征向量
        """
        with self._lock:
            # LRU 驱逐
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                self._evict(oldest_key)
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
    
    def _evict(self, key: str):
        """
        驱逐缓存项
        
        Args:
            key: 缓存键
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def _check_hit_rate(self):
        """检查命中率并发出警告"""
        total = self._hits + self._misses
        if total > 1000:
            hit_rate = self._hits / total
            if hit_rate < self.hit_rate_threshold:
                self.logger.warning(
                    f"Feature cache hit rate ({hit_rate:.2%}) below threshold "
                    f"({self.hit_rate_threshold:.2%}). Consider increasing cache size."
                )
    
    def find_similar(self, embedding: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        近似最近邻搜索
        
        Args:
            embedding: 查询向量
            top_k: 返回前 k 个最相似的结果
            
        Returns:
            (键, 相似度) 元组列表
        """
        if self._ann_index is None:
            return self._brute_force_search(embedding, top_k)
        # 使用 ANN 索引
        return self._ann_search(embedding, top_k)
    
    def _brute_force_search(self, embedding: np.ndarray, top_k: int) -> List[Tuple[str, float]]:
        """
        暴力搜索（小规模数据）
        
        Args:
            embedding: 查询向量
            top_k: 返回前 k 个结果
            
        Returns:
            (键, 相似度) 元组列表
        """
        similarities = []
        with self._lock:
            for key, cached_embedding in self._cache.items():
                sim = self._cosine_similarity(embedding, cached_embedding)
                similarities.append((key, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _ann_search(self, embedding: np.ndarray, top_k: int) -> List[Tuple[str, float]]:
        """
        使用 ANN 索引搜索（预留接口）
        
        Args:
            embedding: 查询向量
            top_k: 返回前 k 个结果
            
        Returns:
            (键, 相似度) 元组列表
        """
        # 预留接口，可以集成 FAISS 或 Annoy
        return self._brute_force_search(embedding, top_k)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            a: 向量 a
            b: 向量 b
            
        Returns:
            余弦相似度
        """
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def persist(self):
        """持久化到磁盘"""
        os.makedirs(self.persist_path, exist_ok=True)
        with self._lock:
            data = {
                'cache': dict(self._cache),
                'timestamps': self._timestamps,
                'stats': {'hits': self._hits, 'misses': self._misses}
            }
            filepath = os.path.join(self.persist_path, 'features.pkl')
            try:
                with open(filepath, 'wb') as f:
                    pickle.dump(data, f)
                self.logger.info(f"Feature store persisted to {filepath}")
            except Exception as e:
                self.logger.error(f"Failed to persist feature store: {e}")
    
    def load(self):
        """从磁盘加载"""
        filepath = os.path.join(self.persist_path, 'features.pkl')
        if not os.path.exists(filepath):
            self.logger.info("No persisted feature store found")
            return
        
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            with self._lock:
                self._cache = OrderedDict(data.get('cache', {}))
                self._timestamps = data.get('timestamps', {})
                stats = data.get('stats', {})
                self._hits = stats.get('hits', 0)
                self._misses = stats.get('misses', 0)
            
            self.logger.info(f"Feature store loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load feature store: {e}")
    
    def warm_cache(self, historical_data: List[Dict]):
        """
        缓存预热
        
        Args:
            historical_data: 历史数据列表，每项包含 'key' 和 'embedding'
        """
        count = 0
        for item in historical_data:
            if 'key' in item and 'embedding' in item:
                self.put(item['key'], item['embedding'])
                count += 1
        
        self.logger.info(f"Cache warmed with {count} items")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total = self._hits + self._misses
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self._hits / total if total > 0 else 0,
            'ttl_seconds': self.ttl_seconds
        }
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._hits = 0
            self._misses = 0
        self.logger.info("Feature store cleared")
