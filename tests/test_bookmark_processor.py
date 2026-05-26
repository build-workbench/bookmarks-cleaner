"""
Tests for Bookmark Processor Module
书签处理器模块测试

重构后使用容器注入进行测试，不再需要 mock 模块级别的导入。
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from src.bookmark_processor import BookmarkProcessor
from src.container import ProcessorContainer
from src.interfaces import ICoordinator, IProcessor


def create_mock_config():
    """创建测试配置"""
    return {
        "category_rules": {
            "编程": {
                "rules": [
                    {
                        "match": "domain",
                        "keywords": ["github.com"],
                        "weight": 15,
                    }
                ]
            }
        },
        "ai_settings": {"confidence_threshold": 0.7},
        "category_order": ["编程"],
    }


def create_mock_coordinator():
    """创建 mock Coordinator"""
    mock = Mock(spec=ICoordinator)
    mock.process_files.return_value = {
        "total_bookmarks": 0,
        "processed_bookmarks": 0,
        "duplicates_removed": 0,
        "errors": 0,
        "processing_time": 0.0,
        "categories_found": {},
        "files_processed": 0,
        "llm_organizer_used": False,
    }
    mock.get_statistics.return_value = {
        "total_bookmarks": 0,
        "processed_bookmarks": 0,
        "duplicates_removed": 0,
        "errors": 0,
        "processing_time": 0.0,
        "categories_found": {},
        "files_processed": 0,
    }
    mock.export_review_queue.return_value = {"items_exported": 0}
    mock.apply_feedback.return_value = {"applied_count": 0}
    mock.train_feedback.return_value = {"trained_samples": 0}
    mock.audit_feedback.return_value = {"audit_backend": "builtin"}
    return mock


def create_mock_health_checker():
    """创建 mock HealthChecker"""
    mock = Mock()
    mock.check_bookmarks.return_value = []
    mock.get_summary.return_value = {
        "accessible_count": 0,
        "total_count": 0,
        "error_count": 0,
    }
    return mock


class TestBookmarkProcessor:
    """BookmarkProcessor 测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例（使用容器注入 mock）"""
        config = create_mock_config()
        mock_coordinator = create_mock_coordinator()
        mock_health_checker = create_mock_health_checker()

        container = ProcessorContainer(
            config=config,
            _coordinator=mock_coordinator,
            _health_checker=mock_health_checker,
        )

        with patch("src.bookmark_processor.load_json_config") as mock_load:
            with patch("src.bookmark_processor.resolve_config_path") as mock_resolve:
                mock_load.return_value = (config, None, True)
                mock_resolve.return_value = (str(tmp_path / "config.json"), True)
                processor = BookmarkProcessor(container=container)
                return processor

    def test_initialization(self, processor):
        """测试初始化"""
        assert processor is not None
        assert processor.config is not None

    def test_initialization_with_injected_container_skips_config_loading(self):
        """测试注入容器时不会额外读取配置文件"""
        config = create_mock_config()
        container = ProcessorContainer(
            config=config,
            _coordinator=create_mock_coordinator(),
            _health_checker=create_mock_health_checker(),
        )

        with patch(
            "src.bookmark_processor.resolve_config_path",
            side_effect=AssertionError("should not resolve config"),
        ), patch(
            "src.bookmark_processor.load_json_config",
            side_effect=AssertionError("should not load config"),
        ):
            processor = BookmarkProcessor(container=container)

        assert processor.config == config
        assert processor._container is container

    def test_process_files_delegates_to_coordinator(self, processor):
        """测试 process_files 委托给 Coordinator"""
        result = processor.process_files(["input.html"])

        # 验证返回值
        assert isinstance(result, dict)
        assert "processed_bookmarks" in result

        # 验证 Coordinator 被调用
        processor._container.coordinator.process_files.assert_called_once()

    def test_health_check_delegates_to_health_checker(self, processor):
        """测试 health_check 委托给 HealthChecker"""
        bookmarks = [{"url": "https://example.com", "title": "Example"}]
        result = processor.health_check(bookmarks)

        # 验证返回值
        assert isinstance(result, dict)
        assert "accessible_count" in result

        # 验证 HealthChecker 被调用
        processor._container.health_checker.check_bookmarks.assert_called_once_with(
            bookmarks
        )

    def test_get_statistics(self, processor):
        """测试统计信息"""
        stats = processor.get_statistics()
        assert isinstance(stats, dict)

    def test_export_review_queue_delegates_to_coordinator(self, processor):
        """测试 export_review_queue 委托给 Coordinator"""
        bookmarks = [{"url": "https://example.com", "title": "Example"}]
        result = processor.export_review_queue(bookmarks)

        assert isinstance(result, dict)
        processor._container.coordinator.export_review_queue.assert_called_once()

    def test_apply_feedback_file_delegates_to_coordinator(self, processor):
        """测试 apply_feedback_file 委托给 Coordinator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
            json.dump({"items": []}, f)
            feedback_path = f.name

        try:
            result = processor.apply_feedback_file(feedback_path)
            assert isinstance(result, dict)
            processor._container.coordinator.apply_feedback.assert_called_once()
        finally:
            Path(feedback_path).unlink(missing_ok=True)

    def test_train_feedback_file_delegates_to_coordinator(self, processor):
        """测试 train_feedback_file 委托给 Coordinator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
            json.dump({"items": []}, f)
            feedback_path = f.name

        try:
            result = processor.train_feedback_file(feedback_path)
            assert isinstance(result, dict)
            processor._container.coordinator.train_feedback.assert_called_once()
        finally:
            Path(feedback_path).unlink(missing_ok=True)

    def test_audit_feedback_file_delegates_to_coordinator(self, processor):
        """测试 audit_feedback_file 委托给 Coordinator"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as f:
            json.dump({"items": []}, f)
            feedback_path = f.name

        try:
            result = processor.audit_feedback_file(feedback_path)
            assert isinstance(result, dict)
            processor._container.coordinator.audit_feedback.assert_called_once()
        finally:
            Path(feedback_path).unlink(missing_ok=True)


