"""
ProcessorContainer - 处理器组件容器

集中管理 BookmarkProcessor 的所有依赖组件，支持：
- 默认组件自动创建
- 自定义组件注入
- 组件替换（用于测试）

深度: 高（简单接口，隐藏复杂的组件创建逻辑）
接缝: 所有组件都可以通过接口替换
"""

from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from src.interfaces import ICoordinator, IHealthChecker


@dataclasses.dataclass
class ProcessorContainer:
    """处理器组件容器

    使用 dataclass 实现，支持：
    - 默认组件延迟创建
    - 组件注入
    - 链式替换（with_* 方法）

    示例:
        # 默认创建
        container = ProcessorContainer(config={})

        # 注入 mock 用于测试
        from unittest.mock import Mock
        mock_coordinator = Mock()
        container = ProcessorContainer(config={}, _coordinator=mock_coordinator)

        # 链式替换
        container = ProcessorContainer(config={}).with_coordinator(custom_coordinator)
    """

    # 配置
    config: Dict[str, Any]
    config_path: Optional[str] = None
    max_workers: int = 4
    confidence_threshold: Optional[float] = None

    # 可注入组件（内部使用，以 _ 开头）
    _coordinator: Optional["ICoordinator"] = dataclasses.field(default=None, repr=False)
    _health_checker: Optional["IHealthChecker"] = dataclasses.field(default=None, repr=False)
    _classifier: Optional[Any] = dataclasses.field(default=None, repr=False)
    _active_learning_engine: Optional[Any] = dataclasses.field(default=None, repr=False)
    _incremental_trainer: Optional[Any] = dataclasses.field(default=None, repr=False)

    # 内部状态
    _logger: Optional[logging.Logger] = dataclasses.field(default=None, repr=False)

    def _get_logger(self) -> logging.Logger:
        """获取日志器"""
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    @property
    def coordinator(self) -> "ICoordinator":
        """获取协调器（延迟创建）"""
        if self._coordinator is None:
            from src.pipelines.coordinator import BookmarkProcessorCoordinator

            self._coordinator = BookmarkProcessorCoordinator(
                config=self.config,
                config_path=self.config_path,
                classifier=self.classifier,
                max_workers=self.max_workers,
                confidence_threshold=self.confidence_threshold,
                active_learning_engine=self.active_learning_engine,
                incremental_trainer=self.incremental_trainer,
            )
        return self._coordinator

    @property
    def health_checker(self) -> "IHealthChecker":
        """获取健康检查器（延迟创建）"""
        if self._health_checker is None:
            from src.health.checker import HealthChecker

            self._health_checker = HealthChecker(max_workers=self.max_workers)
        return self._health_checker

    @property
    def classifier(self) -> Optional[Any]:
        """获取分类器（延迟创建）"""
        if self._classifier is None:
            # 延迟导入避免循环依赖
            from src.classifiers.ai import AIBookmarkClassifier

            try:
                self._classifier = AIBookmarkClassifier(
                    config=self.config,
                    config_path=self.config_path,
                )
            except Exception as e:
                self._get_logger().warning(f"分类器创建失败: {e}")
                self._classifier = None
        return self._classifier

    @property
    def active_learning_engine(self) -> Optional[Any]:
        """获取主动学习引擎（延迟创建）"""
        if self._active_learning_engine is None:
            try:
                from src.services.active_learning import ActiveLearningEngine

                # 合并配置（与原始 BookmarkProcessor 保持一致）
                feedback_config = dict(
                    self.config.get("active_learning_settings", {}) or {}
                )
                feedback_config.update(self.config.get("feedback_loop", {}) or {})

                if feedback_config.get("enabled", False):
                    # 设置置信度阈值
                    if "confidence_threshold" not in feedback_config:
                        feedback_config["confidence_threshold"] = self.config.get(
                            "ai_settings", {}
                        ).get("confidence_threshold", 0.7)
                    self._active_learning_engine = ActiveLearningEngine(feedback_config)
            except ImportError:
                self._get_logger().debug("ActiveLearningEngine 模块未安装")
                self._active_learning_engine = None
            except Exception as e:
                self._get_logger().warning(f"主动学习引擎创建失败: {e}")
                self._active_learning_engine = None
        return self._active_learning_engine

    @property
    def incremental_trainer(self) -> Optional[Any]:
        """获取增量训练器（延迟创建）"""
        if self._incremental_trainer is None:
            try:
                from src.services.incremental_trainer import IncrementalTrainer
                from src.services.feedback_model import FeedbackIncrementalModel

                feedback_config = dict(self.config.get("feedback_loop", {}) or {})
                if feedback_config.get("enabled", False):
                    self._incremental_trainer = IncrementalTrainer(feedback_config)
                    self._incremental_trainer.set_model(FeedbackIncrementalModel())
            except ImportError:
                self._get_logger().debug("IncrementalTrainer 模块未安装")
                self._incremental_trainer = None
            except Exception as e:
                self._get_logger().warning(f"增量训练器创建失败: {e}")
                self._incremental_trainer = None
        return self._incremental_trainer

    # ==================== 链式替换方法 ====================

    def with_coordinator(self, coordinator: "ICoordinator") -> "ProcessorContainer":
        """替换协调器（支持链式调用）

        Args:
            coordinator: 新的协调器实例

        Returns:
            新的容器实例
        """
        return dataclasses.replace(self, _coordinator=coordinator)

    def with_health_checker(self, health_checker: "IHealthChecker") -> "ProcessorContainer":
        """替换健康检查器（支持链式调用）

        Args:
            health_checker: 新的健康检查器实例

        Returns:
            新的容器实例
        """
        return dataclasses.replace(self, _health_checker=health_checker)

    def with_classifier(self, classifier: Any) -> "ProcessorContainer":
        """替换分类器（支持链式调用）

        Args:
            classifier: 新的分类器实例

        Returns:
            新的容器实例
        """
        return dataclasses.replace(self, _classifier=classifier)

    def with_active_learning_engine(self, engine: Any) -> "ProcessorContainer":
        """替换主动学习引擎（支持链式调用）

        Args:
            engine: 新的主动学习引擎实例

        Returns:
            新的容器实例
        """
        return dataclasses.replace(self, _active_learning_engine=engine)

    def with_incremental_trainer(self, trainer: Any) -> "ProcessorContainer":
        """替换增量训练器（支持链式调用）

        Args:
            trainer: 新的增量训练器实例

        Returns:
            新的容器实例
        """
        return dataclasses.replace(self, _incremental_trainer=trainer)
