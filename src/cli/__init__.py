"""
cli - 命令行界面模块

包含交互式 CLI、向导模式等命令行接口
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .enhanced import EnhancedCLI
    from .interface import CLIInterface

__all__ = ["CLIInterface", "EnhancedCLI", "main"]


def __getattr__(name: str):
    """按需加载 CLI 模块"""
    _mapping = {
        "CLIInterface": (".interface", "CLIInterface"),
        "EnhancedCLI": (".enhanced", "EnhancedCLI"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib

        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main():
    """CLI 主入口"""
    from .interface import main as interface_main

    return interface_main()
