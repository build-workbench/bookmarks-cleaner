"""
Classifier Plugins
分类器插件集合
"""

from .embedding_classifier import EmbeddingClassifier
from .rule_classifier import RuleClassifierPlugin
from .ml_classifier import MLClassifierPlugin
from .llm_classifier import LLMClassifierPlugin

__all__ = [
    'EmbeddingClassifier',
    'RuleClassifierPlugin',
    'MLClassifierPlugin',
    'LLMClassifierPlugin'
]
