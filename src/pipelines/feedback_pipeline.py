"""
FeedbackPipeline - 反馈循环管理管道

统一管理反馈循环的所有操作，包括：
- 导出复核队列
- 应用反馈
- 训练反馈
- 审计反馈

特性：
- 完整的反馈生命周期管理
- 支持 cleanlab 辅助审计
- 详细的反馈统计
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple


class FeedbackPipeline:
    """反馈循环管理管道

    深度: 高（简单接口，复杂的反馈处理逻辑）
    接口: export_review_queue(...) / apply_feedback(...) / train_feedback(...) / audit_feedback(...)

    示例:
        pipeline = FeedbackPipeline(config, active_learning_engine, classifier)

        # 导出复核队列
        result = pipeline.export_review_queue(classified_bookmarks, "review_queue.json")

        # 应用反馈
        result = pipeline.apply_feedback("feedback.json")
    """

    def __init__(
        self,
        config: Dict,
        active_learning_engine: Optional[Any] = None,
        incremental_trainer: Optional[Any] = None,
        classifier: Optional[Any] = None,
    ):
        """初始化反馈管道

        Args:
            config: 配置字典
            active_learning_engine: 主动学习引擎
            incremental_trainer: 增量训练器
            classifier: AI 分类器
        """
        self.config = config
        self.active_learning_engine = active_learning_engine
        self.incremental_trainer = incremental_trainer
        self.classifier = classifier
        self.logger = logging.getLogger(__name__)

        # 统计信息
        self.stats = {
            "last_export_result": None,
            "last_apply_result": None,
            "last_train_result": None,
            "last_audit_result": None,
        }

    def export_review_queue(
        self, classified_bookmarks: List[Dict], output_path: Optional[str] = None
    ) -> Dict:
        """导出低置信度复核队列

        Args:
            classified_bookmarks: 已分类的书签列表
            output_path: 输出文件路径（默认使用配置中的路径）

        Returns:
            包含 items_exported 和 path 的字典
        """
        engine = self.active_learning_engine
        if engine is None:
            self.logger.warning("主动学习引擎未启用，无法导出复核队列")
            return {"items_exported": 0, "path": output_path}

        # 获取目标路径
        target_path = output_path or (self.config.get("feedback_loop", {}) or {}).get(
            "review_queue_path"
        )
        if not target_path:
            raise ValueError(
                "feedback_loop.review_queue_path 未配置，无法导出 review queue"
            )

        # 清空队列并处理分类结果
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
                    "score_breakdown": bookmark.get("score_breakdown", {}),
                }
            )

        # 排序
        export_items.sort(
            key=lambda item: (
                -float(item.get("uncertainty_score", 0.0)),
                float(item.get("confidence", 0.0)),
                str(item.get("url", "")),
                str(item.get("title", "")),
            )
        )

        # 写入文件
        payload = {
            "schema_version": "review-queue/v1",
            "items": export_items,
            "summary": {"items_exported": len(export_items)},
        }

        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        result = {"items_exported": len(export_items), "path": target_path}
        self.stats["last_export_result"] = result
        return result

    def apply_feedback(self, feedback_path: str) -> Dict:
        """导入离线反馈文件并应用到现有反馈管道

        Args:
            feedback_path: 反馈文件路径

        Returns:
            包含 applied_count 和 path 的字典
        """
        engine = self.active_learning_engine
        if engine is None:
            raise ValueError("feedback_loop 未启用，无法应用反馈文件")

        items = self._load_feedback_items(feedback_path)

        applied_items: List[Dict] = []
        for item in items:
            bookmark_id = item.get("bookmark_id")
            url = item.get("url", "")
            title = item.get("title", "")
            predicted_category = item.get("predicted_category", "未分类")
            correct_category = item.get("correct_category")
            original_confidence = item.get(
                "original_confidence", item.get("confidence")
            )

            if not bookmark_id or not correct_category:
                raise ValueError("反馈项缺少 bookmark_id 或 correct_category")

            # 提交反馈到主动学习引擎
            engine.submit_feedback(
                bookmark_id=str(bookmark_id),
                correct_category=str(correct_category),
                original_prediction=str(predicted_category),
                original_confidence=(
                    float(original_confidence)
                    if original_confidence is not None
                    else None
                ),
            )

            # 让分类器学习
            if url and title and self.classifier:
                self.classifier.learn_from_feedback(
                    url,
                    title,
                    str(correct_category),
                    str(predicted_category),
                )

            applied_items.append(
                {
                    "bookmark_id": str(bookmark_id),
                    "url": url,
                    "title": title,
                    "predicted_category": str(predicted_category),
                    "correct_category": str(correct_category),
                    "original_confidence": original_confidence,
                }
            )

        # 排序
        applied_items.sort(key=lambda item: item["bookmark_id"])

        # 保存已应用的反馈
        applied_feedback_path = (self.config.get("feedback_loop", {}) or {}).get(
            "applied_feedback_path"
        )
        if applied_feedback_path:
            self._save_applied_feedback(applied_feedback_path, applied_items)

        result = {"applied_count": len(applied_items), "path": feedback_path}
        self.stats["last_apply_result"] = result
        return result

    def train_feedback(self, feedback_path: str) -> Dict:
        """将已批准反馈样本接入增量训练器并生成版本

        Args:
            feedback_path: 反馈文件路径

        Returns:
            包含训练统计的字典
        """
        trainer = self.incremental_trainer
        if trainer is None:
            raise ValueError("feedback_loop 未启用，无法执行反馈训练")

        items = self._load_feedback_items(feedback_path)
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
        trainer_stats = trainer.get_stats()

        result = {
            "trained_samples": trained_samples,
            "version_count": trainer_stats.get("version_count", 0),
            "current_version": trainer_stats.get("current_version"),
        }
        self.stats["last_train_result"] = result
        return result

    def audit_feedback(
        self, feedback_path: str, output_path: Optional[str] = None
    ) -> Dict:
        """审核反馈数据质量，在可用时启用 cleanlab 辅助

        Args:
            feedback_path: 反馈文件路径
            output_path: 输出文件路径

        Returns:
            包含审计统计的字典
        """
        items = self._load_feedback_items(feedback_path)

        # 获取目标路径
        target_path = output_path or (
            ((self.config.get("feedback_loop", {}) or {}).get("audit", {}) or {}).get(
                "output_path"
            )
        )
        if not target_path:
            raise ValueError(
                "feedback_loop.audit.output_path 未配置，无法导出 audit 结果"
            )

        # 计算统计
        disagreement_count = sum(
            1
            for item in items
            if item.get("correct_category")
            and item.get("predicted_category")
            and str(item.get("correct_category")) != str(item.get("predicted_category"))
        )

        # 检测重复 ID
        duplicate_ids: Dict[str, int] = {}
        for item in items:
            bookmark_id = str(item.get("bookmark_id", ""))
            duplicate_ids[bookmark_id] = duplicate_ids.get(bookmark_id, 0) + 1

        summary = {
            "total_items": len(items),
            "disagreement_count": disagreement_count,
            "duplicate_bookmark_ids": sorted(
                [
                    bookmark_id
                    for bookmark_id, count in duplicate_ids.items()
                    if count > 1
                ]
            ),
        }

        # 尝试使用 cleanlab
        audit_backend = "builtin"
        likely_issues: List[Dict] = []
        cleanlab_find_label_issues = self._get_cleanlab_find_label_issues()
        if cleanlab_find_label_issues is not None:
            try:
                likely_issues = self._run_cleanlab_audit(
                    items, cleanlab_find_label_issues
                )
                audit_backend = "cleanlab"
            except Exception as exc:
                self.logger.warning(
                    f"cleanlab audit failed, falling back to builtin audit: {exc}"
                )

        # 写入文件
        payload = {
            "schema_version": "feedback-audit/v1",
            "audit_backend": audit_backend,
            "summary": summary,
            "likely_issues": likely_issues,
        }

        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        result = {"audit_backend": audit_backend, "path": target_path}
        self.stats["last_audit_result"] = result
        return result

    def _load_feedback_items(self, feedback_path: str) -> List[Dict]:
        """加载反馈文件"""
        with open(feedback_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError("反馈文件格式无效：items 必须是列表")
        if not all(isinstance(item, dict) for item in items):
            raise ValueError("反馈项格式无效：每个 item 都必须是对象")
        return items

    def _save_applied_feedback(
        self, applied_feedback_path: str, new_items: List[Dict]
    ) -> None:
        """保存已应用的反馈"""
        existing_items: List[Dict] = []
        if os.path.exists(applied_feedback_path):
            try:
                with open(applied_feedback_path, "r", encoding="utf-8") as f:
                    existing_payload = json.load(f)
                existing_items = (
                    existing_payload.get("items", [])
                    if isinstance(existing_payload, dict)
                    else []
                )
            except Exception:
                pass

        # 合并并去重
        merged = {
            str(item["bookmark_id"]): item
            for item in existing_items + new_items
            if isinstance(item, dict) and item.get("bookmark_id")
        }
        merged_items = [merged[key] for key in sorted(merged)]

        # 写入文件
        os.makedirs(os.path.dirname(applied_feedback_path) or ".", exist_ok=True)
        with open(applied_feedback_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": "applied-feedback/v1",
                    "items": merged_items,
                    "summary": {"applied_count": len(merged_items)},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    def _get_cleanlab_find_label_issues(self) -> Optional[Any]:
        """获取 cleanlab 的 find_label_issues 函数"""
        try:
            from cleanlab.filter import find_label_issues

            return find_label_issues
        except ImportError:
            return None

    def _run_cleanlab_audit(
        self, items: List[Dict], find_label_issues: Any
    ) -> List[Dict]:
        """运行 cleanlab 审计"""
        # 准备数据
        import numpy as np

        labels = []
        pred_probs = []

        for item in items:
            category = item.get("correct_category") or item.get("predicted_category")
            confidence = float(item.get("confidence", 0.5))

            if category:
                labels.append(category)
                # 简化的概率矩阵（实际应用中需要更复杂的实现）
                pred_probs.append([1.0 - confidence, confidence])

        if not labels:
            return []

        labels_array = np.array(labels)
        pred_probs_array = np.array(pred_probs)

        # 运行 cleanlab
        issue_indices = find_label_issues(
            labels=labels_array,
            pred_probs=pred_probs_array,
            return_indices_ranked_by="self_confidence",
        )

        # 构建结果
        issues = []
        for idx in issue_indices:
            if idx < len(items):
                item = items[idx]
                issues.append(
                    {
                        "bookmark_id": item.get("bookmark_id"),
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "predicted_category": item.get("predicted_category"),
                        "correct_category": item.get("correct_category"),
                        "confidence": item.get("confidence"),
                    }
                )

        return issues

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
