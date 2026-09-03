"""书签加载器测试"""

from cleanbookmarks.loader import BookmarkLoader


class TestBookmarkLoader:
    def test_load_demo(self):
        loader = BookmarkLoader()
        bookmarks, stats = loader.load_from_files(["examples/demo_bookmarks.html"])
        assert stats["files_loaded"] == 1
        assert stats["total_bookmarks"] > 0
        assert all("url" in b and "title" in b for b in bookmarks)

    def test_invalid_urls_skipped(self):
        loader = BookmarkLoader()
        bookmarks, _ = loader.load_from_files(["examples/demo_bookmarks.html"])
        # All loaded bookmarks should have valid http(s) URLs
        assert all(b["url"].startswith(("http://", "https://")) for b in bookmarks)

    def test_limit(self):
        loader = BookmarkLoader()
        bookmarks, stats = loader.load_from_files(["examples/demo_bookmarks.html"], limit=5)
        assert len(bookmarks) <= 5
