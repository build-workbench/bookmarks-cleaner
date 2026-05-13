"""
测试 FeedbackService
"""

import pytest
from src.services.feedback_service import FeedbackService


class TestFeedbackService:
    """测试 FeedbackService"""

    @pytest.fixture
    def service(self):
        """创建反馈服务"""
        config = {
            "feedback_loop": {"enabled": False},
            "active_learning_settings": {"enabled": False},
        }
        return FeedbackService(config)

    def test_export_review_queue_disabled(self, service):
        """反馈未启用时导出返回空"""
        result = service.export_review_queue([], "output.json")
        assert result["items_exported"] == 0

    def test_load_feedback_items_empty(self, service, tmp_path):
        """加载空反馈文件"""
        feedback_file = tmp_path / "feedback.json"
        feedback_file.write_text('{"items": []}')

        items = service.load_feedback_items(str(feedback_file))
        assert items == []

    def test_load_feedback_items_list(self, service, tmp_path):
        """加载列表格式反馈文件"""
        feedback_file = tmp_path / "feedback.json"
        feedback_file.write_text('[{"bookmark_id": "1", "correct_category": "技术"}]')

        items = service.load_feedback_items(str(feedback_file))
        assert len(items) == 1
        assert items[0]["bookmark_id"] == "1"

    def test_apply_feedback_disabled(self, service):
        """反馈未启用时应用抛出异常"""
        with pytest.raises(ValueError, match="feedback_loop 未启用"):
            service.apply_feedback("feedback.json")


class TestFeedbackServiceProtocol:
    """测试 FeedbackService 接口"""

    def test_has_required_methods(self):
        """FeedbackService 有必要的方法"""
        assert hasattr(FeedbackService, "export_review_queue")
        assert hasattr(FeedbackService, "apply_feedback")
        assert hasattr(FeedbackService, "train_from_feedback")
