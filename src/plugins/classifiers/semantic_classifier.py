"""
Semantic Classifier Plugin - 语义分析分类器插件
将现有 SemanticAnalyzer 封装为 ClassifierPlugin 接口
"""

import logging
from typing import Any, Dict, Optional

from ..base import (
    BookmarkFeatures,
    ClassificationResult,
    ClassifierPlugin,
    PluginMetadata,
)


class SemanticClassifierPlugin(ClassifierPlugin):
    """语义分析分类器插件"""

    def __init__(self, semantic_analyzer=None):
        """
        初始化语义分析分类器插件

        Args:
            semantic_analyzer: 可选的 SemanticAnalyzer 实例
        """
        self._semantic_analyzer = semantic_analyzer
        self._config: Dict[str, Any] = {}
        self._initialized = False
        self.logger = logging.getLogger(__name__)

    @property
    def metadata(self) -> PluginMetadata:
        """返回插件元数据"""
        return PluginMetadata(
            name="semantic_analyzer",
            version="1.0.0",
            capabilities=["semantic_analysis", "keyword_matching", "similarity"],
            author="CleanBook",
            description="基于语义分析和关键词匹配的分类器",
            dependencies=[],
            priority=60,  # 中等优先级
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

            if self._semantic_analyzer is None:
                from src.engines.semantic import SemanticAnalyzer
                self._semantic_analyzer = SemanticAnalyzer(config)

            self._initialized = True
            self.logger.info("SemanticClassifierPlugin initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize SemanticClassifierPlugin: {e}")
            return False

    def shutdown(self) -> None:
        """关闭插件"""
        self._semantic_analyzer = None
        self._initialized = False
        self.logger.info("SemanticClassifierPlugin shutdown")

    def classify(self, features: BookmarkFeatures) -> Optional[ClassificationResult]:
        """
        执行分类

        Args:
            features: 书签特征

        Returns:
            分类结果，如果无法分类则返回 None
        """
        if not self._initialized or self._semantic_analyzer is None:
            return None

        try:
            result = self._semantic_analyzer.classify(features)

            if result is None:
                return None

            # 如果已经是 ClassificationResult，直接返回
            if isinstance(result, ClassificationResult):
                return result

            # 转换字典结果
            if isinstance(result, dict):
                return ClassificationResult(
                    category=result.get("category", "未分类"),
                    confidence=float(result.get("confidence", 0.0)),
                    reasoning=result.get("reasoning", []),
                    method="semantic_analyzer",
                    facets=result.get("facets", {}),
                )

            return None

        except Exception as e:
            self.logger.debug(f"Semantic classification failed: {e}")
            return None
