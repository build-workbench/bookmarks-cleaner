"""
ML Classifier Plugin - 机器学习分类器插件
将现有 MLBookmarkClassifier 封装为 ClassifierPlugin 接口
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures


class MLClassifierPlugin(ClassifierPlugin):
    """机器学习分类器插件"""
    
    def __init__(self, ml_classifier=None):
        """
        初始化机器学习分类器插件
        
        Args:
            ml_classifier: 可选的 MLBookmarkClassifier 实例
        """
        self._ml_classifier = ml_classifier
        self._config: Dict[str, Any] = {}
        self._initialized = False
        self._ml_available = False
        self.logger = logging.getLogger(__name__)
    
    @property
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        return PluginMetadata(
            name="ml_classifier",
            version="1.0.0",
            capabilities=["machine_learning", "ensemble", "online_learning"],
            author="CleanBook",
            description="基于机器学习的分类器，支持多种算法和在线学习",
            dependencies=["scikit-learn", "jieba"],
            priority=50  # 中等优先级
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件
        
        Args:
            config: 配置字典
            
        Returns:
            初始化是否成功
        """
        try:
            self._config = config
            
            # 检查 ML 依赖是否可用
            try:
                from ...ml_classifier import ML_AVAILABLE, MLBookmarkClassifier
                self._ml_available = ML_AVAILABLE
            except ImportError:
                self._ml_available = False
                self.logger.warning("ML dependencies not available")
                return False
            
            if not self._ml_available:
                self.logger.warning("ML dependencies not available")
                return False
            
            if self._ml_classifier is None:
                model_dir = config.get('model_dir', 'models/ml')
                self._ml_classifier = MLBookmarkClassifier(model_dir=model_dir)
                
                # 尝试加载已有模型
                self._ml_classifier.load_model()
            
            self._initialized = True
            self.logger.info("MLClassifierPlugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MLClassifierPlugin: {e}")
            return False
    
    def shutdown(self) -> None:
        """关闭插件"""
        if self._ml_classifier is not None:
            # 保存模型
            try:
                self._ml_classifier.save_model()
            except Exception as e:
                self.logger.error(f"Failed to save model on shutdown: {e}")
        
        self._ml_classifier = None
        self._initialized = False
        self.logger.info("MLClassifierPlugin shutdown")
    
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行分类
        
        Args:
            features: 书签特征
            
        Returns:
            分类结果，如果无法分类则返回 None
        """
        if not self._initialized or self._ml_classifier is None:
            return None
        
        if not self._ml_available:
            return None
        
        try:
            # 构建书签字典
            bookmark = {
                'url': features.url,
                'title': features.title,
                'domain': features.domain,
                'path_segments': features.path_segments,
                'content_type': features.content_type,
                'language': features.language
            }
            
            # 预测
            category, confidence = self._ml_classifier.predict_single(bookmark)
            
            if confidence < 0.3:  # 最低置信度阈值
                return None
            
            return ClassificationResult(
                category=category,
                confidence=confidence,
                score_breakdown={},
                alternative_categories=[],
                reasoning=[f"ML model prediction with confidence {confidence:.2f}"],
                method='machine_learning',
                facets={}
            )
            
        except Exception as e:
            self.logger.error(f"ML classification failed: {e}")
            return None
    
    def supports_batch(self) -> bool:
        """是否支持批量处理"""
        return True
    
    def classify_batch(self, features_list: List[BookmarkFeatures]) -> List[Optional[ClassificationResult]]:
        """
        批量分类
        
        Args:
            features_list: 书签特征列表
            
        Returns:
            分类结果列表
        """
        if not self._initialized or self._ml_classifier is None:
            return [None] * len(features_list)
        
        try:
            bookmarks = [
                {
                    'url': f.url,
                    'title': f.title,
                    'domain': f.domain,
                    'path_segments': f.path_segments,
                    'content_type': f.content_type,
                    'language': f.language
                }
                for f in features_list
            ]
            
            predictions = self._ml_classifier.predict(bookmarks)
            
            results = []
            for category, confidence in predictions:
                if confidence < 0.3:
                    results.append(None)
                else:
                    results.append(ClassificationResult(
                        category=category,
                        confidence=confidence,
                        score_breakdown={},
                        alternative_categories=[],
                        reasoning=[f"ML model prediction with confidence {confidence:.2f}"],
                        method='machine_learning',
                        facets={}
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"ML batch classification failed: {e}")
            return [None] * len(features_list)
    
    def online_learn(self, features: BookmarkFeatures, correct_category: str):
        """在线学习"""
        if self._ml_classifier is not None:
            bookmark = {
                'url': features.url,
                'title': features.title,
                'domain': features.domain,
                'path_segments': features.path_segments,
                'content_type': features.content_type,
                'language': features.language
            }
            self._ml_classifier.online_learn(bookmark, correct_category)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if self._ml_classifier is None:
            return {}
        return self._ml_classifier.get_stats()
