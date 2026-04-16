"""
Plugin System for CleanBook Classifier
插件式分类器架构

提供可扩展的分类器插件接口，支持动态加载和组合多种分类策略。

Example:
    >>> from src.plugins import ClassifierPlugin, PluginMetadata
    >>> from src.plugins.base import BookmarkFeatures, ClassificationResult

    class MyClassifier(ClassifierPlugin):
        @property
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="my_classifier",
                version="1.0.0",
                capabilities=["custom"],
            )

        def classify(self, features: BookmarkFeatures) -> ClassificationResult:
            # 实现分类逻辑
            pass
"""

from .base import (
    ClassifierPlugin,
    PluginMetadata,
    BookmarkFeatures,
    ClassificationResult,
)
from .registry import PluginRegistry
from .pipeline import ClassifierPipeline

__all__ = [
    'ClassifierPlugin',
    'PluginMetadata',
    'BookmarkFeatures',
    'ClassificationResult',
    'PluginRegistry',
    'ClassifierPipeline',
]
