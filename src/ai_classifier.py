"""
AI Bookmark Classifier - 兼容性重定向模块

此模块已被重构到 src.classifiers.ai
请使用新的导入路径: from src.classifiers.ai import AIBookmarkClassifier

保留此文件仅为向后兼容，将在未来版本中移除。
"""

import warnings

# 发出弃用警告
warnings.warn(
    "从 src.ai_classifier 导入已弃用，请使用 src.classifiers.ai 代替",
    DeprecationWarning,
    stacklevel=2,
)

# 重定向到新模块
from src.classifiers.ai import (
    AIBookmarkClassifier,
    BookmarkFeatures,
    ClassificationResult,
)

__all__ = ["AIBookmarkClassifier", "BookmarkFeatures", "ClassificationResult"]
