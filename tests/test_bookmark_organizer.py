"""测试书签组织器"""

import pytest
from src.processing.bookmark_organizer import BookmarkOrganizer


def test_organize_bookmarks():
    """测试基本书签组织"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "Python Tutorial", "subject": "编程", "resource_type": "教程"},
        {"title": "ML Guide", "subject": "编程", "resource_type": "教程"},
        {"title": "AI News", "subject": "人工智能", "resource_type": "资讯"},
    ]

    result = organizer.organize(bookmarks)

    assert "编程" in result
    assert "人工智能" in result
    assert "教程" in result["编程"]
    assert "资讯" in result["人工智能"]
    assert len(result["编程"]["教程"]) == 2
    assert len(result["人工智能"]["资讯"]) == 1


def test_organize_with_default_values():
    """测试使用默认值的组织"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "Example", "url": "https://example.com"},
        {"title": "Another", "url": "https://another.com"},
    ]

    result = organizer.organize(bookmarks)

    assert "未分类" in result
    assert "网页" in result["未分类"]
    assert len(result["未分类"]["网页"]) == 2


def test_organize_with_sorting():
    """测试书签排序"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "Zebra", "subject": "编程", "resource_type": "教程"},
        {"title": "Apple", "subject": "编程", "resource_type": "教程"},
        {"title": "Banana", "subject": "编程", "resource_type": "教程"},
    ]

    result = organizer.organize(bookmarks)

    # 验证排序（按标题字母顺序）
    titles = [b["title"] for b in result["编程"]["教程"]]
    assert titles == ["Apple", "Banana", "Zebra"]


def test_organize_with_taxonomy_standardizer():
    """测试使用分类法标准化器"""
    organizer = BookmarkOrganizer()

    # 创建一个简单的模拟标准化器
    class MockStandardizer:
        def normalize_subject(self, subject):
            return subject.upper()

        def normalize_resource_type(self, resource_type):
            return resource_type.title()

    bookmarks = [
        {"title": "Test", "subject": "编程", "resource_type": "教程"},
    ]

    result = organizer.organize(bookmarks, taxonomy_standardizer=MockStandardizer())

    # 验证标准化后的主题
    assert "编程".upper() in result
    assert "教程".title() in result["编程".upper()]


def test_get_statistics():
    """测试统计信息"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "Python Tutorial", "subject": "编程", "resource_type": "教程"},
        {"title": "ML Guide", "subject": "编程", "resource_type": "教程"},
        {"title": "AI News", "subject": "人工智能", "resource_type": "资讯"},
        {"title": "Web Dev", "subject": "编程", "resource_type": "文档"},
    ]

    organized = organizer.organize(bookmarks)
    stats = organizer.get_statistics(organized)

    assert stats["total"] == 4
    assert stats["subject_count"] == 2
    assert stats["subjects"]["编程"] == 3
    assert stats["subjects"]["人工智能"] == 1
    assert stats["resource_types"]["教程"] == 2
    assert stats["resource_types"]["资讯"] == 1
    assert stats["resource_types"]["文档"] == 1


def test_organize_empty_bookmarks():
    """测试空书签列表"""
    organizer = BookmarkOrganizer()
    result = organizer.organize([])

    assert result == {}


def test_organize_with_missing_fields():
    """测试缺失字段的处理"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "No Subject", "resource_type": "文档"},
        {"title": "No Type", "subject": "编程"},
        {"title": "Only Title"},
    ]

    result = organizer.organize(bookmarks)

    # 验证使用默认值
    assert "未分类" in result
    assert "网页" in result["未分类"]


def test_multiple_resource_types_per_subject():
    """测试一个主题下多种资源类型"""
    organizer = BookmarkOrganizer()
    bookmarks = [
        {"title": "Tutorial 1", "subject": "编程", "resource_type": "教程"},
        {"title": "Doc 1", "subject": "编程", "resource_type": "文档"},
        {"title": "Tool 1", "subject": "编程", "resource_type": "工具"},
    ]

    result = organizer.organize(bookmarks)

    assert len(result["编程"]) == 3
    assert "教程" in result["编程"]
    assert "文档" in result["编程"]
    assert "工具" in result["编程"]


def test_statistics_with_empty_organized():
    """测试空组织结构的统计"""
    organizer = BookmarkOrganizer()
    stats = organizer.get_statistics({})

    assert stats["total"] == 0
    assert stats["subject_count"] == 0
    assert stats["subjects"] == {}
    assert stats["resource_types"] == {}
