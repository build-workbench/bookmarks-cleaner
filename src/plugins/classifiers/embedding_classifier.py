"""
Embedding Classifier Plugin - 基于嵌入的分类器插件
使用 Transformer 嵌入和余弦相似度进行分类
"""

import logging
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugins.base import ClassifierPlugin, PluginMetadata

@dataclass
class ClassificationResult:
    """分类结果"""
    category: str
    confidence: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    alternative_categories: List[Tuple[str, float]] = field(default_factory=list)
    reasoning: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    method: str = "embedding"

class EmbeddingClassifier(ClassifierPlugin):
    """基于嵌入的分类器插件"""
    
    def __init__(self):
        self._metadata = PluginMetadata(
            name="embedding_classifier",
            version="1.0.0",
            capabilities=["classification", "similarity"],
            author="CleanBook",
            description="Transformer embedding-based classifier using cosine similarity",
            priority=50
        )
        self._initialized = False
        self._embedding_service = None
        self._category_prototypes: Dict[str, np.ndarray] = {}
        self._similarity_threshold = 0.5
        self.logger = logging.getLogger(__name__)
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件
        
        Args:
            config: 配置字典，包含 embedding_service 和 category_prototypes
            
        Returns:
            初始化是否成功
        """
        try:
            self._embedding_service = config.get('embedding_service')
            self._similarity_threshold = config.get('similarity_threshold', 0.5)
            
            # 加载类别原型嵌入
            prototypes = config.get('category_prototypes', {})
            for category, prototype in prototypes.items():
                if isinstance(prototype, np.ndarray):
                    self._category_prototypes[category] = prototype
                elif isinstance(prototype, list):
                    self._category_prototypes[category] = np.array(prototype)
            
            self._initialized = True
            self.logger.info(f"EmbeddingClassifier initialized with {len(self._category_prototypes)} categories")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize EmbeddingClassifier: {e}")
            return False
    
    def shutdown(self) -> None:
        """关闭插件"""
        self._initialized = False
        self._category_prototypes.clear()
        self.logger.info("EmbeddingClassifier shutdown")
    
    def classify(self, features) -> Optional[ClassificationResult]:
        """
        执行分类
        
        Args:
            features: 书签特征对象
            
        Returns:
            分类结果
        """
        if not self._initialized or not self._embedding_service:
            return None
        
        if not self._category_prototypes:
            return None
        
        try:
            # 生成书签嵌入
            text = f"{features.title} {features.url}"
            bookmark_embedding = self._embedding_service.embed(text)
            
            # 计算与各类别原型的相似度
            similarities = {}
            for category, prototype in self._category_prototypes.items():
                sim = self._embedding_service.compute_similarity(bookmark_embedding, prototype)
                similarities[category] = sim
            
            if not similarities:
                return None
            
            # 选择最相似的类别
            best_category = max(similarities, key=similarities.get)
            best_similarity = similarities[best_category]
            
            # 检查是否超过阈值
            if best_similarity < self._similarity_threshold:
                return None
            
            # 生成备选类别
            alternatives = [
                (cat, sim) for cat, sim in similarities.items()
                if cat != best_category
            ]
            alternatives.sort(key=lambda x: x[1], reverse=True)
            
            return ClassificationResult(
                category=best_category,
                confidence=best_similarity,
                score_breakdown=similarities,
                alternative_categories=alternatives[:5],
                reasoning=[f"Cosine similarity with '{best_category}' prototype: {best_similarity:.3f}"],
                method="embedding"
            )
        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            return None
    
    def supports_batch(self) -> bool:
        return True
    
    def classify_batch(self, features_list) -> List[Optional[ClassificationResult]]:
        """批量分类"""
        return [self.classify(f) for f in features_list]
    
    def add_category_prototype(self, category: str, texts: List[str]):
        """
        添加类别原型
        
        Args:
            category: 类别名称
            texts: 代表该类别的文本列表
        """
        if not self._embedding_service:
            return
        
        embeddings = self._embedding_service.embed_batch(texts)
        prototype = np.mean(embeddings, axis=0)
        self._category_prototypes[category] = prototype
        self.logger.info(f"Added prototype for category '{category}' from {len(texts)} texts")
    
    def update_prototype(self, category: str, new_embedding: np.ndarray, alpha: float = 0.1):
        """
        增量更新类别原型
        
        Args:
            category: 类别名称
            new_embedding: 新的嵌入向量
            alpha: 学习率
        """
        if category in self._category_prototypes:
            old_prototype = self._category_prototypes[category]
            self._category_prototypes[category] = (1 - alpha) * old_prototype + alpha * new_embedding
        else:
            self._category_prototypes[category] = new_embedding
