"""
Bookmark Processor - 书签处理器门面类

负责提供书签处理的完整功能入口，内部委托给 BookmarkProcessorCoordinator 协调各个 Pipeline。

架构说明:
    此模块是主要的入口点，内部使用 ProcessorContainer 管理 BookmarkProcessorCoordinator
    协调各个 Pipeline。对于简单的处理流程，可以直接使用 BookmarkProcessorCoordinator。

    BookmarkProcessor 提供了额外的功能:
    - 健康检查（通过 HealthChecker）
    - LLM 整理器集成（可选）
    - 依赖注入支持（通过 ProcessorContainer）

    所有核心处理流程委托给 Coordinator，包括：
    - 书签加载（BookmarkLoader Pipeline）
    - 去重（DeduplicationPipeline）
    - 分类（ClassificationPipeline）
    - 组织（OrganizationPipeline）
    - 导出（ExportPipeline）
    - 反馈（FeedbackPipeline）

深度: 高（简单接口，隐藏复杂的处理流程）
接缝: 通过 ProcessorContainer 支持组件替换

重构历史:
    原始实现是一个 1148 行的上帝类，承担了过多职责。
    重构后（当前实现）是一个约 350 行的门面类，核心逻辑委托给 Pipeline 架构。
"""

from __future__ import annotations

import importlib
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

from src.container import ProcessorContainer
from src.utils.category import normalize_category_config, normalize_category_string
from src.utils.resource_loader import load_json_config, resolve_config_path

if TYPE_CHECKING:
    from src.interfaces import IProcessor

RuntimeLLMBookmarkOrganizer: Any = None
try:
    _llm_module = importlib.import_module("src.llm.organizer")
except ImportError:
    pass
else:
    RuntimeLLMBookmarkOrganizer = getattr(_llm_module, "LLMBookmarkOrganizer", None)


