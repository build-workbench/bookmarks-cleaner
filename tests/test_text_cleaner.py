"""
TextCleaner 单元测试

测试统一的文本清理工具功能。
"""

import pytest
from src.utils.text_cleaner import TextCleaner, clean_title, strip_prefix, normalize_category_name


class TestTextCleaner:
    """TextCleaner 测试套件"""
    
    def test_clean_title_basic(self):
        """测试基本的标题清理"""
        cleaner = TextCleaner()
        
        # 移除 emoji 前缀
        assert cleaner.clean_title("🟢 GitHub") == "GitHub"
        assert cleaner.clean_title("🟡 低置信度") == "低置信度"
        assert cleaner.clean_title("🟠 中等") == "中等"
        assert cleaner.clean_title("🔴 低") == "低"
        
        # 移除多个 emoji
        assert cleaner.clean_title("🟢🟡 GitHub") == "GitHub"
        
        # 保留非前缀 emoji
        assert cleaner.clean_title("GitHub 🌟") == "GitHub 🌟"
    
    def test_clean_title_empty(self):
        """测试空标题清理"""
        cleaner = TextCleaner()
        
        assert cleaner.clean_title("") == ""
        assert cleaner.clean_title(None) == ""
        assert cleaner.clean_title("   ") == ""
    
    def test_clean_title_no_emoji(self):
        """测试无 emoji 标题"""
        cleaner = TextCleaner()
        
        assert cleaner.clean_title("GitHub") == "GitHub"
        assert cleaner.clean_title("  GitHub  ") == "GitHub"
    
    def test_clean_title_with_extra_emojis(self):
        """测试额外 emoji 清理"""
        cleaner = TextCleaner()
        
        # 使用额外 emoji
        result = cleaner.clean_title("🎯 目标", extra_prefix_emojis=["🎯"])
        assert result == "目标"
        
        # 不使用额外 emoji
        result = cleaner.clean_title("🎯 目标")
        assert result == "🎯 目标"
    
    def test_strip_prefix_chinese(self):
        """测试中文前缀保留"""
        cleaner = TextCleaner()
        
        # 中文开头应该保留
        assert cleaner.strip_prefix("开发工具") == "开发工具"
        assert cleaner.strip_prefix("  开发工具  ") == "开发工具"
    
    def test_strip_prefix_emoji(self):
        """测试 emoji 前缀移除"""
        cleaner = TextCleaner()
        
        # emoji 开头应该被移除
        assert cleaner.strip_prefix("🔥开发工具") == "开发工具"
        assert cleaner.strip_prefix("🟢🟡开发工具") == "开发工具"
    
    def test_strip_prefix_alphanumeric(self):
        """测试字母数字前缀保留"""
        cleaner = TextCleaner()
        
        # 字母数字开头应该保留
        assert cleaner.strip_prefix("API") == "API"
        assert cleaner.strip_prefix("123abc") == "123abc"
    
    def test_strip_prefix_mixed(self):
        """测试混合前缀"""
        cleaner = TextCleaner()
        
        # 混合情况
        assert cleaner.strip_prefix("🔥 API") == "API"
        assert cleaner.strip_prefix("🟢 开发工具") == "开发工具"
    
    def test_strip_prefix_empty(self):
        """测试空前缀"""
        cleaner = TextCleaner()
        
        assert cleaner.strip_prefix("") == ""
        assert cleaner.strip_prefix(None) == ""
        assert cleaner.strip_prefix("   ") == ""
    
    def test_normalize_category_name(self):
        """测试分类名称规范化"""
        cleaner = TextCleaner()
        
        # 基本规范化
        assert cleaner.normalize_category_name("  开发工具  ") == "开发工具"
        assert cleaner.normalize_category_name("🔥开发工具") == "开发工具"
        assert cleaner.normalize_category_name("🟢 技术/编程") == "技术/编程"
    
    def test_normalize_category_name_with_slash(self):
        """测试带斜杠的分类名称"""
        cleaner = TextCleaner()
        
        assert cleaner.normalize_category_name("技术/编程") == "技术/编程"
        assert cleaner.normalize_category_name("🔥 技术/编程") == "技术/编程"
    
    def test_normalize_category_name_empty(self):
        """测试空分类名称"""
        cleaner = TextCleaner()
        
        assert cleaner.normalize_category_name("") == ""
        assert cleaner.normalize_category_name(None) == ""
    
    def test_custom_cleaner_with_extra_emojis(self):
        """测试自定义清理器"""
        extra_emojis = {"🎯", "🚀"}
        cleaner = TextCleaner(extra_emojis=extra_emojis)
        
        # 自定义 emoji 应该被清理
        assert cleaner.clean_title("🎯 目标") == "目标"
        assert cleaner.clean_title("🚀 发布") == "发布"
        
        # 默认 emoji 也应该被清理
        assert cleaner.clean_title("🟢 GitHub") == "GitHub"
    
    def test_cleaner_without_strip_whitespace(self):
        """测试不去除空白的清理器（只保留右侧空白）"""
        cleaner = TextCleaner(strip_whitespace=False)
        
        # strip_prefix 会去除左侧空白以便识别前缀，但保留右侧空白
        assert cleaner.strip_prefix("  开发工具  ") == "开发工具  "
        assert cleaner.strip_prefix("🔥开发工具  ") == "开发工具  "
    
    def test_module_level_functions(self):
        """测试模块级便捷函数"""
        # clean_title
        assert clean_title("🟢 GitHub") == "GitHub"
        
        # strip_prefix
        assert strip_prefix("🔥开发工具") == "开发工具"
        
        # normalize_category_name
        assert normalize_category_name("🔥 开发工具") == "开发工具"


class TestTextCleanerConsistency:
    """测试 TextCleaner 与现有实现的一致性"""
    
    def test_consistency_with_emoji_cleaner(self):
        """测试与 emoji_cleaner 的一致性"""
        from src.utils.emoji_cleaner import clean_title as emoji_clean_title
        
        test_cases = [
            "🟢 GitHub - 代码托管平台",
            "🟡 低置信度书签",
            "🟠 中等置信度",
            "🔴 低置信度",
            "🔥 热门书签",
            "📌 重要",
            "⭐ 收藏",
            "❓ 未知",
            "🟢🟡 双 emoji",
            "GitHub",
            "",
        ]
        
        for case in test_cases:
            expected = emoji_clean_title(case)
            actual = clean_title(case)
            assert actual == expected, f"不一致于 '{case}': expected='{expected}', actual='{actual}'"
    
    def test_consistency_with_category_strip(self):
        """测试与 category.strip_category_prefix 的一致性"""
        from src.utils.category import strip_category_prefix as category_strip
        
        test_cases = [
            "开发工具",
            "🔥开发工具",
            "🟢 技术",
            "API",
            "123abc",
            "",
            "   ",
        ]
        
        for case in test_cases:
            expected = category_strip(case)
            actual = strip_prefix(case)
            assert actual == expected, f"不一致于 '{case}': expected='{expected}', actual='{actual}'"
