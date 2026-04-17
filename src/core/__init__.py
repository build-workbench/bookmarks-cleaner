"""
core - 核心功能模块

包含书签处理的核心功能：处理器、导出器、去重器等
"""

# 延迟导入，避免循环依赖
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .processor import BookmarkProcessor
    from .exporter import DataExporter
    from src.data.deduplicator import BookmarkDeduplicator

__all__ = ["BookmarkProcessor", "DataExporter", "BookmarkDeduplicator"]


def __getattr__(name: str):
    """按需加载核心模块"""
    _mapping = {
        "BookmarkProcessor": (".processor", "BookmarkProcessor"),
        "DataExporter": (".exporter", "DataExporter"),
        "BookmarkDeduplicator": (".deduplicator", "BookmarkDeduplicator"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