class BookmarkProcessor:
    """书签处理器门面类

    职责：
    1. 保持向后兼容的公共接口
    2. 委托核心处理流程给 Coordinator
    3. 提供额外功能（health_check、LLM Organizer）

    示例:
        # 默认创建
        processor = BookmarkProcessor(config_path="config.json")
        stats = processor.process_files(["bookmarks.html"])

        # 使用容器注入 mock 组件（测试）
        from unittest.mock import Mock
        container = ProcessorContainer(config={}, _coordinator=Mock())
        processor = BookmarkProcessor(container=container)
    """

    # 命名常量
    MAX_WORKERS_LIMIT = 32

    def __init__(
        self,
        config_path: str | None = None,
        max_workers: int = 4,
        use_ml: bool = True,
        confidence_threshold: Optional[float] = None,
        container: Optional[ProcessorContainer] = None,
    ):
        """初始化书签处理器

        Args:
            config_path: 配置文件路径
            max_workers: 最大并行线程数
            use_ml: 是否启用机器学习
            confidence_threshold: 置信度阈值
            container: 依赖注入容器（用于测试）
        """
        # 限制线程数
        self.max_workers = min(max_workers, self.MAX_WORKERS_LIMIT)
        self.use_ml = use_ml

        # 解析置信度阈值
        self.confidence_threshold: Optional[float] = None
        if confidence_threshold is not None:
            try:
                ct = float(confidence_threshold)
                if ct < 0:
                    ct = 0.0
                if ct > 1:
                    ct = 1.0
                self.confidence_threshold = ct
            except (TypeError, ValueError):
                self.confidence_threshold = None

        self.logger = logging.getLogger(__name__)

        container_instance: ProcessorContainer

        if container is not None:
            injected_config_path = (
                config_path if config_path is not None else container.config_path
            )
            self.config_path = (
                str(injected_config_path) if injected_config_path is not None else ""
            )
            self._explicit_config = injected_config_path is not None
            self.config = self._normalize_category_config(container.config)
        else:
            resolved_path, self._explicit_config = resolve_config_path(config_path)
            self.config_path = str(resolved_path)
            loaded_config, _, explicit = load_json_config(self.config_path)
            self.config = self._normalize_category_config(loaded_config)
            self._explicit_config = explicit

        # 验证配置
        if not isinstance(
            self.config.get("category_rules"), dict
        ) or not self.config.get("category_rules"):
            source = "显式配置" if self._explicit_config else "默认配置"
            raise ValueError(f"{source}缺少有效的 category_rules: {self.config_path}")

        # 更新 AI 设置
        ai_settings = self.config.get("ai_settings")
        if not isinstance(ai_settings, dict):
            ai_settings = {}
            self.config["ai_settings"] = ai_settings

        if max_workers is not None:
            ai_settings["max_workers"] = self.max_workers

        if use_ml is not None:
            ai_settings["enable_learning"] = bool(use_ml)

        self.confidence_threshold = (
            ai_settings.get("confidence_threshold")
            if self.confidence_threshold is None
            else self.confidence_threshold
        )

        if self.confidence_threshold is not None:
            ai_settings["confidence_threshold"] = self.confidence_threshold

        # 初始化容器
        if container is None:
            container_instance = ProcessorContainer(
                config=self.config,
                config_path=self.config_path,
                max_workers=self.max_workers,
                confidence_threshold=self.confidence_threshold,
            )
        else:
            container.config = self.config
            container.config_path = container.config_path or self.config_path
            container.max_workers = self.max_workers
            container.confidence_threshold = self.confidence_threshold
            container_instance = container

        self._container: ProcessorContainer = container_instance

        # LLM 整理器（可选）
        self._llm_organizer: Optional[Any] = None
        self.llm_organizer_meta: Optional[Dict] = None

        # 统计信息（兼容旧接口）
        self.stats: Dict[str, Any] = {}

    def _normalize_category_config(self, config: Dict) -> Dict:
        """标准化分类配置"""
        return normalize_category_config(config)

    def _normalize_category_string(self, category: str) -> str:
        """标准化分类字符串"""
        return normalize_category_string(category)

    @property
    def llm_organizer(self) -> Optional[Any]:
        """延迟初始化 LLM 整理器"""
        if self._llm_organizer is None and RuntimeLLMBookmarkOrganizer is not None:
            try:
                self._llm_organizer = RuntimeLLMBookmarkOrganizer(
                    config_path=self.config_path, config=self.config
                )
            except Exception as exc:
                self.logger.warning(f"LLM organizer init failed: {exc}")
                self._llm_organizer = None
        return self._llm_organizer

    # ==================== 核心方法 ====================

    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
        review_queue_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """处理多个书签文件

        Args:
            input_files: HTML 文件路径列表
            output_dir: 输出目录
            train_models: 是否训练模型
            limit: 限制处理的书签数量
            review_queue_path: 复核队列输出路径

        Returns:
            处理统计信息
        """
        start_time = time.time()

        self.logger.info(f"开始处理 {len(input_files)} 个文件")

        # 委托给 Coordinator
        self.stats = self._container.coordinator.process_files(
            input_files=input_files,
            output_dir=output_dir,
            train_models=train_models,
            limit=limit,
            review_queue_path=review_queue_path,
        )

        # 可选：LLM 整理器后处理
        self._apply_llm_organizer_if_enabled()

        # 更新处理时间
        self.stats["processing_time"] = time.time() - start_time

        self.logger.info(f"处理完成: {self.stats.get('processed_bookmarks', 0)} 个书签已分类")

        return self.stats

    def _apply_llm_organizer_if_enabled(self) -> None:
        """如果启用，应用 LLM 整理器"""
        self.llm_organizer_meta = None
        self.stats["llm_organizer_used"] = False
        self.stats.pop("llm_organizer_meta", None)

        if self.llm_organizer and self.llm_organizer.enabled():
            try:
                # 获取已组织的书签（需要从 Coordinator 获取）
                # 注意：这需要 Coordinator 暴露已组织的书签
                # 当前实现：跳过 LLM 整理，因为 Coordinator 不暴露内部数据
                self.logger.info("LLM Organizer 已启用，但当前 Coordinator 不支持后处理")
            except Exception as exc:
                self.logger.warning(f"LLM organizer execution failed: {exc}")

    def health_check(self, bookmarks: List[Dict]) -> Dict[str, Any]:
        """对书签进行健康检查

        Args:
            bookmarks: 书签列表

        Returns:
            健康检查结果摘要
        """
        self.logger.info(f"开始健康检查 {len(bookmarks)} 个书签...")

        health_checker: Any = self._container.health_checker
        results = health_checker.check_bookmarks(bookmarks)
        summary = health_checker.get_summary(results)

        self.logger.info(
            f"健康检查完成: {summary['accessible_count']}/{summary['total_count']} 个链接可访问"
        )

        return cast(Dict[str, Any], summary)

    def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息

        Returns:
            统计信息字典
        """
        # 合并 Coordinator 的统计
        coordinator: Any = self._container.coordinator
        coordinator_stats = coordinator.get_statistics()

        # 计算 BPS
        processing_time = coordinator_stats.get("processing_time", 0.0)
        processed_bookmarks = coordinator_stats.get("processed_bookmarks", 0)
        total_bookmarks = coordinator_stats.get("total_bookmarks", 1)

        return {
            **coordinator_stats,
            "processing_speed_bps": processed_bookmarks / max(processing_time, 0.001),
            "success_rate_percent": (processed_bookmarks / max(total_bookmarks, 1)) * 100,
        }

    # ==================== 反馈方法（委托给 Coordinator） ====================

    def export_review_queue(
        self, classified_bookmarks: List[Dict], output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """导出低置信度复核队列

        Args:
            classified_bookmarks: 已分类的书签列表
            output_path: 输出文件路径

        Returns:
            导出统计信息
        """
        coordinator: Any = self._container.coordinator
        return cast(
            Dict[str, Any],
            coordinator.export_review_queue(classified_bookmarks, output_path),
        )

    def apply_feedback_file(self, feedback_path: str) -> Dict[str, Any]:
        """应用反馈数据

        Args:
            feedback_path: 反馈文件路径

        Returns:
            应用统计信息
        """
        coordinator: Any = self._container.coordinator
        return cast(Dict[str, Any], coordinator.apply_feedback(feedback_path))

    def train_feedback_file(self, feedback_path: str) -> Dict[str, Any]:
        """使用反馈数据训练模型

        Args:
            feedback_path: 反馈文件路径

        Returns:
            训练统计信息
        """
        coordinator: Any = self._container.coordinator
        return cast(Dict[str, Any], coordinator.train_feedback(feedback_path))

    def audit_feedback_file(
        self, feedback_path: str, output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """审核反馈数据质量

        Args:
            feedback_path: 反馈文件路径
            output_path: 审核报告输出路径

        Returns:
            审核统计信息
        """
        coordinator: Any = self._container.coordinator
        return cast(
            Dict[str, Any],
            coordinator.audit_feedback(feedback_path, output_path),
        )

    # ==================== 兼容性属性 ====================

    @property
    def classifier(self):
        """兼容性属性：获取分类器"""
        return self._container.classifier

    @property
    def deduplicator(self):
        """兼容性属性：获取去重器"""
        # 委托给 Coordinator 的去重 Pipeline
        coordinator: Any = self._container.coordinator
        return coordinator.deduplication

    @property
    def exporter(self):
        """兼容性属性：获取导出器"""
        # 委托给 Coordinator 的导出 Pipeline
        coordinator: Any = self._container.coordinator
        return coordinator.export_pipeline.exporter

    @property
    def active_learning_engine(self):
        """兼容性属性：获取主动学习引擎"""
        return self._container.active_learning_engine

    @property
    def incremental_trainer(self):
        """兼容性属性：获取增量训练器"""
        return self._container.incremental_trainer
