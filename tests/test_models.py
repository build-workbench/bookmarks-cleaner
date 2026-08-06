"""数据结构测试"""

from cleanbook.models import BookmarkFeatures, ClassificationResult


class TestBookmarkFeatures:
    def test_from_url_title(self):
        f = BookmarkFeatures.from_url_title("https://github.com/user/repo", "Test", "code_repository", "en")
        assert f.domain == "github.com"
        assert f.path_segments == ["user", "repo"]
        assert f.content_type == "code_repository"
        assert f.language == "en"

    def test_is_secure(self):
        f = BookmarkFeatures.from_url_title("https://example.com", "Test")
        assert f.is_secure is True
        f2 = BookmarkFeatures.from_url_title("http://example.com", "Test")
        assert f2.is_secure is False

    def test_has_chinese(self):
        f = BookmarkFeatures.from_url_title("https://example.com", "中文标题")
        assert f.has_chinese is True
        f2 = BookmarkFeatures.from_url_title("https://example.com", "English")
        assert f2.has_chinese is False


class TestClassificationResult:
    def test_defaults(self):
        r = ClassificationResult(category="编程", confidence=0.9)
        assert r.subcategory is None
        assert r.reasoning == []
        assert r.alternatives == []
        assert r.method == "unknown"

    def test_alternative_categories(self):
        r = ClassificationResult(category="编程", confidence=0.9, alternatives=[("AI", 0.1)])
        assert r.alternative_categories == [("AI", 0.1)]
