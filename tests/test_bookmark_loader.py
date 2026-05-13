"""
测试 BookmarkLoader
"""

import pytest
from src.processing.bookmark_loader import BookmarkLoader


class TestBookmarkLoader:
    """测试 BookmarkLoader"""

    @pytest.fixture
    def loader(self):
        """创建加载器"""
        return BookmarkLoader()

    def test_load_nonexistent_file(self, loader):
        """加载不存在的文件返回空列表"""
        result = loader.load("nonexistent_file.html")
        assert result == []

    def test_load_batch_empty(self, loader):
        """批量加载空列表"""
        result = loader.load_batch([])
        assert result == []

    def test_satisfies_protocol(self):
        """BookmarkLoader 满足 IBookmarkLoader Protocol"""
        from src.interfaces import IBookmarkLoader

        assert hasattr(BookmarkLoader, "load")
        assert hasattr(BookmarkLoader, "load_batch")
