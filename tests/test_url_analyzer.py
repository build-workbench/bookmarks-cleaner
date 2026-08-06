"""URL 分析器测试"""

from cleanbook.url_analyzer import URLAnalyzer, analyze_url


class TestURLAnalyzer:
    def test_github_repo(self):
        a = analyze_url("https://github.com/user/repo")
        assert a.site_type == "github"
        assert a.repo_owner == "user"
        assert a.repo_name == "repo"

    def test_github_issues(self):
        a = analyze_url("https://github.com/user/repo/issues")
        assert a.site_type == "github"
        assert a.content_type == "issues"

    def test_video_youtube(self):
        a = analyze_url("https://www.youtube.com/watch?v=12345")
        assert a.site_type == "video"
        assert a.content_type == "video"

    def test_video_bilibili(self):
        a = analyze_url("https://www.bilibili.com/video/BV1234")
        assert a.site_type == "video"

    def test_docs(self):
        a = analyze_url("https://docs.python.org/3/")
        assert a.site_type == "docs"

    def test_category_hints(self):
        a = analyze_url("https://github.com/user/repo")
        assert len(a.category_hints) > 0
        categories = [h[0] for h in a.category_hints]
        assert any("编程" in c for c in categories)

    def test_language_detection(self):
        a = analyze_url("https://github.com/user/repo/blob/main/app.py")
        assert a.language_hint == "Python"

    def test_invalid_url(self):
        a = analyze_url("not a url")
        assert a.site_type in ("unknown", "website")
