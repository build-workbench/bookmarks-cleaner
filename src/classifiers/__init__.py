"""
classifiers - 分类器模块

包含规则、ML、LLM 等多种分类策略的实现
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ai import AIBookmarkClassifier
    from .ml import MLClassifier
    from .llm import LLMClassifier
    from .enhanced import EnhancedClassifier

__all__ = [
    "AIBookmarkClassifier",
    "MLClassifier",
    "LLMClassifier",
    "EnhancedClassifier",
]


def __getattr__(name: str):
    """按需加载分类器模块"""
    _mapping = {
        "AIBookmarkClassifier": (".ai", "AIBookmarkClassifier"),
        "MLClassifier": (".ml", "MLClassifier"),
        "LLMClassifier": (".llm", "LLMClassifier"),
        "EnhancedClassifier": (".enhanced", "EnhancedClassifier"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
