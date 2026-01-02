"""
Active Learning Engine - 主动学习引擎
识别低置信度样本并管理用户反馈收集
"""

import heapq
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


@dataclass(order=True)
class ReviewItem:
    """待审核项"""
    priority: float = field(compare=True)  # 用于堆排序（负的不确定性分数）
    bookmark_id: str = field(compare=False)
    url: str = field(compare=False)
    title: str = field(compare=False)
    predicted_category: str = field(compare=False)
    confidence: float = field(compare=False)
    alternatives: List[Tuple[str, float]] = field(compare=False, default_factory=list)
    uncertainty_score: float = field(compare=False, default=0.0)
    timestamp: datetime = field(compare=False, default_factory=datetime.now)


class ActiveLearningEngine:
    """主动学习引擎"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化主动学习引擎
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.confidence_threshold = self.config.get('confidence_threshold', 0.6)
        self.max_requests_per_session = self.config.get('max_requests_per_session', 10)
        self.persist_path = self.config.get('persist_path', 'data/active_learning')
        
        # 优先队列（使用负的不确定性分数，因为 heapq 是最小堆）
        self.review_queue: List[ReviewItem] = []
        
        # 已标注样本
        self.labeled_samples: List[Dict] = []
        
        # 会话请求计数
        self.session_request_count = 0
        
        # 统计信息
        self._stats = {
            'total_processed': 0,
            'low_confidence_detected': 0,
            'feedback_collected': 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # 加载持久化数据
        self._load_data()
    
    def process_classification(
        self,
        bookmark: Dict,
        category: str,
        confidence: float,
        alternatives: List[Tuple[str, float]] = None
    ) -> Optional[ReviewItem]:
        """
        处理分类结果，识别低置信度样本
        
        Args:
            bookmark: 书签信息字典
            category: 预测的分类
            confidence: 置信度
            alternatives: 备选分类列表
            
        Returns:
            如果是低置信度样本，返回 ReviewItem；否则返回 None
        """
        self._stats['total_processed'] += 1
        
        if confidence >= self.confidence_threshold:
            return None
        
        self._stats['low_confidence_detected'] += 1
        
        # 计算不确定性分数（熵）
        uncertainty = self._calculate_uncertainty(confidence, alternatives or [])
        
        item = ReviewItem(
            priority=-uncertainty,  # 负值用于最大堆效果
            bookmark_id=bookmark.get('id', str(hash(bookmark.get('url', '')))),
            url=bookmark.get('url', ''),
            title=bookmark.get('title', ''),
            predicted_category=category,
            confidence=confidence,
            alternatives=alternatives[:3] if alternatives else [],
            uncertainty_score=uncertainty,
            timestamp=datetime.now()
        )
        
        # 加入优先队列
        heapq.heappush(self.review_queue, item)
        
        return item
    
    def _calculate_uncertainty(
        self,
        confidence: float,
        alternatives: List[Tuple[str, float]]
    ) -> float:
        """
        计算不确定性分数（基于熵）
        
        Args:
            confidence: 主分类置信度
            alternatives: 备选分类列表
            
        Returns:
            不确定性分数
        """
        scores = [confidence] + [s for _, s in alternatives]
        total = sum(scores)
        
        if total == 0:
            return 1.0
        
        probs = [s / total for s in scores]
        
        # 计算熵
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * np.log(p + 1e-10)
        
        return float(entropy)
    
    def get_next_review_item(self) -> Optional[ReviewItem]:
        """
        获取下一个待审核项
        
        Returns:
            待审核项，如果队列为空或达到会话限制则返回 None
        """
        if self.session_request_count >= self.max_requests_per_session:
            return None
        
        if not self.review_queue:
            return None
        
        self.session_request_count += 1
        item = heapq.heappop(self.review_queue)
        
        return item
    
    def peek_review_queue(self, n: int = 5) -> List[ReviewItem]:
        """
        查看队列中的前 n 个待审核项（不移除）
        
        Args:
            n: 要查看的数量
            
        Returns:
            待审核项列表
        """
        # 获取最小的 n 个元素（不确定性最高的）
        return heapq.nsmallest(n, self.review_queue)
    
    def submit_feedback(
        self,
        bookmark_id: str,
        correct_category: str,
        original_prediction: str = None,
        original_confidence: float = None
    ):
        """
        提交用户反馈
        
        Args:
            bookmark_id: 书签 ID
            correct_category: 正确的分类
            original_prediction: 原始预测分类
            original_confidence: 原始置信度
        """
        sample = {
            'bookmark_id': bookmark_id,
            'correct_category': correct_category,
            'original_prediction': original_prediction,
            'original_confidence': original_confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        self.labeled_samples.append(sample)
        self._stats['feedback_collected'] += 1
        
        # 持久化
        self._save_data()
    
    def get_labeled_samples(self, since: datetime = None) -> List[Dict]:
        """
        获取已标注样本用于训练
        
        Args:
            since: 可选的时间过滤器
            
        Returns:
            已标注样本列表
        """
        if since is None:
            return self.labeled_samples.copy()
        
        return [
            s for s in self.labeled_samples
            if datetime.fromisoformat(s['timestamp']) >= since
        ]
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return len(self.review_queue)
    
    def get_remaining_requests(self) -> int:
        """获取本会话剩余请求数"""
        return max(0, self.max_requests_per_session - self.session_request_count)
    
    def reset_session(self):
        """重置会话计数"""
        self.session_request_count = 0
    
    def clear_queue(self):
        """清空审核队列"""
        self.review_queue.clear()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self._stats,
            'queue_size': len(self.review_queue),
            'labeled_samples_count': len(self.labeled_samples),
            'session_requests': self.session_request_count,
            'remaining_requests': self.get_remaining_requests()
        }
    
    def _save_data(self):
        """持久化数据"""
        try:
            os.makedirs(self.persist_path, exist_ok=True)
            
            data = {
                'labeled_samples': self.labeled_samples,
                'stats': self._stats
            }
            
            filepath = os.path.join(self.persist_path, 'active_learning_data.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save active learning data: {e}")
    
    def _load_data(self):
        """加载持久化数据"""
        try:
            filepath = os.path.join(self.persist_path, 'active_learning_data.json')
            
            if not os.path.exists(filepath):
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.labeled_samples = data.get('labeled_samples', [])
            self._stats.update(data.get('stats', {}))
            
        except Exception as e:
            self.logger.error(f"Failed to load active learning data: {e}")
