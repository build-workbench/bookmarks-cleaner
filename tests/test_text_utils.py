"""文本清理工具测试"""

from cleanbookmarks.text_utils import TextCleaner, clean_title, strip_prefix, normalize_category_string, normalize_category_config


class TestCleanTitle:
    def test_removes_emoji_prefix(self):
        assert clean_title("🟢 GitHub") == "GitHub"

    def test_removes_multiple_emoji(self):
        assert clean_title("🟢🟡 标题") == "标题"

    def test_empty(self):
        assert clean_title("") == ""
        assert clean_title(None) == ""

    def test_no_emoji(self):
        assert clean_title("普通标题") == "普通标题"

    def test_extra_emojis(self):
        assert clean_title("✨ 标题", extra_prefix_emojis={"✨"}) == "标题"


class TestStripPrefix:
    def test_strips_emoji(self):
        assert strip_prefix("🔥开发工具") == "开发工具"

    def test_strips_special_chars(self):
        assert strip_prefix("///测试") == "测试"

    def test_preserves_alnum(self):
        assert strip_prefix("GitHub") == "GitHub"

    def test_empty(self):
        assert strip_prefix("") == ""


class TestNormalizeCategoryString:
    def test_simple(self):
        assert normalize_category_string("编程") == "编程"

    def test_with_slash(self):
        assert normalize_category_string("编程/后端") == "编程/后端"

    def test_with_emoji_prefix(self):
        assert normalize_category_string("🔥编程/后端") == "编程/后端"

    def test_empty(self):
        assert normalize_category_string("") == ""


class TestNormalizeCategoryConfig:
    def test_normalizes_category_order(self):
        config = {"category_order": ["🔥编程", "📚学习"]}
        result = normalize_category_config(config)
        assert result["category_order"] == ["编程", "学习"]

    def test_normalizes_category_rules(self):
        config = {"category_rules": {"🔥编程": {"rules": []}}}
        result = normalize_category_config(config)
        assert "编程" in result["category_rules"]
        assert "🔥编程" not in result["category_rules"]

    def test_empty_config(self):
        assert normalize_category_config({}) == {}
        assert normalize_category_config(None) == {}


class TestTextCleanerRules:
    def test_site_prefix_suffix_replacement(self):
        cleaner = TextCleaner(
            prefixes=["登录 |", "Sign in ·"],
            suffixes=["- V2EX", " · GitHub"],
            replacements={"&": "&", "(7条消息)": ""},
        )
        assert cleaner.clean_title("登录 | 首页 - V2EX") == "首页"
        assert cleaner.clean_title("Sign in · GitHub · GitHub") == "GitHub"
        assert cleaner.clean_title("Python 教程(7条消息)") == "Python 教程"

    def test_no_rules_default_unchanged(self):
        cleaner = TextCleaner()
        assert cleaner.clean_title("⭐ 我的收藏") == "我的收藏"
        assert cleaner.clean_title("普通标题 - V2EX") == "普通标题 - V2EX"
