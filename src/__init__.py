"""src 顶层包

为现有模块提供包命名空间，便于打包与 console script 导入。
"""

__version__ = "2.0.1"

__all__ = [
    "AIBookmarkClassifier",
    "BookmarkProcessor",
    "RuleEngine",
    "DataExporter",
    "BookmarkDeduplicator",
]


def __getattr__(name: str):
    """按需延迟导入，避免启动时加载全部模块。"""
    _mapping = {
        "AIBookmarkClassifier": ".classifiers.ai",
        "BookmarkProcessor": ".bookmark_processor",
        "RuleEngine": ".rule_engine",
        "DataExporter": ".data_exporter",
        "BookmarkDeduplicator": ".deduplicator",
    }
    if name in _mapping:
        import importlib

        module = importlib.import_module(_mapping[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
