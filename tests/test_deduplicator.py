"""去重器测试"""

from cleanbook.deduplicator import BookmarkDeduplicator


class TestBookmarkDeduplicator:
    def test_exact_url_match(self):
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://example.com", "title": "Example"},
            {"url": "https://example.com", "title": "Example Duplicate"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 1
        assert len(duplicates) == 1

    def test_no_duplicates(self):
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://a.com", "title": "A"},
            {"url": "https://b.com", "title": "B"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 2
        assert len(duplicates) == 0

    def test_tracking_params_ignored(self):
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://example.com/page?utm_source=feed", "title": "Page"},
            {"url": "https://example.com/page", "title": "Page"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 1

    def test_empty(self):
        d = BookmarkDeduplicator()
        unique, duplicates = d.remove_duplicates([])
        assert unique == []
        assert duplicates == []

    def test_similar_paths_not_duplicates(self):
        """回归：短路径仅 1 字符差异（如年份不同）不得误判为重复"""
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://example.com/2018/talks/announcements", "title": "Talks 2018"},
            {"url": "https://example.com/2019/talks/announcements", "title": "Talks 2019"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 2
        assert len(duplicates) == 0

    def test_same_path_different_fragment_is_duplicate(self):
        """同路径仅 fragment 不同 -> 重复"""
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://example.com/page#section1", "title": "Page A"},
            {"url": "https://example.com/page#section2", "title": "Page B"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 1
        assert len(duplicates) == 1

    def test_same_path_different_query_not_duplicate(self):
        """回归：同路径但 query 决定内容（搜索/分页/ID 变体）不得误判为重复"""
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://github.com/search?q=python", "title": "Search python"},
            {"url": "https://github.com/search?q=java", "title": "Search java"},
            {"url": "https://example.com/list?page=1", "title": "List 1"},
            {"url": "https://example.com/list?page=2", "title": "List 2"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 4
        assert len(duplicates) == 0

    def test_calibration_matrix(self):
        """去重判定校准矩阵：防误删回归（年份差异/不同文章/跨域不得判重）"""
        d = BookmarkDeduplicator()
        cases = [
            # (b1, b2, 期望判定)
            ({"url": "https://example.com/2018/talks/announcements", "title": "Talks 2018"},
             {"url": "https://example.com/2019/talks/announcements", "title": "Talks 2019"}, False),
            ({"url": "https://github.com/user/repo", "title": "GitHub - user/repo"},
             {"url": "https://github.com/user/repo", "title": "user/repo - GitHub"}, True),
            ({"url": "https://example.com/page?utm_source=feed", "title": "Page"},
             {"url": "https://example.com/page", "title": "Page"}, True),
            ({"url": "https://example.com/page#a", "title": "Page A"},
             {"url": "https://example.com/page#b", "title": "Page B"}, True),
            ({"url": "https://a.com/x", "title": "Article One"},
             {"url": "https://b.com/x", "title": "Article One"}, False),
            ({"url": "https://example.com/docs/python", "title": "Python 教程"},
             {"url": "https://example.com/docs/python", "title": "Python 教程(2024)"}, True),
            ({"url": "https://example.com/blog/post-1", "title": "Post 1"},
             {"url": "https://example.com/blog/post-2", "title": "Post 2"}, False),
            ({"url": "http://www.example.com/page?a=1&b=2", "title": "X"},
             {"url": "https://example.com/page?b=2&a=1", "title": "X"}, True),
            ({"url": "https://example.com/a", "title": "Python 教程"},
             {"url": "https://example.com/b", "title": "Python 教程"}, True),
        ]
        for b1, b2, expect in cases:
            got = d._are_duplicates(b1, b2)
            assert got == expect, f"{b1} vs {b2}: 期望 {expect}, 实际 {got}"

    def test_select_best_bookmark(self):
        d = BookmarkDeduplicator()
        bookmarks = [
            {"url": "https://example.com/long?utm_source=x", "title": "Short"},
            {"url": "https://example.com/long", "title": "A Much Longer And More Descriptive Title"},
        ]
        unique, duplicates = d.remove_duplicates(bookmarks)
        assert len(unique) == 1
        # The one with better quality should be kept
        assert unique[0]["title"] == "A Much Longer And More Descriptive Title"
