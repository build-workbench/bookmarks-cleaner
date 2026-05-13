"""
utils - 工具函数模块

包含配置管理、URL 分析、分类工具等辅助功能
"""

# 从 category 导入函数
from .category import (
    normalize_category_config,
    normalize_category_string,
    strip_category_prefix,
)

# 从 resource_loader 导入函数和异常
from .resource_loader import (
    ResourceResolutionError,
    default_config_path,
    load_json_config,
    resolve_config_path,
    resolve_taxonomy_path,
)


# ConfigManager 延迟导入以避免循环依赖
def __getattr__(name: str):
    if name == "ConfigManager":
        from src.config_manager import EnhancedConfigManager

        return EnhancedConfigManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ConfigManager",
    "strip_category_prefix",
    "normalize_category_string",
    "normalize_category_config",
    "ResourceResolutionError",
    "resolve_config_path",
    "load_json_config",
    "resolve_taxonomy_path",
    "default_config_path",
]
