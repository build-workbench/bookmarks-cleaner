"""
data - 数据处理模块

包含数据导出、导入、转换等功能
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .exporter import DataExporter
    from src.data.deduplicator import BookmarkDeduplicator

__all__ = ["DataExporter", "BookmarkDeduplicator"]


def __getattr__(name: str):
    """按需加载数据模块"""
    _mapping = {
        "DataExporter": (".exporter", "DataExporter"),
        "BookmarkDeduplicator": (".deduplicator", "BookmarkDeduplicator"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
