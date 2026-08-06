"""文本清理工具"""

from __future__ import annotations

import re
from typing import Iterable, Optional, Set

DEFAULT_PREFIX_EMOJIS: Set[str] = {
    "🟢", "🟡", "🟠", "🔴", "🔥", "📌", "⭐", "❓",
}

_EMOJI_PATTERN = re.compile(rf'^(?:[{"".join(DEFAULT_PREFIX_EMOJIS)}]\s*)+')


class TextCleaner:
    """统一的文本清理工具"""

    def __init__(self, extra_emojis: Optional[Set[str]] = None, strip_whitespace: bool = True):
        self._strip_whitespace = strip_whitespace
        all_emojis = DEFAULT_PREFIX_EMOJIS | (extra_emojis or set())
        safe = "".join(sorted(all_emojis))
        self._emoji_pattern = re.compile(rf"^(?:[{safe}]\s*)+") if safe else None

    def clean_title(self, title: Optional[str], extra_prefix_emojis: Optional[Iterable[str]] = None) -> str:
        if not title:
            return ""
        text = str(title)
        pattern = self._emoji_pattern
        if extra_prefix_emojis:
            all_emojis = DEFAULT_PREFIX_EMOJIS | set(extra_prefix_emojis)
            safe = "".join(sorted(all_emojis))
            pattern = re.compile(rf"^(?:[{safe}]\s*)+")
        if pattern:
            text = pattern.sub("", text)
        return text.strip() if self._strip_whitespace else text

    def strip_prefix(self, text: Optional[str]) -> str:
        """移除 emoji 等非文字前缀，保留中文/字母/数字起始的内容"""
        if not text:
            return ""
        s = str(text).strip() if self._strip_whitespace else str(text).lstrip()
        i = 0
        while i < len(s) and not ("\u4e00" <= s[i] <= "\u9fff" or s[i].isalnum()):
            i += 1
        result = s[i:] if i < len(s) else s
        return result.strip() if self._strip_whitespace else result


_default_cleaner = TextCleaner()


def clean_title(title: Optional[str], extra_prefix_emojis: Optional[Iterable[str]] = None) -> str:
    return _default_cleaner.clean_title(title, extra_prefix_emojis)


def strip_prefix(text: Optional[str]) -> str:
    return _default_cleaner.strip_prefix(text)


def normalize_category_string(category: str) -> str:
    """规范化分类字符串（支持 '主类/子类' 格式）"""
    if not category:
        return ""
    cat = str(category).strip()
    if not cat:
        return ""
    if "/" in cat:
        main, sub = cat.split("/", 1)
        main_n = strip_prefix(main)
        sub_n = strip_prefix(sub)
        return f"{main_n}/{sub_n}" if sub_n else main_n
    return strip_prefix(cat)


def normalize_category_config(config: dict) -> dict:
    """规范化配置字典中所有分类相关的键名"""
    if not isinstance(config, dict):
        return {}
    normalized = dict(config)

    order = normalized.get("category_order")
    if isinstance(order, list):
        normalized["category_order"] = [strip_prefix(x) for x in order if str(x).strip()]

    dgr = normalized.get("domain_grouping_rules")
    if isinstance(dgr, dict):
        new_dgr: dict = {}
        for k, v in dgr.items():
            nk = strip_prefix(k)
            if not nk:
                continue
            if nk in new_dgr and isinstance(new_dgr[nk], list) and isinstance(v, list):
                new_dgr[nk].extend(v)
            else:
                new_dgr[nk] = v
        normalized["domain_grouping_rules"] = new_dgr

    pr = normalized.get("priority_rules")
    if isinstance(pr, dict):
        normalized["priority_rules"] = {
            normalize_category_string(k): v
            for k, v in pr.items()
            if normalize_category_string(k)
        }

    cr = normalized.get("category_rules")
    if isinstance(cr, dict):
        normalized["category_rules"] = {
            normalize_category_string(k): v
            for k, v in cr.items()
            if normalize_category_string(k)
        }

    return normalized
