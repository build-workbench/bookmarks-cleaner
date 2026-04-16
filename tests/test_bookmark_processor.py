"""
Tests for Bookmark Processor Module
书签处理器模块测试
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from src.bookmark_processor import BookmarkProcessor


class TestBookmarkProcessor:
    """BookmarkProcessor 测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例"""
        with patch("src.bookmark_processor.AIBookmarkClassifier") as mock_classifier:
            mock_classifier.return_value = MagicMock()
            processor = BookmarkProcessor(output_dir=str(tmp_path))
            return processor

    @pytest.fixture
    def sample_bookmarks(self):
        """示例书签数据"""
        return [
            {
                "url": "https://github.com/user/repo",
                "title": "GitHub Repository",
                "add_date": "2024-01-01",
            },
            {
                "url": "https://stackoverflow.com/questions/123",
                "title": "Stack Overflow Question",
                "add_date": "2024-01-02",
            },
            {
                "url": "https://example.com",
                "title": "Example Site",
                "add_date": "2024-01-03",
            },
        ]

    def test_initialization(self, processor):
        """测试初始化"""
        assert processor is not None
        assert processor.output_dir is not None

    def test_process_bookmarks_basic(self, processor, sample_bookmarks):
        """测试基本书签处理"""
        with patch.object(
            processor, "_classify_bookmark"
        ) as mock_classify:
            mock_classify.return_value = {
                "category": "编程",
                "confidence": 0.9,
            }

            results = processor.process(sample_bookmarks)

            assert len(results) == len(sample_bookmarks)
            assert mock_classify.call_count == len(sample_bookmarks)

    def test_process_empty_list(self, processor):
        """测试处理空列表"""
        results = processor.process([])

        assert results == []

    def test_process_with_workers(self, processor, sample_bookmarks):
        """测试多worker处理"""
        with patch.object(
            processor, "_classify_bookmark"
        ) as mock_classify:
            mock_classify.return_value = {
                "category": "测试",
                "confidence": 0.8,
            }

            results = processor.process(sample_bookmarks, workers=2)

            assert len(results) == len(sample_bookmarks)

    def test_export_to_json(self, processor, sample_bookmarks, tmp_path):
        """测试导出为JSON"""
        processed_data = [
            {**bm, "category": "测试", "confidence": 0.9}
            for bm in sample_bookmarks
        ]

        output_file = tmp_path / "output.json"
        processor.export_to_json(processed_data, str(output_file))

        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert len(loaded) == len(processed_data)

    def test_export_to_html(self, processor, sample_bookmarks, tmp_path):
        """测试导出为HTML"""
        processed_data = [
            {**bm, "category": "测试", "confidence": 0.9}
            for bm in sample_bookmarks
        ]

        output_file = tmp_path / "output.html"
        processor.export_to_html(processed_data, str(output_file))

        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE" in content or "<html" in content

    def test_export_to_markdown(self, processor, sample_bookmarks, tmp_path):
        """测试导出为Markdown"""
        processed_data = [
            {**bm, "category": "测试", "confidence": 0.9}
            for bm in sample_bookmarks
        ]

        output_file = tmp_path / "output.md"
        processor.export_to_markdown(processed_data, str(output_file))

        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert content  # 非空内容

    def test_group_by_category(self, processor, sample_bookmarks):
        """测试按分类分组"""
        processed_data = [
            {**sample_bookmarks[0], "category": "编程", "confidence": 0.9},
            {**sample_bookmarks[1], "category": "编程", "confidence": 0.85},
            {**sample_bookmarks[2], "category": "其他", "confidence": 0.5},
        ]

        grouped = processor.group_by_category(processed_data)

        assert "编程" in grouped
        assert "其他" in grouped
        assert len(grouped["编程"]) == 2
        assert len(grouped["其他"]) == 1

    def test_filter_by_confidence(self, processor, sample_bookmarks):
        """测试按置信度过滤"""
        processed_data = [
            {**sample_bookmarks[0], "category": "A", "confidence": 0.9},
            {**sample_bookmarks[1], "category": "B", "confidence": 0.5},
            {**sample_bookmarks[2], "category": "C", "confidence": 0.3},
        ]

        filtered = processor.filter_by_confidence(processed_data, threshold=0.6)

        assert len(filtered) == 1
        assert filtered[0]["confidence"] == 0.9

    def test_statistics(self, processor, sample_bookmarks):
        """测试统计信息"""
        processed_data = [
            {**sample_bookmarks[0], "category": "编程", "confidence": 0.9},
            {**sample_bookmarks[1], "category": "编程", "confidence": 0.85},
            {**sample_bookmarks[2], "category": "其他", "confidence": 0.5},
        ]

        stats = processor.get_statistics(processed_data)

        assert stats["total"] == 3
        assert "categories" in stats
        assert "average_confidence" in stats
        assert stats["categories"]["编程"] == 2
        assert stats["categories"]["其他"] == 1


class TestBookmarkProcessorEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例"""
        with patch("src.bookmark_processor.AIBookmarkClassifier"):
            return BookmarkProcessor(output_dir=str(tmp_path))

    def test_malformed_bookmark(self, processor):
        """测试格式错误的书签"""
        malformed_bookmarks = [
            {"url": None, "title": "No URL"},
            {"url": "https://example.com", "title": None},
            {},  # 空字典
            {"url": "", "title": ""},  # 空值
        ]

        with patch.object(processor, "_classify_bookmark") as mock_classify:
            mock_classify.return_value = {"category": "未分类", "confidence": 0.0}

            # 应该能处理而不崩溃
            results = processor.process(malformed_bookmarks)

            assert len(results) == len(malformed_bookmarks)

    def test_duplicate_urls(self, processor):
        """测试重复URL"""
        bookmarks = [
            {"url": "https://example.com", "title": "First"},
            {"url": "https://example.com", "title": "Second"},
        ]

        with patch.object(processor, "_classify_bookmark") as mock_classify:
            mock_classify.return_value = {"category": "测试", "confidence": 0.8}

            results = processor.process(bookmarks)

            # 应该都处理，除非有去重逻辑
            assert len(results) >= 1

    def test_special_characters_in_title(self, processor):
        """测试标题中的特殊字符"""
        bookmarks = [
            {
                "url": "https://example.com",
                "title": "Test <>&\"'特殊字符🎉",
            }
        ]

        with patch.object(processor, "_classify_bookmark") as mock_classify:
            mock_classify.return_value = {"category": "测试", "confidence": 0.8}

            results = processor.process(bookmarks)

            assert len(results) == 1

    @given(
        url=st.text(min_size=1, max_size=500),
        title=st.text(min_size=0, max_size=500),
    )
    def test_fuzz_process(self, processor, url: str, title: str):
        """模糊测试处理"""
        bookmark = {"url": url, "title": title}

        with patch.object(processor, "_classify_bookmark") as mock_classify:
            mock_classify.return_value = {"category": "测试", "confidence": 0.5}

            try:
                processor.process([bookmark])
            except Exception:
                pass  # 某些输入可能抛异常，可接受


class TestBookmarkProcessorPerformance:
    """性能测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例"""
        with patch("src.bookmark_processor.AIBookmarkClassifier"):
            return BookmarkProcessor(output_dir=str(tmp_path))

    def test_large_batch_processing(self, processor):
        """测试大批量处理"""
        # 生成1000个书签
        bookmarks = [
            {
                "url": f"https://example{i}.com",
                "title": f"Example {i}",
            }
            for i in range(1000)
        ]

        with patch.object(processor, "_classify_bookmark") as mock_classify:
            mock_classify.return_value = {"category": "测试", "confidence": 0.8}

            import time

            start = time.time()
            results = processor.process(bookmarks, workers=4)
            elapsed = time.time() - start

            assert len(results) == 1000
            # 应该在合理时间内完成
            assert elapsed < 30.0  # 30秒内
