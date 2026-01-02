"""
Rule Classifier Plugin - 规则分类器插件
将现有 RuleEngine 封装为 ClassifierPlugin 接口
"""

import logging
from typing import Dict, List, Optional, Any

from ..base import ClassifierPlugin, PluginMetadata, ClassificationResult, BookmarkFeatures


class RuleClassifierPlugin(ClassifierPlugin):
    """规则分类器插件"""
    
    def __init__(self, rule_engine=None):
        """
        初始化规则分类器插件
        
        Args:
            rule_engine: 可选的 RuleEngine 实例，如果不提供则在 initialize 时创建
        """
        self._rule_engine = rule_engine
        self._config: Dict[str, Any] = {}
        self._initialized = False
        self.logger = logging.getLogger(__name__)
    
    @property
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        return PluginMetadata(
            name="rule_classifier",
            version="1.0.0",
            capabilities=["fast_classification", "rule_based", "domain_matching"],
            author="CleanBook",
            description="基于规则的快速分类器，使用域名、URL、标题等特征进行匹配",
            dependencies=[],
            priority=10  # 高优先级，规则引擎应该先执行
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化插件
        
        Args:
            config: 配置字典，应包含规则配置
            
        Returns:
            初始化是否成功
        """
        try:
            self._config = config
            
            if self._rule_engine is None:
                # 延迟导入以避免循环依赖
                from ...rule_engine import RuleEngine
                
                # 从配置中获取规则配置
                rule_config = config.get('rules', config)
                self._rule_engine = RuleEngine(rule_config)
            
            self._initialized = True
            self.logger.info("RuleClassifierPlugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RuleClassifierPlugin: {e}")
            return False
    
    def shutdown(self) -> None:
        """关闭插件"""
        self._rule_engine = None
        self._initialized = False
        self.logger.info("RuleClassifierPlugin shutdown")
    
    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行分类
        
        Args:
            features: 书签特征
            
        Returns:
            分类结果，如果无法分类则返回 None
        """
        if not self._initialized or self._rule_engine is None:
            return None
        
        try:
            result = self._rule_engine.classify(features)
            
            if result is None:
                return None
            
            # 转换为 ClassificationResult
            alternatives = result.get('alternatives', [])
            
            return ClassificationResult(
                category=result['category'],
                confidence=result['confidence'],
                score_breakdown=result.get('score_breakdown', {}),
                alternative_categories=alternatives,
                reasoning=result.get('reasoning', []),
                method='rule_engine',
                facets=result.get('facets', {})
            )
            
        except Exception as e:
            self.logger.error(f"Rule classification failed: {e}")
            return None
    
    def supports_batch(self) -> bool:
        """是否支持批量处理"""
        return False
    
    def get_rule_performance(self) -> Dict:
        """获取规则性能统计"""
        if self._rule_engine is None:
            return {}
        return self._rule_engine.get_rule_performance()
    
    def add_dynamic_rule(self, category: str, match_type: str, keyword: str, weight: float = 1.0):
        """动态添加规则"""
        if self._rule_engine is not None:
            self._rule_engine.add_dynamic_rule(category, match_type, keyword, weight)
