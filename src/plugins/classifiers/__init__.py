"""
Classifier Plugins
分类器插件集合

所有插件均为可选组件，缺少依赖时按需报错而非启动时崩溃。
"""

__all__ = [
    "EmbeddingClassifier",
    "RuleClassifierPlugin",
    "MLClassifierPlugin",
    "LLMClassifierPlugin",
    "SemanticClassifierPlugin",
    "UserProfilerPlugin",
]


def __getattr__(name: str):
    """按需延迟导入插件。"""
    _mapping = {
        "EmbeddingClassifier": ".embedding_classifier",
        "RuleClassifierPlugin": ".rule_classifier",
        "MLClassifierPlugin": ".ml_classifier",
        "LLMClassifierPlugin": ".llm_classifier",
        "SemanticClassifierPlugin": ".semantic_classifier",
        "UserProfilerPlugin": ".user_profiler_plugin",
    }
    if name in _mapping:
        import importlib

        module = importlib.import_module(_mapping[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
