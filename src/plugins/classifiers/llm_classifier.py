"""
LLM Classifier Plugin - 大模型分类器插件
将现有 LLMClassifier 封装为 ClassifierPlugin 接口
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures


class LLMClassifierPlugin(ClassifierPlugin):
    """大模型分类器插件"""
    
    def __init__(self, llm_classifier=None):
        """
        初始化大模型分类器插件
        
        Args:
            llm_classifier: 可选的 LLMClassifier 实例
        """
        self._llm_classifier = llm_classifier
        self._config: Dict[str, Any] = {}
        self._initialized = False
        self.logger = logging.getLogger(__name__)
    
    @property
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        return PluginMetadata(
            name="llm_classifier",
            version="1.0.0",
            capabilities=["llm", "semantic_understanding", "context_aware"],
            author="CleanBook",
            description="基于大语言模型的分类器，提供深度语义理解能力",
            dependencies=["requests"],
            priority=90  # 低优先级，LLM 调用成本高
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
            
            if self._llm_classifier is None:
                # 延迟导入以避免循环依赖
                from ...llm_classifier import LLMClassifier
                
                config_path = config.get('config_path', 'config.json')
                self._llm_classifier = LLMClassifier(config_path=config_path)
            
            # 检查 LLM 是否启用
            if not self._llm_classifier.enabled():
                self.logger.info("LLM classifier is disabled in config")
                # 仍然标记为初始化成功，但 classify 会返回 None
            
            self._initialized = True
            self.logger.info("LLMClassifierPlugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLMClassifierPlugin: {e}")
            return False
    
    def shutdown(self) -> None:
        """关闭插件"""
        self._llm_classifier = None
        self._initialized = False
        self.logger.info("LLMClassifierPlugin shutdown")
    
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行分类
        
        Args:
            features: 书签特征
            
        Returns:
            分类结果，如果无法分类则返回 None
        """
        if not self._initialized or self._llm_classifier is None:
            return None
        
        if not self._llm_classifier.enabled():
            return None
        
        try:
            # 构建上下文
            context = {
                'domain': features.domain,
                'path_segments': features.path_segments,
                'content_type': features.content_type,
                'language': features.language
            }
            
            result = self._llm_classifier.classify(
                url=features.url,
                title=features.title,
                context=context
            )
            
            if result is None:
                return None
            
            return ClassificationResult(
                category=result['category'],
                confidence=result['confidence'],
                score_breakdown={},
                alternative_categories=[],
                reasoning=result.get('reasoning', []),
                method='llm',
                facets=result.get('facets', {})
            )
            
        except Exception as e:
            self.logger.error(f"LLM classification failed: {e}")
            return None
    
    def supports_batch(self) -> bool:
        """是否支持批量处理"""
        return False  # LLM 调用成本高，不支持批量
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        if self._llm_classifier is None:
            return {}
        return self._llm_classifier.get_stats()
