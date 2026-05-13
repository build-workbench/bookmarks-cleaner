"""
Pipeline 模块单元测试

测试各个 Pipeline 模块的基本功能。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List

from src.pipelines import (
    BookmarkLoader,
    DeduplicationPipeline,
    ClassificationPipeline,
    OrganizationPipeline,
    ExportPipeline,
    FeedbackPipeline,
)


class TestBookmarkLoader:
    """BookmarkLoader 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        loader = BookmarkLoader(max_workers=4)
        assert loader.max_workers == 4
        assert loader.stats["total_bookmarks"] == 0

    def test_is_valid_url(self):
        """测试 URL 验证"""
        loader = BookmarkLoader()

        # 有效 URL
        assert loader._is_valid_url("https://github.com") is True
        assert loader._is_valid_url("http://example.com") is True

        # 无效 URL
        assert loader._is_valid_url("") is False
        assert loader._is_valid_url("javascript:void(0)") is False
        assert loader._is_valid_url("data:text/html,<h1>Test</h1>") is False
        assert loader._is_valid_url("mailto:test@example.com") is False
        assert loader._is_valid_url("ftp://example.com") is False

    def test_stats_reset(self):
        """测试统计重置"""
        loader = BookmarkLoader()
        loader.stats["total_bookmarks"] = 100
        loader._reset_stats()
        assert loader.stats["total_bookmarks"] == 0


class TestDeduplicationPipeline:
    """DeduplicationPipeline 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        pipeline = DeduplicationPipeline(similarity_threshold=0.9)
        assert pipeline.similarity_threshold == 0.9
        assert pipeline.enable_fast_dedup is True
        assert pipeline.enable_advanced_dedup is True

    def test_fast_url_dedup(self):
        """测试快速 URL 去重"""
        pipeline = DeduplicationPipeline()

        bookmarks = [
            {"url": "https://example.com", "title": "Example"},
            {"url": "https://github.com", "title": "GitHub"},
            {"url": "https://example.com", "title": "Example Duplicate"},
        ]

        unique, duplicates = pipeline._fast_url_dedup(bookmarks)

        assert len(unique) == 2
        assert len(duplicates) == 1
        assert duplicates[0]["title"] == "Example Duplicate"

    def test_deduplicate_empty(self):
        """测试空列表去重"""
        pipeline = DeduplicationPipeline()

        unique, duplicates, stats = pipeline.deduplicate([])

        assert len(unique) == 0
        assert len(duplicates) == 0
        assert stats["input_count"] == 0

    def test_deduplicate_no_duplicates(self):
        """测试无重复去重"""
        pipeline = DeduplicationPipeline(enable_advanced_dedup=False)

        bookmarks = [
            {"url": "https://example.com", "title": "Example"},
            {"url": "https://github.com", "title": "GitHub"},
        ]

        unique, duplicates, stats = pipeline.deduplicate(bookmarks)

        assert len(unique) == 2
        assert stats["duplicates_removed"] == 0


class TestClassificationPipeline:
    """ClassificationPipeline 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        mock_classifier = Mock()
        pipeline = ClassificationPipeline(
            config={}, classifier=mock_classifier, max_workers=2, cache_size=1000
        )

        assert pipeline.max_workers == 2
        assert pipeline.classifier == mock_classifier

    def test_classify_empty(self):
        """测试空列表分类"""
        mock_classifier = Mock()
        pipeline = ClassificationPipeline(config={}, classifier=mock_classifier)

        classified, stats = pipeline.classify_batch([])

        assert len(classified) == 0
        assert stats["classified_count"] == 0


class TestOrganizationPipeline:
    """OrganizationPipeline 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        mock_standardizer = Mock()
        pipeline = OrganizationPipeline(mock_standardizer)

        assert pipeline.standardizer == mock_standardizer

    def test_organize_empty(self):
        """测试空列表组织"""
        mock_standardizer = Mock()
        pipeline = OrganizationPipeline(mock_standardizer)

        organized, stats = pipeline.organize([], {})

        assert len(organized) == 0
        assert stats["total_subjects"] == 0


class TestExportPipeline:
    """ExportPipeline 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        mock_exporter = Mock()
        pipeline = ExportPipeline(mock_exporter)

        assert pipeline.exporter == mock_exporter
        assert "html" in pipeline.default_formats
        assert "json" in pipeline.default_formats
        assert "markdown" in pipeline.default_formats

    def test_invalid_format(self):
        """测试无效格式"""
        mock_exporter = Mock()
        pipeline = ExportPipeline(mock_exporter)

        with pytest.raises(ValueError, match="不支持的导出格式"):
            pipeline.export_all({}, "output", formats=["invalid"])


class TestFeedbackPipeline:
    """FeedbackPipeline 测试套件"""

    def test_initialization(self):
        """测试初始化"""
        pipeline = FeedbackPipeline(config={})

        assert pipeline.active_learning_engine is None
        assert pipeline.incremental_trainer is None
        assert pipeline.classifier is None

    def test_export_review_queue_without_engine(self):
        """测试无引擎时导出复核队列"""
        pipeline = FeedbackPipeline(config={})

        result = pipeline.export_review_queue([], "test.json")

        assert result["items_exported"] == 0

    def test_apply_feedback_without_engine(self):
        """测试无引擎时应用反馈"""
        pipeline = FeedbackPipeline(config={})

        with pytest.raises(ValueError, match="feedback_loop 未启用"):
            pipeline.apply_feedback("test.json")

    def test_train_feedback_without_trainer(self):
        """测试无训练器时训练反馈"""
        pipeline = FeedbackPipeline(config={})

        with pytest.raises(ValueError, match="feedback_loop 未启用"):
            pipeline.train_feedback("test.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
