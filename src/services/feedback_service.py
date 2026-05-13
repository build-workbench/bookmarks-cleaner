"""
Feedback Service - 反馈服务

处理反馈循环：导出复核队列、应用反馈、训练模型、审核数据。

深度: 高（简单接口，复杂的反馈处理逻辑）
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class FeedbackService:
    """
    反馈服务

    处理用户反馈的导入、应用和训练。

    示例:
        service = FeedbackService(config)
        service.export_review_queue(classified_bookmarks, "review.json")
        service.apply_feedback("feedback.json")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化反馈服务

        Args:
            config: 配置字典
        """
        self.config = config
        self.feedback_config = config.get("feedback_loop", {}) or {}
        self.active_learning_config = config.get("active_learning_settings", {}) or {}
        self.logger = logging.getLogger(__name__)

        # 延迟初始化引擎
        self._active_learning_engine = None
        self._incremental_trainer = None

    @property
    def active_learning_engine(self):
        """延迟加载主动学习引擎"""
        if self._active_learning_engine is None:
            try:
                from src.services.active_learning import ActiveLearningEngine

                merged_config = {**self.active_learning_config, **self.feedback_config}
                if merged_config.get("enabled", False):
                    self._active_learning_engine = ActiveLearningEngine(merged_config)
            except Exception as e:
                self.logger.warning(f"主动学习引擎初始化失败: {e}")
        return self._active_learning_engine

    @property
    def incremental_trainer(self):
        """延迟加载增量训练器"""
        if self._incremental_trainer is None:
            try:
                from src.services.incremental_trainer import IncrementalTrainer
                from src.services.feedback_model import FeedbackIncrementalModel

                if self.feedback_config.get("enabled", False):
                    self._incremental_trainer = IncrementalTrainer(self.feedback_config)
                    self._incremental_trainer.set_model(FeedbackIncrementalModel())
            except Exception as e:
                self.logger.warning(f"增量训练器初始化失败: {e}")
        return self._incremental_trainer

    def export_review_queue(
        self,
        classified_bookmarks: List[Dict],
        output_path: str,
        confidence_threshold: float = 0.7,
    ) -> Dict:
        """
        导出低置信度复核队列

        Args:
            classified_bookmarks: 已分类的书签列表
            output_path: 输出文件路径
            confidence_threshold: 置信度阈值

        Returns:
            导出统计
        """
        engine = self.active_learning_engine
        if engine is None:
            return {"items_exported": 0, "path": output_path}

        engine.clear_queue()
        export_items: List[Dict] = []

        for bookmark in classified_bookmarks:
            review_item = engine.process_classification(
                bookmark=bookmark,
                category=bookmark.get("category", "未分类"),
                confidence=float(bookmark.get("confidence", 0.0)),
                alternatives=bookmark.get("alternatives", []),
            )
            if review_item is None:
                continue

            export_items.append(
                {
                    "bookmark_id": review_item.bookmark_id,
                    "url": review_item.url,
                    "title": review_item.title,
                    "predicted_category": review_item.predicted_category,
                    "confidence": review_item.confidence,
                    "alternatives": list(review_item.alternatives),
                    "uncertainty_score": review_item.uncertainty_score,
                    "reasoning": bookmark.get("reasoning", []),
                    "method": bookmark.get("method", "unknown"),
                }
            )

        # 按不确定度排序
        export_items.sort(
            key=lambda item: (
                -float(item.get("uncertainty_score", 0.0)),
                float(item.get("confidence", 0.0)),
            )
        )

        payload = {
            "schema_version": "review-queue/v1",
            "items": export_items,
            "summary": {"items_exported": len(export_items)},
        }

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"items_exported": len(export_items), "path": output_path}

    def load_feedback_items(self, feedback_path: str) -> List[Dict]:
        """加载反馈文件"""
        with open(feedback_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        return []

    def apply_feedback(
        self,
        feedback_path: str,
        classifier: Any = None,
    ) -> Dict:
        """
        应用反馈

        Args:
            feedback_path: 反馈文件路径
            classifier: 可选的分类器（用于学习）

        Returns:
            应用统计
        """
        engine = self.active_learning_engine
        if engine is None:
            raise ValueError("feedback_loop 未启用，无法应用反馈")

        items = self.load_feedback_items(feedback_path)
        applied_count = 0

        for item in items:
            bookmark_id = item.get("bookmark_id")
            correct_category = item.get("correct_category")

            if not bookmark_id or not correct_category:
                continue

            engine.submit_feedback(
                bookmark_id=str(bookmark_id),
                correct_category=str(correct_category),
                original_prediction=str(item.get("predicted_category", "未分类")),
                original_confidence=item.get("confidence"),
            )

            # 如果提供了分类器，让它也学习
            if classifier and hasattr(classifier, "learn_from_feedback"):
                classifier.learn_from_feedback(
                    item.get("url", ""),
                    item.get("title", ""),
                    str(correct_category),
                    str(item.get("predicted_category", "未分类")),
                )

            applied_count += 1

        return {"applied_count": applied_count, "path": feedback_path}

    def train_from_feedback(self, feedback_path: str) -> Dict:
        """
        从反馈训练模型

        Args:
            feedback_path: 反馈文件路径

        Returns:
            训练统计
        """
        trainer = self.incremental_trainer
        if trainer is None:
            raise ValueError("feedback_loop 未启用，无法执行反馈训练")

        items = self.load_feedback_items(feedback_path)
        trained_samples = 0

        for item in items:
            correct_category = item.get("correct_category")
            if not correct_category:
                continue

            trainer.add_sample(
                features={
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "predicted_category": item.get("predicted_category", "未分类"),
                    "bookmark_id": item.get("bookmark_id", ""),
                },
                label=str(correct_category),
            )
            trained_samples += 1

        trainer.force_update()
        stats = trainer.get_stats()

        return {
            "trained_samples": trained_samples,
            "version_count": stats.get("version_count", 0),
            "current_version": stats.get("current_version"),
        }
