"""
TextCleaner - 统一的文本清理工具

整合分散在多个模块中的文本清理逻辑，提供统一的接口。
用于替换 emoji_cleaner.py、category.py 中的清理函数和 standardizer.py 中的 _strip_prefix。

特性：
- 移除标题开头的指示类 emoji
- 移除分类名称中的非文字前缀
- 支持自定义 emoji 集合
- 线程安全
"""

from __future__ import annotations

import re
from typing import Iterable, Optional, Set

# 常见的指示类 emoji，可按需扩展
DEFAULT_PREFIX_EMOJIS: Set[str] = {
    "🟢",  # 置信度色块 - 高
    "🟡",  # 置信度色块 - 中
    "🟠",  # 置信度色块 - 中低
    "🔴",  # 置信度色块 - 低
    "🔥",  # 其他指示
    "📌",
    "⭐",
    "❓",
}

# 预编译的前缀清理正则：匹配开头连续出现的上述 emoji 和其后的空格
_EMOJI_PATTERN = re.compile(rf'^(?:[{"".join(DEFAULT_PREFIX_EMOJIS)}]\s*)+')


class TextCleaner:
    """统一的文本清理工具类
    
    提供多种文本清理功能，用于书签标题和分类名称的规范化。
    
    示例：
        cleaner = TextCleaner()
        
        # 清理标题中的 emoji
        title = cleaner.clean_title("🟢 GitHub - 代码托管平台")
        # 结果: "GitHub - 代码托管平台"
        
        # 移除非文字前缀
        category = cleaner.strip_prefix("🔥开发工具")
        # 结果: "开发工具"
        
        # 规范化分类名称
        name = cleaner.normalize_category_name("  🟢 技术/编程  ")
        # 结果: "技术/编程"
    """
    
    def __init__(
        self,
        extra_emojis: Optional[Set[str]] = None,
        strip_whitespace: bool = True
    ):
        """初始化文本清理器
        
        Args:
            extra_emojis: 额外需要清理的 emoji 集合
            strip_whitespace: 是否在清理后去除两端空白
        """
        self._extra_emojis = extra_emojis or set()
        self._strip_whitespace = strip_whitespace
        
        # 构建 emoji 模式
        all_emojis = DEFAULT_PREFIX_EMOJIS | self._extra_emojis
        if all_emojis:
            safe = "".join(sorted(all_emojis))
            self._emoji_pattern = re.compile(rf"^(?:[{safe}]\s*)+")
        else:
            self._emoji_pattern = None
    
    def clean_title(
        self,
        title: Optional[str],
        extra_prefix_emojis: Optional[Iterable[str]] = None
    ) -> str:
        """移除标题开头的指示类 emoji 前缀并去除两端空白
        
        Args:
            title: 原始标题
            extra_prefix_emojis: 额外需要清理的前缀 emoji 列表/集合
            
        Returns:
            清理后的标题（若 title 为空则返回空串）
        """
        if not title:
            return ""
        
        text = str(title)
        
        # 使用实例级别的 emoji 模式
        pattern = self._emoji_pattern
        
        # 若指定了额外 emoji，则构建新的正则
        if extra_prefix_emojis:
            all_emojis = DEFAULT_PREFIX_EMOJIS | set(extra_prefix_emojis)
            safe = "".join(sorted(all_emojis))
            pattern = re.compile(rf"^(?:[{safe}]\s*)+")
        
        if pattern:
            text = pattern.sub("", text)
        
        return text.strip() if self._strip_whitespace else text
    
    def strip_prefix(self, text: Optional[str]) -> str:
        """移除文本中的 emoji 等非文字前缀，保留中文/字母/数字起始的内容
        
        Args:
            text: 原始文本
            
        Returns:
            移除前缀后的文本
        """
        if not text:
            return ""
        s = str(text)
        # 如果要去除空白，先去除
        if self._strip_whitespace:
            s = s.strip()
        else:
            # 只去除左侧空白以便正确识别前缀
            s = s.lstrip()
        
        i = 0
        while i < len(s) and not ("\u4e00" <= s[i] <= "\u9fff" or s[i].isalnum()):
            i += 1
        result = s[i:] if i < len(s) else s
        
        # 如果要去除空白，去除两端空白
        if self._strip_whitespace:
            result = result.strip()
        
        return result
    
    def normalize_category_name(self, text: Optional[str]) -> str:
        """规范化分类名称
        
        执行以下清理：
        1. 移除两端空白
        2. 移除 emoji 前缀
        3. 移除非文字前缀
        
        Args:
            text: 原始分类名称
            
        Returns:
            规范化后的分类名称
        """
        if not text:
            return ""
        
        # 先移除非文字前缀（更通用）
        result = self.strip_prefix(text)
        
        # 再移除 emoji 前缀（针对 emoji 特殊处理）
        if result and self._emoji_pattern:
            result = self._emoji_pattern.sub("", result)
        
        return result.strip() if self._strip_whitespace else result


# 全局实例，用于模块级别的便捷函数
_default_cleaner = TextCleaner()


def clean_title(
    title: Optional[str],
    extra_prefix_emojis: Optional[Iterable[str]] = None
) -> str:
    """移除标题开头的指示类 emoji 前缀（模块级便捷函数）
    
    Args:
        title: 原始标题
        extra_prefix_emojis: 额外需要清理的前缀 emoji 列表/集合
        
    Returns:
        清理后的标题
    """
    return _default_cleaner.clean_title(title, extra_prefix_emojis)


def strip_prefix(text: Optional[str]) -> str:
    """移除非文字前缀（模块级便捷函数）
    
    Args:
        text: 原始文本
        
    Returns:
        移除前缀后的文本
    """
    return _default_cleaner.strip_prefix(text)


def normalize_category_name(text: Optional[str]) -> str:
    """规范化分类名称（模块级便捷函数）
    
    Args:
        text: 原始分类名称
        
    Returns:
        规范化后的分类名称
    """
    return _default_cleaner.normalize_category_name(text)
