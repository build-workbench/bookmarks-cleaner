"""
Emoji Cleaner - 标题前缀清理工具

职责：
- 统一移除书签标题开头的指示类 emoji（如 🟢🟡🟠🔴🔥📌⭐❓ 等）
- 保持 KISS：仅做“前缀去除 + 两端空白清理”，不做复杂规范化
- 提供可扩展的 emoji 集合与清理函数接口
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

# 常见的指示类 emoji，可按需扩展
DEFAULT_PREFIX_EMOJIS = (
    "🟢",
    "🟡",
    "🟠",
    "🔴",  # 置信度色块
    "🔥",
    "📌",
    "⭐",
    "❓",  # 其他指示
)

# 预编译的前缀清理正则：匹配开头连续出现的上述 emoji 和其后的空格
# 注意：使用非捕获分组，允许出现多个连续 emoji + 空格
_PREFIX_RE = re.compile(rf'^(?:[{"".join(DEFAULT_PREFIX_EMOJIS)}]\s*)+')


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
    if not title:
        return ""

    text = str(title)

    # 若指定了额外 emoji，则构建新的正则；否则使用默认预编译
    if extra_prefix_emojis:
        safe = "".join(DEFAULT_PREFIX_EMOJIS) + "".join(extra_prefix_emojis)
        pattern = re.compile(rf"^(?:[{safe}]\s*)+")
        return pattern.sub("", text).strip()

    return _PREFIX_RE.sub("", text).strip()
