"""分类结果融合引擎 - 加权投票"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Callable, Dict, List, Optional

from cleanbook.models import BookmarkFeatures, ClassificationResult

logger = logging.getLogger(__name__)


class FusionEngine:
    """加权投票融合多个分类器的结果"""

    DEFAULT_WEIGHTS = {
        "rule_engine": 0.50,
        "machine_learning": 0.15,
        "llm": 0.50,
    }

    def __init__(
        self,
        method_weights: Optional[Dict[str, float]] = None,
        category_normalizer: Optional[Callable[[str], str]] = None,
    ):
        self.method_weights = {**self.DEFAULT_WEIGHTS, **(method_weights or {})}
        self.category_normalizer = category_normalizer
        self.logger = logging.getLogger(__name__)

    def fuse(
        self,
        results: List[ClassificationResult],
        features: Optional[BookmarkFeatures] = None,
        confidence_threshold: float = 0.7,
        subcategory_resolver: Optional[Callable[[str, BookmarkFeatures], Optional[str]]] = None,
    ) -> ClassificationResult:
        if not results:
            return ClassificationResult(
                category="未分类", confidence=0.0,
                reasoning=["没有找到合适的分类方法"], method="fallback",
            )

        category_scores: Dict[str, float] = defaultdict(float)
        category_raw_confidences: Dict[str, float] = {}
        all_reasoning: List[str] = []
        methods_used: List[str] = []
        merged_facets: Dict[str, str] = {}

        for res in results:
            method = res.method
            if self.category_normalizer:
                category = self.category_normalizer(res.category) or "未分类"
            else:
                category = res.category or "未分类"
            confidence = res.confidence
            weight = self.method_weights.get(method, 0.1)
            category_scores[category] += confidence * weight
            if category not in category_raw_confidences or confidence > category_raw_confidences[category]:
                category_raw_confidences[category] = confidence
            all_reasoning.extend(res.reasoning or [])
            methods_used.append(method)
            for k, v in (res.facets or {}).items():
                if v and k not in merged_facets:
                    merged_facets[k] = v

        if not category_scores:
            return ClassificationResult(
                category="未分类", confidence=0.0,
                reasoning=["所有分类方法都失败"], method="error",
            )

        best_category = max(category_scores, key=category_scores.get)
        total_score = sum(category_scores.values())
        confidence = category_raw_confidences.get(best_category, 0.0)

        alternatives = [
            (cat, score / total_score)
            for cat, score in category_scores.items()
            if cat != best_category and total_score > 0
        ]
        alternatives.sort(key=lambda x: x[1], reverse=True)

        subcategory = None
        if subcategory_resolver and features:
            try:
                subcategory = subcategory_resolver(best_category, features)
            except Exception as e:
                self.logger.debug(f"子分类解析失败: {e}")

        final_method = "+".join(set(methods_used)) if methods_used else "unknown"

        if best_category != "未分类" and confidence < confidence_threshold:
            threshold_reasoning = list(all_reasoning)
            threshold_reasoning.append(
                f"最终置信度 {confidence:.2f} 低于阈值 {confidence_threshold:.2f}，标记为未分类"
            )
            threshold_alternatives = [(best_category, confidence)]
            threshold_alternatives.extend(a for a in alternatives if a[0] != best_category)
            return ClassificationResult(
                category="未分类", subcategory=None, confidence=confidence,
                reasoning=threshold_reasoning, alternatives=threshold_alternatives[:3],
                method=final_method, facets=merged_facets,
            )

        return ClassificationResult(
            category=best_category, subcategory=subcategory, confidence=confidence,
            reasoning=all_reasoning, alternatives=alternatives[:3],
            method=final_method, facets=merged_facets,
        )

    def update_weight(self, method: str, weight: float) -> None:
        self.method_weights[method] = weight

    def get_weights(self) -> Dict[str, float]:
        return dict(self.method_weights)
