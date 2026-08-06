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