class TestProcessorContainer:
    """ProcessorContainer 测试"""

    def test_container_creation(self):
        """测试容器创建"""
        config = create_mock_config()
        container = ProcessorContainer(config=config)
        assert container.config == config

    def test_container_with_coordinator(self):
        """测试容器替换 Coordinator"""
        config = create_mock_config()
        mock_coordinator = create_mock_coordinator()

        container = ProcessorContainer(config=config)
        new_container = container.with_coordinator(mock_coordinator)

        assert new_container._coordinator == mock_coordinator
        assert container._coordinator is None  # 原容器不变

    def test_container_with_health_checker(self):
        """测试容器替换 HealthChecker"""
        config = create_mock_config()
        mock_hc = create_mock_health_checker()

        container = ProcessorContainer(config=config)
        new_container = container.with_health_checker(mock_hc)

        assert new_container._health_checker == mock_hc

    def test_container_coordinator_lazy_init(self):
        """测试 Coordinator 延迟初始化"""
        config = create_mock_config()
        container = ProcessorContainer(config=config)

        # 首次访问触发初始化
        coordinator = container.coordinator
        assert coordinator is not None

        # 再次访问返回同一实例
        assert container.coordinator is coordinator


class TestInterfaces:
    """接口测试"""

    def test_bookmark_processor_implements_iprocessor(self):
        """测试 BookmarkProcessor 实现 IProcessor 接口"""
        # 创建一个最小化的实例用于接口检查
        processor = BookmarkProcessor.__new__(BookmarkProcessor)
        processor.process_files = lambda *a, **k: {}
        processor.health_check = lambda *a, **k: {}
        processor.get_statistics = lambda *a, **k: {}
        processor.export_review_queue = lambda *a, **k: {}
        processor.apply_feedback_file = lambda *a, **k: {}
        processor.train_feedback_file = lambda *a, **k: {}
        processor.audit_feedback_file = lambda *a, **k: {}

        assert isinstance(processor, IProcessor)

    def test_coordinator_implements_icoordinator(self):
        """测试 Coordinator 实现 ICoordinator 接口"""
        from src.pipelines.coordinator import BookmarkProcessorCoordinator

        coordinator = BookmarkProcessorCoordinator(config={})
        assert isinstance(coordinator, ICoordinator)


class TestBookmarkProcessorEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例"""
        config = create_mock_config()
        mock_coordinator = create_mock_coordinator()
        mock_health_checker = create_mock_health_checker()

        container = ProcessorContainer(
            config=config,
            _coordinator=mock_coordinator,
            _health_checker=mock_health_checker,
        )

        with patch("src.bookmark_processor.load_json_config") as mock_load:
            with patch("src.bookmark_processor.resolve_config_path") as mock_resolve:
                mock_load.return_value = (config, None, True)
                mock_resolve.return_value = (str(tmp_path / "config.json"), True)
                return BookmarkProcessor(container=container)

    def test_empty_bookmarks_list(self, processor):
        """测试空书签列表"""
        result = processor.health_check([])
        assert result["total_count"] == 0

    def test_process_files_empty_list(self, processor):
        """测试处理空文件列表"""
        result = processor.process_files([])
        assert isinstance(result, dict)


class TestBookmarkProcessorPerformance:
    """性能测试"""

    @pytest.fixture
    def processor(self, tmp_path):
        """创建处理器实例"""
        config = create_mock_config()
        mock_coordinator = create_mock_coordinator()
        mock_health_checker = create_mock_health_checker()

        container = ProcessorContainer(
            config=config,
            _coordinator=mock_coordinator,
            _health_checker=mock_health_checker,
        )

        with patch("src.bookmark_processor.load_json_config") as mock_load:
            with patch("src.bookmark_processor.resolve_config_path") as mock_resolve:
                mock_load.return_value = (config, None, True)
                mock_resolve.return_value = (str(tmp_path / "config.json"), True)
                return BookmarkProcessor(container=container)

    def test_large_batch_delegation(self, processor):
        """测试大批量委托"""
        # 模拟大批量处理
        mock_coordinator = processor._container.coordinator
        mock_coordinator.process_files.return_value = {
            "total_bookmarks": 10000,
            "processed_bookmarks": 10000,
            "duplicates_removed": 100,
            "errors": 0,
            "processing_time": 10.0,
            "categories_found": {"编程": 5000, "技术": 5000},
            "files_processed": 1,
        }

        result = processor.process_files(["large_file.html"])

        assert result["processed_bookmarks"] == 10000
        assert result["processing_time"] > 0
