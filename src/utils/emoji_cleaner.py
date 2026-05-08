"""
Emoji Cleaner - 标题前缀清理工具

职责：
- 统一移除书签标题开头的指示类 emoji（如 🟢🟡🟠🔴🔥📌⭐❓ 等）
- 保持 KISS：仅做"前缀去除 + 两端空白清理"，不做复杂规范化
- 提供可扩展的 emoji 集合与清理函数接口

注意：此模块现在使用 TextCleaner 实现，保持向后兼容。
"""

from __future__ import annotations

from typing import Iterable, Optional

# 从 TextCleaner 导入实现
from src.utils.text_cleaner import (
    DEFAULT_PREFIX_EMOJIS,
    TextCleaner,
    clean_title as _clean_title,
)

# 向后兼容：保留模块级变量和函数
PREFIX_EMOJIS = DEFAULT_PREFIX_EMOJIS


def clean_title(
    title: Optional[str], extra_prefix_emojis: Optional[Iterable[str]] = None
) -> str:
    """移除标题开头的指示类 emoji 前缀并去除两端空白。

    参数:
    - title: 原始标题
    - extra_prefix_emojis: 额外需要清理的前缀 emoji 列表/集合

    返回:
    - 清理后的标题（若 title 为空则返回空串）
    """
    return _clean_title(title, extra_prefix_emojis)
