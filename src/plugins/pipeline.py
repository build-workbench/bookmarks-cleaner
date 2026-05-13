"""
Classifier Pipeline - 分类器管道
协调多个分类方法的执行顺序和结果融合
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from .registry import PluginRegistry
from ..services.fusion_engine import FusionEngine

if TYPE_CHECKING:
    from ..plugins.base import BookmarkFeatures, ClassificationResult


class FusionStrategy(Enum):
    """融合策略"""

    WEIGHTED_VOTING = "weighted_voting"
    STACKING = "stacking"
    BAYESIAN = "bayesian"


class ClassifierPipeline:
    """分类器管道"""

    def __init__(self, registry: PluginRegistry, config: Dict[str, Any]):
        """
        初始化分类器管道

        Args:
            registry: 插件注册中心
            config: 配置字典
        """
        self.registry = registry
        self.config = config
        self.fusion_strategy = FusionStrategy(
            config.get("fusion_strategy", "weighted_voting")
        )
        self.method_weights: Dict[str, float] = config.get("method_weights", {})
        self.fusion_engine = FusionEngine(method_weights=self.method_weights)
        self.method_stats: Dict[str, Dict] = defaultdict(
            lambda: {"calls": 0, "errors": 0, "total_time": 0.0}
        )
        self.conflict_rules: Dict[str, str] = config.get("conflict_rules", {})
        self.logger = logging.getLogger(__name__)

    def classify(self, features: "BookmarkFeatures") -> "ClassificationResult":
        """
        执行分类

        Args:
            features: 书签特征对象

        Returns:
            分类结果
        """
        start_time = time.time()
        results: List[Tuple[str, "ClassificationResult"]] = []

        # 按优先级调用所有启用的插件
        for plugin in self.registry.get_enabled_plugins():
            plugin_name = plugin.metadata.name
            self.method_stats[plugin_name]["calls"] += 1

            try:
                plugin_start = time.time()
                result = plugin.classify(features)
                plugin_time = time.time() - plugin_start

                self.method_stats[plugin_name]["total_time"] += plugin_time

                if result:
                    results.append((plugin_name, result))
                    self.logger.debug(
                        f"Plugin '{plugin_name}' classified as '{result.category}' "
                        f"with confidence {result.confidence:.2f}"
                    )
            except Exception as e:
                # 记录错误，继续处理
                self._log_plugin_error(plugin_name, e)
                continue

        if not results:
            return self._default_result()

        # 融合结果
        fused = self._fuse_results(results)

        # 记录处理时间
        fused.processing_time = time.time() - start_time

        return fused

    def classify_batch(
        self, features_list: List["BookmarkFeatures"]
    ) -> List["ClassificationResult"]:
        """
        批量分类

        Args:
            features_list: 书签特征列表

        Returns:
            分类结果列表
        """
        # 检查是否有插件支持批量处理
        batch_plugins = [
            p for p in self.registry.get_enabled_plugins() if p.supports_batch()
        ]

        if batch_plugins:
            # 使用批量处理
            return self._classify_batch_optimized(features_list, batch_plugins)
        else:
            # 逐个处理
            return [self.classify(f) for f in features_list]

    def _classify_batch_optimized(self, features_list, batch_plugins):
        """优化的批量分类"""
        # 简化实现：逐个处理
        return [self.classify(f) for f in features_list]

    def _fuse_results(
        self, results: List[Tuple[str, "ClassificationResult"]]
    ) -> "ClassificationResult":
        """
        融合多个分类结果

        Args:
            results: (插件名, 分类结果) 元组列表

        Returns:
            融合后的分类结果
        """
        # 提取 ClassificationResult 列表
        result_list = [r[1] for r in results]

        # 委托给 FusionEngine
        return self.fusion_engine.fuse(result_list)

    def _weighted_voting(
        self, results: List[Tuple[str, "ClassificationResult"]]
    ) -> "ClassificationResult":
        """
        向后兼容方法，委托给 FusionEngine
        """
        result_list = [r[1] for r in results]
        return self.fusion_engine.fuse(result_list)

    def _stacking(
        self, results: List[Tuple[str, "ClassificationResult"]]
    ) -> "ClassificationResult":
        """向后兼容方法，委托给 FusionEngine"""
        result_list = [r[1] for r in results]
        return self.fusion_engine.fuse(result_list)

    def _bayesian_combination(
        self, results: List[Tuple[str, "ClassificationResult"]]
    ) -> "ClassificationResult":
        """向后兼容方法，委托给 FusionEngine"""
        result_list = [r[1] for r in results]
        return self.fusion_engine.fuse(result_list)

    def _resolve_conflicts(
        self, scores: Dict[str, float], results: List
    ) -> Dict[str, float]:
        """
        应用冲突解决规则

        Args:
            scores: 分类得分字典
            results: 原始结果列表

        Returns:
            调整后的得分字典
        """
        for rule_key, rule_action in self.conflict_rules.items():
            if rule_action == "prefer_rule_engine":
                for method_name, result in results:
                    if "rule" in method_name.lower():
                        scores[result.category] *= 1.5

        return scores

    def _log_plugin_error(self, plugin_name: str, error: Exception):
        """
        记录插件错误

        Args:
            plugin_name: 插件名称
            error: 异常对象
        """
        self.method_stats[plugin_name]["errors"] += 1
        self.logger.error(f"Plugin '{plugin_name}' failed: {error}", exc_info=True)

    def _default_result(self) -> "ClassificationResult":
        """
        返回默认分类结果

        Returns:
            默认分类结果
        """
        from ..classifiers.ai import ClassificationResult

        return ClassificationResult(
            category="未分类",
            confidence=0.0,
            reasoning=["No plugins available or all plugins failed"],
            method="default",
        )

    def update_method_weight(self, method_name: str, accuracy: float):
        """
        根据准确率更新方法权重

        Args:
            method_name: 方法名称
            accuracy: 准确率 (0-1)
        """
        current_weight = self.method_weights.get(method_name, 1.0)
        # 指数移动平均
        alpha = 0.1
        new_weight = alpha * accuracy + (1 - alpha) * current_weight
        self.method_weights[method_name] = new_weight
        self.logger.info(
            f"Updated weight for '{method_name}': {current_weight:.3f} -> {new_weight:.3f}"
        )

    def get_stats(self) -> Dict:
        """
        获取管道统计信息

        Returns:
            统计信息字典
        """
        return {
            "fusion_strategy": self.fusion_strategy.value,
            "method_weights": dict(self.method_weights),
            "method_stats": dict(self.method_stats),
            "enabled_plugins": len(self.registry.get_enabled_plugins()),
        }

    def set_fusion_strategy(self, strategy: str):
        """
        设置融合策略

        Args:
            strategy: 融合策略名称
        """
        try:
            self.fusion_strategy = FusionStrategy(strategy)
            self.logger.info(f"Fusion strategy set to: {strategy}")
        except ValueError:
            self.logger.error(f"Invalid fusion strategy: {strategy}")
            raise
