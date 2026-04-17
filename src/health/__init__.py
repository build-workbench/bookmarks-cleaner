"""
health - 健康检查模块

包含书签链接检查、系统健康检查等功能
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .checker import HealthChecker, run_health_check
    from .bookmark_checker import BookmarkHealthChecker

__all__ = ["HealthChecker", "run_health_check", "BookmarkHealthChecker"]


def __getattr__(name: str):
    """按需加载健康检查模块"""
    _mapping = {
        "HealthChecker": (".bookmark_checker", "HealthChecker"),
        "run_health_check": (".checker", "run_health_check"),
        "BookmarkHealthChecker": (".bookmark_checker", "HealthChecker"),
    }
    if name in _mapping:
        module_path, attr_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, attr_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
