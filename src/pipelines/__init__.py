"""
Pipeline 模块 - 书签处理流水线

将 BookmarkProcessor 的职责拆分为独立的 Pipeline 模块，
每个 Pipeline 负责一个特定的处理阶段。

Pipeline:
- BookmarkLoader: 书签加载与解析
- DeduplicationPipeline: 去重处理
- ClassificationPipeline: 分类处理
- OrganizationPipeline: 组织与排序
- ExportPipeline: 导出处理
- FeedbackPipeline: 反馈循环管理
- BookmarkProcessorCoordinator: 协调层
"""

from .bookmark_loader import BookmarkLoader
from .classification_pipeline import ClassificationPipeline
from .coordinator import BookmarkProcessorCoordinator
from .deduplication_pipeline import DeduplicationPipeline
from .export_pipeline import ExportPipeline
from .feedback_pipeline import FeedbackPipeline
from .organization_pipeline import OrganizationPipeline

__all__ = [
    "BookmarkLoader",
    "BookmarkProcessorCoordinator",
    "ClassificationPipeline",
    "DeduplicationPipeline",
    "ExportPipeline",
    "FeedbackPipeline",
    "OrganizationPipeline",
]
