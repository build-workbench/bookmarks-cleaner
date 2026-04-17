"""
llm - LLM 相关模块

包含 LLM 分类器、组织者、提示词构建等
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .classifier import LLMClassifier
    from .organizer import LLMBookmarkOrganizer
    from .prompt_builder import LLMPromptBuilder
    from .second_pass import SecondPassPrompt
    from .exporter import PromptExporter

__all__ = [
    "LLMClassifier",
    "LLMBookmarkOrganizer",
    "LLMPromptBuilder",
    "SecondPassPrompt",
    "PromptExporter",
]


def __getattr__(name: str):
    """按需加载 LLM 模块"""
    _mapping = {
        "LLMClassifier": (".classifier", "LLMClassifier"),
        "LLMBookmarkOrganizer": (".organizer", "LLMBookmarkOrganizer"),
        "LLMPromptBuilder": (".prompt_builder", "LLMPromptBuilder"),
        "SecondPassPromptGenerator": (".second_pass", "SecondPassPromptGenerator"),
        "PromptExporter": (".exporter", "export_llm_prompt"),
    }
    if name in _mapping:
        module_path, cls_name = _mapping[name]
        import importlib
        module = importlib.import_module(module_path, __name__)
        return getattr(module, cls_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
