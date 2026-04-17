"""
engines - 引擎模块

包含规则引擎、语义分析、URL 分析等核心引擎
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .rules import RuleEngine
    from .semantic import SemanticAnalyzer
    from .url import URLAnalyzer
    from .smart_loader import SmartRuleLoader

__all__ = ["RuleEngine", "SemanticAnalyzer", "URLAnalyzer", "SmartRuleLoader"]


def __getattr__(name: str):
    """按需加载引擎模块"""
    _mapping = {
        "RuleEngine": (".rules", "RuleEngine"),
        "SemanticAnalyzer": (".semantic", "SemanticAnalyzer"),
        "URLAnalyzer": (".url", "URLAnalyzer"),
        "SmartRuleLoader": (".smart_loader", "SmartRuleLoader"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
