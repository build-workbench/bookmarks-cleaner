"""
Fusion Engine - 分类结果融合引擎

统一的融合逻辑，消除三处重复实现（AIBookmarkClassifier、
ClassifierOrchestrator、ClassifierPipeline）。

深度: 高（简单接口，复杂的加权投票逻辑）
接缝: IFusionEngine Protocol
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from src.plugins.base import BookmarkFeatures, ClassificationResult


class FusionEngine:
    """
    分类结果融合引擎

    使用加权投票融合多个分类器的结果。

    示例:
        engine = FusionEngine()
        result = engine.fuse([result1, result2, result3], features)
    """

    # 默认方法权重
    DEFAULT_WEIGHTS = {
        "rule_engine": 0.50,
        "machine_learning": 0.15,
        "semantic_analyzer": 0.10,
        "user_profiler": 0.10,
        "llm": 0.50,
    }

    def __init__(
        self,
        method_weights: Optional[Dict[str, float]] = None,
        confidence_calibrator: Optional[Callable[[float], float]] = None,
        category_normalizer: Optional[Callable[[str], str]] = None,
    ):
        """
        初始化融合引擎

        Args:
            method_weights: 方法权重覆盖，默认使用 DEFAULT_WEIGHTS
            confidence_calibrator: 可选的置信度校准函数
            category_normalizer: 可选的分类名称标准化函数
        """
        self.method_weights = {**self.DEFAULT_WEIGHTS, **(method_weights or {})}
        self.confidence_calibrator = confidence_calibrator
        self.category_normalizer = category_normalizer
        self.logger = logging.getLogger(__name__)

    def fuse(
        self,
        results: List["ClassificationResult"],
        features: Optional["BookmarkFeatures"] = None,
        confidence_threshold: float = 0.7,
        subcategory_resolver: Optional[Callable[[str, "BookmarkFeatures"], Optional[str]]] = None,
    ) -> "ClassificationResult":
        """
        融合多个分类结果

        Args:
            results: 分类结果列表
            features: 书签特征（用于子分类决策）
            confidence_threshold: 置信度阈值
            subcategory_resolver: 可选的子分类解析函数

        Returns:
            融合后的分类结果
        """
        # 延迟导入避免循环依赖
        from src.plugins.base import ClassificationResult

        # 空结果处理
        if not results:
            return ClassificationResult(
                category="未分类",
                confidence=0.0,
                reasoning=["没有找到合适的分类方法"],
                method="fallback",
            )

        # 加权投票
        category_scores: Dict[str, float] = defaultdict(float)
        category_raw_confidences: Dict[str, float] = {}
        all_reasoning: List[str] = []
        methods_used: List[str] = []
        merged_facets: Dict[str, str] = {}

        for res in results:
            method = res.method
            # 应用分类名称标准化
            if self.category_normalizer:
                category = self.category_normalizer(res.category) or "未分类"
            else:
                category = res.category or "未分类"
            confidence = res.confidence
            reasoning = res.reasoning or []
            facets = res.facets or {}

            weight = self.method_weights.get(method, 0.1)
            category_scores[category] += confidence * weight

            # 保存最高原始置信度
            if (
                category not in category_raw_confidences
                or confidence > category_raw_confidences[category]
            ):
                category_raw_confidences[category] = confidence

            all_reasoning.extend(reasoning)
            methods_used.append(method)

            # 合并分面提示（先到先得）
            for k, v in facets.items():
                if v and k not in merged_facets:
                    merged_facets[k] = v

        if not category_scores:
            return ClassificationResult(
                category="未分类",
                confidence=0.0,
                reasoning=["所有分类方法都失败"],
                method="error",
            )

        # 选择得分最高的类别
        best_category = max(category_scores, key=category_scores.get)
        total_score = sum(category_scores.values())

        # 使用原始置信度
        confidence = category_raw_confidences.get(best_category, 0.0)

        # 置信度校准
        calibrated_confidence = confidence
        if self.confidence_calibrator:
            try:
                calibrated_confidence = self.confidence_calibrator(confidence)
            except Exception as e:
                self.logger.warning(f"置信度校准失败: {e}")

        # 计算备选分类
        alternatives = [
            (cat, score / total_score)
            for cat, score in category_scores.items()
            if cat != best_category and total_score > 0
        ]
        alternatives.sort(key=lambda x: x[1], reverse=True)

        # 解析子分类
        subcategory = None
        if subcategory_resolver and features:
            try:
                subcategory = subcategory_resolver(best_category, features)
            except Exception as e:
                self.logger.debug(f"子分类解析失败: {e}")

        # 构建方法标识
        final_method = "+".join(set(methods_used)) if methods_used else "unknown"

        # 置信度阈值检查
        if best_category != "未分类" and calibrated_confidence < confidence_threshold:
            threshold_reasoning = list(all_reasoning)
            threshold_reasoning.append(
                f"最终置信度 {calibrated_confidence:.2f} 低于阈值 {confidence_threshold:.2f}，标记为未分类"
            )

            threshold_alternatives = [(best_category, calibrated_confidence)]
            for alt in alternatives:
                if alt[0] != best_category:
                    threshold_alternatives.append(alt)

            return ClassificationResult(
                category="未分类",
                subcategory=None,
                confidence=calibrated_confidence,
                reasoning=threshold_reasoning,
                alternatives=threshold_alternatives[:3],
                method=final_method,
                facets=merged_facets,
                score_breakdown={"calibrated_from": confidence} if self.confidence_calibrator else {},
            )

        return ClassificationResult(
            category=best_category,
            subcategory=subcategory,
            confidence=calibrated_confidence,
            reasoning=all_reasoning,
            alternatives=alternatives[:3],
            method=final_method,
            facets=merged_facets,
            score_breakdown={"calibrated_from": confidence} if self.confidence_calibrator else {},
        )

    def update_weight(self, method: str, weight: float) -> None:
        """更新方法权重"""
        self.method_weights[method] = weight

    def get_weights(self) -> Dict[str, float]:
        """获取当前权重"""
        return dict(self.method_weights)


# 模块级单例（可选使用）
_default_engine: Optional[FusionEngine] = None


def get_default_fusion_engine() -> FusionEngine:
    """获取默认融合引擎单例"""
    global _default_engine
    if _default_engine is None:
        _default_engine = FusionEngine()
    return _default_engine
