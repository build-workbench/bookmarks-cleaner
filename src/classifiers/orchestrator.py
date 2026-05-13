"""
Classifier Orchestrator - 分类器编排器

使用 PluginRegistry 注册和编排分类器，替代硬编码的分类器调用顺序。

深度: 高（简单接口，复杂的编排和融合逻辑）
接口: orchestrate(features) -> ClassificationResult

特性:
- 通过 PluginRegistry 管理分类器生命周期
- 按优先级编排分类器调用
- 支持动态启用/禁用分类器
- 委托给 FusionEngine 进行结果融合
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from src.plugins.base import BookmarkFeatures, ClassificationResult
from src.plugins.registry import PluginRegistry
from src.services.fusion_engine import FusionEngine

if TYPE_CHECKING:
    from src.plugins.base import ClassifierPlugin


class ClassifierOrchestrator:
    """分类器编排器

    使用插件系统编排多个分类器，委托给 FusionEngine 进行结果融合。

    示例:
        orchestrator = ClassifierOrchestrator()
        orchestrator.register_default_plugins(config)

        result = orchestrator.orchestrate(features)
    """

    # 默认方法权重（与 FusionEngine 保持一致）
    DEFAULT_WEIGHTS = {
        "rule_engine": 0.50,
        "machine_learning": 0.15,
        "semantic_analyzer": 0.10,
        "user_profiler": 0.10,
        "llm": 0.50,
    }

    def __init__(
        self,
        registry: Optional[PluginRegistry] = None,
        method_weights: Optional[Dict[str, float]] = None,
        fusion_engine: Optional[FusionEngine] = None,
    ):
        """初始化编排器

        Args:
            registry: 可选的 PluginRegistry 实例，如果不提供则创建新实例
            method_weights: 可选的方法权重覆盖
            fusion_engine: 可选的 FusionEngine 实例，如果不提供则创建新实例
        """
        self.registry = registry or PluginRegistry()
        self.method_weights = {**self.DEFAULT_WEIGHTS, **(method_weights or {})}
        self.fusion_engine = fusion_engine or FusionEngine(
            method_weights=self.method_weights
        )
        self.logger = logging.getLogger(__name__)
        self._initialized = False

    def register_plugin(self, plugin: "ClassifierPlugin", enable: bool = True) -> bool:
        """注册分类器插件

        Args:
            plugin: 分类器插件实例
            enable: 是否立即启用

        Returns:
            注册是否成功
        """
        if not self.registry.register(plugin):
            return False

        if enable:
            self.registry.enable(plugin.metadata.name)

        return True

    def initialize_all(self, config: Dict) -> bool:
        """初始化所有已注册的插件

        Args:
            config: 配置字典

        Returns:
            是否所有插件都初始化成功
        """
        success = True
        for name in self.registry.list_plugins():
            plugin = self.registry.get_plugin(name)
            if plugin is not None:
                try:
                    if not plugin.initialize(config):
                        self.logger.warning(f"插件 {name} 初始化失败")
                        success = False
                except Exception as e:
                    self.logger.error(f"插件 {name} 初始化异常: {e}")
                    success = False

        self._initialized = success
        return success

    def orchestrate(
        self,
        features: BookmarkFeatures,
        confidence_threshold: float = 0.7,
    ) -> ClassificationResult:
        """编排分类器调用并融合结果

        Args:
            features: 书签特征
            confidence_threshold: 置信度阈值

        Returns:
            融合后的分类结果
        """
        # 获取已启用的插件（按优先级排序）
        plugins = self.registry.get_enabled_plugins()

        if not plugins:
            return ClassificationResult(
                category="未分类",
                confidence=0.0,
                reasoning=["没有可用的分类器"],
                method="fallback",
            )

        # 收集所有分类器的结果
        results: List[ClassificationResult] = []

        for plugin in plugins:
            try:
                result = plugin.classify(features)
                if result is not None:
                    results.append(result)
            except Exception as e:
                self.logger.debug(f"分类器 {plugin.metadata.name} 执行失败: {e}")

        # 委托给 FusionEngine 融合结果
        return self.fusion_engine.fuse(results, features, confidence_threshold)

    # _ensemble 方法已移至 FusionEngine，保留向后兼容委托
    def _ensemble(
        self,
        results: List[ClassificationResult],
        features: BookmarkFeatures,
        confidence_threshold: float,
        methods_used: List[str],
    ) -> ClassificationResult:
        """向后兼容方法，委托给 FusionEngine"""
        return self.fusion_engine.fuse(results, features, confidence_threshold)

    def get_enabled_classifiers(self) -> List[str]:
        """获取已启用的分类器名称列表"""
        return [p.metadata.name for p in self.registry.get_enabled_plugins()]

    def enable_classifier(self, name: str) -> bool:
        """启用指定分类器"""
        return self.registry.enable(name)

    def disable_classifier(self, name: str) -> bool:
        """禁用指定分类器"""
        return self.registry.disable(name)

    def shutdown(self) -> None:
        """关闭所有分类器"""
        for name in self.registry.list_plugins():
            self.registry.unregister(name)
        self._initialized = False
        self.logger.info("ClassifierOrchestrator 已关闭")
