"""
Bookmark Processor - 书签处理器

负责批量处理书签文件，协调各个组件完成整个分类流程
"""

import json
import logging
import os
import re
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from src.utils.emoji_cleaner import clean_title as clean_emoji_title

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
from src.classifiers.ai import AIBookmarkClassifier
from src.utils.category import (
    normalize_category_config,
    normalize_category_string,
    strip_category_prefix,
)
from src.utils.resource_loader import load_json_config, resolve_config_path
from src.utils.standardizer import TaxonomyStandardizer

try:
    from src.llm.organizer import LLMBookmarkOrganizer
except ImportError:
    LLMBookmarkOrganizer = None

from src.data.deduplicator import BookmarkDeduplicator

# 导入核心组件
from src.data.exporter import DataExporter
from src.health.bookmark_checker import HealthChecker

try:
    from src.services.active_learning import ActiveLearningEngine
except ImportError:
    ActiveLearningEngine = None

try:
    from src.services.incremental_trainer import IncrementalTrainer
except ImportError:
    IncrementalTrainer = None


class FeedbackIncrementalModel:
    """轻量级反馈增量模型，用于离线 feedback 训练与版本化。"""

    def __init__(self):
        self.classes_: List[str] = []
        self._label_by_signature: Dict[str, str] = {}
        self._label_counts: Dict[str, int] = {}

    def partial_fit(self, X, y, classes=None):
        if classes:
            merged = set(self.classes_) | set(classes)
            self.classes_ = sorted(str(label) for label in merged)

        for features, label in zip(X, y):
            label = str(label)
            signature = self._signature(features)
            self._label_by_signature[signature] = label
            self._label_counts[label] = self._label_counts.get(label, 0) + 1

    def predict(self, X):
        default_label = max(
            self._label_counts,
            key=self._label_counts.get,
            default="未分类",
        )
        return [
            self._label_by_signature.get(self._signature(features), default_label)
            for features in X
        ]

    def _signature(self, features: Dict) -> str:
        url = str(features.get("url", ""))
        title = str(features.get("title", "")).strip().lower()
        domain = urlparse(url).netloc.lower().replace("www.", "")
        return f"{domain}::{title}"


class BookmarkProcessor:
    """书签处理器主类"""

    def __init__(
        self,
        config_path: str | None = None,
        max_workers: int = 4,
        use_ml: bool = True,
        confidence_threshold: Optional[float] = None,
    ):
        resolved_path, self._explicit_config = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        # 优化线程池大小：限制最大线程数避免过度竞争
        self.max_workers = min(max_workers, 32)  # 限制最大32线程
        self.use_ml = use_ml

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

        # 初始化组件
        loaded_config, _, explicit = load_json_config(self.config_path)
        self.config = self._normalize_category_config(loaded_config)
        self._config_load_ok = True
        self._explicit_config = explicit

        if not isinstance(
            self.config.get("category_rules"), dict
        ) or not self.config.get("category_rules"):
            source = "显式配置" if explicit else "默认配置"
            raise ValueError(f"{source}缺少有效的 category_rules: {self.config_path}")

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

        # 标准化层（受控词表）
        self.standardizer = TaxonomyStandardizer(self.config)

        # 延迟初始化组件以避免启动开销
        self._classifier = None
        self._deduplicator = None
        self._health_checker = None
        self._exporter = None
        self._llm_organizer = None
        self._active_learning_engine = None
        self._incremental_trainer = None
        self.llm_organizer_meta: Optional[Dict] = None

        # 缓存和性能优化 (OrderedDict with LRU eviction)
        self._max_cache_size = 10000
        self._classification_cache: OrderedDict = OrderedDict()
        self._url_validation_cache: OrderedDict = OrderedDict()
        self._stats_lock = threading.Lock()

        # 处理统计
        self.stats = {
            "total_bookmarks": 0,
            "processed_bookmarks": 0,
            "duplicates_removed": 0,
            "errors": 0,
            "processing_time": 0.0,
            "categories_found": {},
            "files_processed": 0,
            "llm_organizer_used": False,
        }

    @staticmethod
    def _strip_category_prefix(text: str) -> str:
        return strip_category_prefix(text)

    def _normalize_category_config(self, config: Dict) -> Dict:
        return normalize_category_config(config)

    def _normalize_category_string(self, category: str) -> str:
        return normalize_category_string(category)

    @property
    def classifier(self):
        """Lazy loading classifier"""
        if self._classifier is None:
            self._classifier = AIBookmarkClassifier(
                self.config_path, enable_ml=self.use_ml, config=self.config
            )

            if self.confidence_threshold is not None:
                ai_settings = self._classifier.config.get("ai_settings")
                if not isinstance(ai_settings, dict):
                    ai_settings = {}
                    self._classifier.config["ai_settings"] = ai_settings
                ai_settings["confidence_threshold"] = self.confidence_threshold
        return self._classifier

    @property
    def deduplicator(self):
        """Lazy loading deduplicator"""
        if self._deduplicator is None:
            self._deduplicator = BookmarkDeduplicator()
        return self._deduplicator

    @property
    def health_checker(self):
        """Lazy loading health checker"""
        if self._health_checker is None:
            self._health_checker = HealthChecker()
        return self._health_checker

    @property
    def exporter(self):
        """Lazy loading exporter"""
        if self._exporter is None:
            self._exporter = DataExporter(config=self.config)
        return self._exporter

    @property
    def llm_organizer(self) -> Optional[LLMBookmarkOrganizer]:
        """Lazy loading LLM organizer"""
        if self._llm_organizer is None and LLMBookmarkOrganizer is not None:
            try:
                self._llm_organizer = LLMBookmarkOrganizer(
                    config_path=self.config_path, config=self.config
                )
            except Exception as exc:
                self.logger.warning(f"LLM organizer init failed: {exc}")
                self._llm_organizer = None
        return self._llm_organizer

    @property
    def active_learning_engine(self):
        """Lazy loading offline review/feedback engine."""
        if self._active_learning_engine is None and ActiveLearningEngine is not None:
            feedback_config = dict(
                self.config.get("active_learning_settings", {}) or {}
            )
            feedback_config.update(self.config.get("feedback_loop", {}) or {})
            if "confidence_threshold" not in feedback_config:
                feedback_config["confidence_threshold"] = self.config.get(
                    "ai_settings", {}
                ).get("confidence_threshold", 0.7)
            if feedback_config.get("enabled", False):
                self._active_learning_engine = ActiveLearningEngine(feedback_config)
        return self._active_learning_engine

    @property
    def incremental_trainer(self):
        """Lazy loading incremental trainer for approved feedback."""
        if self._incremental_trainer is None and IncrementalTrainer is not None:
            feedback_config = dict(self.config.get("feedback_loop", {}) or {})
            if feedback_config.get("enabled", False):
                self._incremental_trainer = IncrementalTrainer(feedback_config)
                self._incremental_trainer.set_model(FeedbackIncrementalModel())
        return self._incremental_trainer

    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
        review_queue_path: Optional[str] = None,
    ) -> Dict:
        """处理多个书签文件"""
        if BeautifulSoup is None:
            raise ImportError(
                "缺少依赖 beautifulsoup4（bs4），请先安装：pip install beautifulsoup4"
            )

        start_time = time.time()

        self.logger.info(f"开始处理 {len(input_files)} 个文件")

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 并行加载所有书签以加速IO操作
        all_bookmarks = []
        with ThreadPoolExecutor(max_workers=min(len(input_files), 8)) as file_executor:
            file_futures = {
                file_executor.submit(
                    self._load_bookmarks_from_file, file_path
                ): file_path
                for file_path in input_files
            }

            for future in as_completed(file_futures):
                file_path = file_futures[future]
                try:
                    bookmarks = future.result()
                    all_bookmarks.extend(bookmarks)
                    self.stats["files_processed"] += 1
                except Exception as e:
                    self.logger.error(f"加载文件失败 {file_path}: {e}")
                    self.stats["errors"] += 1

        # 应用 limit 截断（调试用）
        if limit and limit > 0 and len(all_bookmarks) > limit:
            self.logger.info(
                f"应用 --limit={limit}，截断 {len(all_bookmarks)} -> {limit} 个书签"
            )
            all_bookmarks = all_bookmarks[:limit]

        self.stats["total_bookmarks"] = len(all_bookmarks)

        if not all_bookmarks:
            self.logger.warning("没有找到有效的书签")
            return self.stats

        # 优化去重处理：先进行快速URL去重
        self.logger.info("开始快速去重处理...")
        # 快速URL去重
        seen_urls = set()
        fast_unique = []
        for bookmark in all_bookmarks:
            url = bookmark.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                fast_unique.append(bookmark)

        fast_duplicates_removed = len(all_bookmarks) - len(fast_unique)
        self.logger.info(f"快速去重移除了 {fast_duplicates_removed} 个重复书签")

        # 对剩余书签执行高级去重（始终执行，提升跨浏览器合并的去重质量）
        unique_bookmarks, duplicates = self.deduplicator.remove_duplicates(fast_unique)
        self.stats["duplicates_removed"] = fast_duplicates_removed + len(duplicates)

        # 并行分类处理
        self.logger.info(f"开始分类 {len(unique_bookmarks)} 个书签...")
        classified_bookmarks = self._classify_bookmarks_parallel(unique_bookmarks)

        # 组织分类结果
        organized_bookmarks = self._organize_bookmarks(classified_bookmarks)

        if review_queue_path:
            self.export_review_queue(classified_bookmarks, review_queue_path)

        # 可选：调用 LLM 进行更高层次的整理
        self.llm_organizer_meta = None
        self.stats["llm_organizer_used"] = False
        self.stats.pop("llm_organizer_meta", None)

        if self.llm_organizer and self.llm_organizer.enabled():
            try:
                llm_result = self.llm_organizer.organize(
                    bookmarks=classified_bookmarks, baseline=organized_bookmarks
                )
            except Exception as exc:
                self.logger.warning(f"LLM organizer execution failed: {exc}")
                llm_result = None

            if llm_result and llm_result.get("organized"):
                organized_bookmarks = llm_result["organized"]
                self.llm_organizer_meta = llm_result.get("meta")
                self.stats["llm_organizer_used"] = True
                if self.llm_organizer_meta:
                    self.stats["llm_organizer_meta"] = self.llm_organizer_meta

        organized_bookmarks = self._sort_organized_structure(organized_bookmarks)

        # 更新统计
        self.stats["processing_time"] = time.time() - start_time
        self.stats["processed_bookmarks"] = len(classified_bookmarks)

        # 导出结果
        self._export_results(organized_bookmarks, output_dir)

        # 训练模型（如果启用）
        if train_models and self.use_ml:
            self._train_models(classified_bookmarks)

        self.logger.info(f"处理完成: {self.stats['processed_bookmarks']} 个书签已分类")

        return self.stats

    def export_review_queue(
        self, classified_bookmarks: List[Dict], output_path: Optional[str] = None
    ) -> Dict:
        """导出低置信度复核队列。"""
        engine = self.active_learning_engine
        if engine is None:
            return {"items_exported": 0, "path": output_path}

        target_path = output_path or (self.config.get("feedback_loop", {}) or {}).get(
            "review_queue_path"
        )
        if not target_path:
            raise ValueError(
                "feedback_loop.review_queue_path 未配置，无法导出 review queue"
            )

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

        export_items.sort(
            key=lambda item: (
                -float(item.get("uncertainty_score", 0.0)),
                float(item.get("confidence", 0.0)),
                str(item.get("url", "")),
                str(item.get("title", "")),
            )
        )

        payload = {
            "schema_version": "review-queue/v1",
            "items": export_items,
            "summary": {"items_exported": len(export_items)},
        }

        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"items_exported": len(export_items), "path": target_path}

    def apply_feedback_file(self, feedback_path: str) -> Dict:
        """导入离线反馈文件并应用到现有反馈管道。"""
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

            if url and title:
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

        applied_items.sort(key=lambda item: item["bookmark_id"])
        applied_feedback_path = (self.config.get("feedback_loop", {}) or {}).get(
            "applied_feedback_path"
        )
        if applied_feedback_path:
            existing_items: List[Dict] = []
            if os.path.exists(applied_feedback_path):
                with open(applied_feedback_path, "r", encoding="utf-8") as f:
                    existing_payload = json.load(f)
                existing_items = (
                    existing_payload.get("items", [])
                    if isinstance(existing_payload, dict)
                    else []
                )

            merged = {
                str(item["bookmark_id"]): item
                for item in existing_items + applied_items
                if isinstance(item, dict) and item.get("bookmark_id")
            }
            merged_items = [merged[key] for key in sorted(merged)]

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

        return {"applied_count": len(applied_items), "path": feedback_path}

    def train_feedback_file(self, feedback_path: str) -> Dict:
        """将已批准反馈样本接入增量训练器并生成版本。"""
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
        stats = trainer.get_stats()
        return {
            "trained_samples": trained_samples,
            "version_count": stats.get("version_count", 0),
            "current_version": stats.get("current_version"),
        }

    def audit_feedback_file(
        self, feedback_path: str, output_path: Optional[str] = None
    ) -> Dict:
        """审核反馈数据质量，在可用时启用 cleanlab 辅助。"""
        items = self._load_feedback_items(feedback_path)
        target_path = output_path or (
            ((self.config.get("feedback_loop", {}) or {}).get("audit", {}) or {}).get(
                "output_path"
            )
        )
        if not target_path:
            raise ValueError(
                "feedback_loop.audit.output_path 未配置，无法导出 audit 结果"
            )

        disagreement_count = sum(
            1
            for item in items
            if item.get("correct_category")
            and item.get("predicted_category")
            and str(item.get("correct_category")) != str(item.get("predicted_category"))
        )
        duplicate_ids = {}
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

        payload = {
            "schema_version": "feedback-audit/v1",
            "audit_backend": audit_backend,
            "summary": summary,
            "likely_issues": likely_issues,
        }

        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"audit_backend": audit_backend, "path": target_path}

    def _load_feedback_items(self, feedback_path: str) -> List[Dict]:
        with open(feedback_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        items = payload.get("items", payload) if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            raise ValueError("反馈文件格式无效：items 必须是列表")
        if not all(isinstance(item, dict) for item in items):
            raise ValueError("反馈项格式无效：每个 item 都必须是对象")
        return items

    def _get_cleanlab_find_label_issues(self):
        try:
            from cleanlab.filter import find_label_issues
        except ImportError:
            return None
        return find_label_issues

    def _run_cleanlab_audit(self, items: List[Dict], find_label_issues) -> List[Dict]:
        import numpy as np

        categories = sorted(
            {
                str(category)
                for item in items
                for category in [
                    item.get("correct_category"),
                    item.get("predicted_category"),
                    *[alt[0] for alt in item.get("alternatives", []) if alt],
                ]
                if category
            }
        )
        if len(categories) < 2:
            return []

        category_to_idx = {category: idx for idx, category in enumerate(categories)}
        labels = []
        pred_probs = []
        indexed_items = []

        for item in items:
            correct_category = item.get("correct_category")
            predicted_category = item.get("predicted_category")
            if not correct_category or not predicted_category:
                continue

            scores = {
                str(predicted_category): float(item.get("confidence", 1.0) or 0.0)
            }
            for alt_category, alt_score in item.get("alternatives", []):
                scores[str(alt_category)] = float(alt_score)

            total = sum(max(score, 0.0) for score in scores.values())
            if total <= 0:
                continue

            probs = np.zeros(len(categories), dtype=float)
            for category, score in scores.items():
                probs[category_to_idx[category]] = max(score, 0.0) / total

            labels.append(category_to_idx[str(correct_category)])
            pred_probs.append(probs)
            indexed_items.append(item)

        if len(pred_probs) < 2:
            return []

        issue_indices = find_label_issues(
            labels=np.array(labels),
            pred_probs=np.array(pred_probs),
            return_indices_ranked_by="self_confidence",
        )

        return [
            {
                "bookmark_id": indexed_items[int(idx)].get("bookmark_id"),
                "url": indexed_items[int(idx)].get("url", ""),
                "predicted_category": indexed_items[int(idx)].get("predicted_category"),
                "correct_category": indexed_items[int(idx)].get("correct_category"),
            }
            for idx in issue_indices
        ]

    def _load_bookmarks_from_file(self, file_path: str) -> List[Dict]:
        """优化的从HTML文件加载书签"""
        bookmarks = []

        try:
            if BeautifulSoup is None:
                raise ImportError(
                    "缺少依赖 beautifulsoup4（bs4），请先安装：pip install beautifulsoup4"
                )

            # 使用更快的解析器
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 使用lxml解析器如果可用，否则使用html.parser
            try:
                soup = BeautifulSoup(content, "lxml")
            except (ImportError, Exception):
                soup = BeautifulSoup(content, "html.parser")

            links = soup.find_all("a", href=True)  # 只查找有href的链接

            for link in links:
                url = link.get("href", "").strip()
                title_raw = (link.string or link.get_text() or "").strip()
                # 统一使用预处理模块清理标题前缀emoji，防止多次导出叠加
                title = clean_emoji_title(title_raw)

                if url and title and self._is_valid_url(url):
                    bookmarks.append(
                        {
                            "url": url,
                            "title": title,
                            "source_file": file_path,
                            "add_date": link.get("add_date", ""),
                            "last_modified": link.get("last_modified", ""),
                        }
                    )

            self.logger.info(f"从 {file_path} 加载了 {len(bookmarks)} 个书签")

        except Exception as e:
            self.logger.error(f"加载文件失败 {file_path}: {e}")
            self.stats["errors"] += 1

        return bookmarks

    _INVALID_URL_PREFIXES = (
        "javascript:",
        "data:",
        "chrome:",
        "about:",
        "file:",
        "mailto:",
    )

    def _is_valid_url(self, url: str) -> bool:
        """验证URL有效性"""
        if not url:
            return False
        url_lower = url.lower()
        if url_lower.startswith(self._INVALID_URL_PREFIXES):
            return False
        return url.startswith(("http://", "https://"))

    def _classify_bookmarks_parallel(self, bookmarks: List[Dict]) -> List[Dict]:
        """优化的并行分类书签"""
        classified_bookmarks = []
        batch_size = 100  # 批处理大小

        # 复用同一个线程池，避免每批重复创建/销毁的开销
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(0, len(bookmarks), batch_size):
                batch = bookmarks[i : i + batch_size]

                # 提交分类任务
                future_to_bookmark = {
                    executor.submit(
                        self._classify_single_bookmark_cached, bookmark
                    ): bookmark
                    for bookmark in batch
                }

                # 收集结果
                batch_results = []
                for future in as_completed(future_to_bookmark):
                    bookmark = future_to_bookmark[future]

                    try:
                        result = future.result(timeout=30)
                        if result:
                            batch_results.append(result)

                    except Exception as e:
                        self.logger.error(
                            f"分类失败 {bookmark.get('url', 'unknown')}: {e}"
                        )
                        with self._stats_lock:
                            self.stats["errors"] += 1

                classified_bookmarks.extend(batch_results)

                # 显示进度
                completed = i + len(batch)
                progress = min(completed / len(bookmarks) * 100, 100)
                self.logger.info(
                    f"分类进度: {progress:.1f}% ({completed}/{len(bookmarks)})"
                )

        return classified_bookmarks

    def _classify_single_bookmark_cached(self, bookmark: Dict) -> Optional[Dict]:
        """带缓存的单个书签分类"""
        try:
            url = bookmark["url"]
            title = bookmark["title"]

            # 创建缓存键
            cache_key = f"{url}|{title}"

            # 检查缓存 (with LRU update)
            if cache_key in self._classification_cache:
                self._classification_cache.move_to_end(cache_key)
                cached_result = self._classification_cache[cache_key]
                return {**bookmark, **cached_result}

            # 使用AI分类器
            result = self.classifier.classify(url, title)

            # 处理分类结果（可能是对象或字典）
            if hasattr(result, "category"):
                # ClassificationResult对象
                cached_data = {
                    "category": self._normalize_category_string(result.category),
                    "subcategory": (
                        result.subcategory if hasattr(result, "subcategory") else None
                    ),
                    "confidence": result.confidence,
                    "alternatives": (
                        result.alternatives if hasattr(result, "alternatives") else []
                    ),
                    "reasoning": (
                        result.reasoning if hasattr(result, "reasoning") else []
                    ),
                    "method": result.method if hasattr(result, "method") else "unknown",
                    "processing_time": (
                        result.processing_time
                        if hasattr(result, "processing_time")
                        else 0.0
                    ),
                    "facets": result.facets if hasattr(result, "facets") else {},
                    "score_breakdown": (
                        result.score_breakdown
                        if hasattr(result, "score_breakdown")
                        else {}
                    ),
                }
            else:
                # 字典结果
                cached_data = {
                    "category": self._normalize_category_string(
                        result.get("category", "未分类")
                    ),
                    "subcategory": result.get("subcategory"),
                    "confidence": result.get("confidence", 0.0),
                    "alternatives": result.get("alternatives", []),
                    "reasoning": result.get("reasoning", []),
                    "method": result.get("method", "unknown"),
                    "processing_time": result.get("processing_time", 0.0),
                    "facets": result.get("facets", {}),
                    "score_breakdown": result.get("score_breakdown", {}),
                }

            # LRU cache eviction
            if len(self._classification_cache) >= self._max_cache_size:
                self._classification_cache.popitem(last=False)
            self._classification_cache[cache_key] = cached_data

            # 构建结果
            classified_bookmark = {**bookmark, **cached_data}

            # 更新分类统计（线程安全）
            category = cached_data["category"]
            with self._stats_lock:
                self.stats["categories_found"][category] = (
                    self.stats["categories_found"].get(category, 0) + 1
                )

            return classified_bookmark

        except Exception as e:
            self.logger.error(f"单个书签分类失败: {e}")
            return None

    def _organize_bookmarks(self, classified_bookmarks: List[Dict]) -> Dict:
        """按 subject -> resource_type 两级组织（受控词表标准化）。"""
        organized: Dict[str, Dict] = {}

        for bookmark in classified_bookmarks:
            category = (bookmark.get("category") or "").strip()
            subcategory = (bookmark.get("subcategory") or "").strip() or None

            # 从分类派生 subject / resource_type
            derived_subject, derived_rt = self.standardizer.derive_from_category(
                category, content_type=None
            )

            # 标准化 subject 与 resource_type
            subject = (
                derived_subject
                or self.standardizer.normalize_subject(category)
                or "其他"
            )
            # 优先使用规则引擎提供的 resource_type 分面提示
            facets = bookmark.get("facets") or {}
            facet_rt_hint = (
                facets.get("resource_type_hint") if isinstance(facets, dict) else None
            )
            facet_rt_std = (
                self.standardizer.normalize_resource_type(facet_rt_hint)
                if facet_rt_hint
                else None
            )
            resource_type = (
                facet_rt_std
                or self.standardizer.normalize_resource_type(subcategory)
                or derived_rt
            )

            # 初始化 subject 节点
            if subject not in organized:
                organized[subject] = {"_items": [], "_subcategories": {}}

            # 放入 resource_type 子类或直接归于 subject
            if resource_type:
                if resource_type not in organized[subject]["_subcategories"]:
                    organized[subject]["_subcategories"][resource_type] = {"_items": []}
                organized[subject]["_subcategories"][resource_type]["_items"].append(
                    bookmark
                )
            else:
                organized[subject]["_items"].append(bookmark)

        return self._sort_organized_structure(organized)

    def _sort_organized_structure(self, organized: Optional[Dict]) -> Dict:
        """统一的排序逻辑，保证导出结果有序。"""
        if not organized:
            return {}

        def _count_subject(subject_data: Dict) -> int:
            total = 0
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                total += len(items)
            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        total += len(sub_items)
            return total

        category_order = self.config.get("category_order")
        preferred_subject_order: List[str] = []
        if isinstance(category_order, list):
            for raw in category_order:
                if not raw:
                    continue
                subj = self.standardizer.normalize_subject(str(raw))
                if subj and subj not in preferred_subject_order:
                    preferred_subject_order.append(subj)

        preferred_subject_order = [s for s in preferred_subject_order if s in organized]

        ordered_subjects: List[str] = []
        ordered_subjects.extend(preferred_subject_order)

        remaining = [s for s in organized.keys() if s not in ordered_subjects]
        remaining.sort(key=lambda s: (-_count_subject(organized.get(s) or {}), str(s)))
        ordered_subjects.extend(remaining)

        sorted_organized: Dict[str, Dict] = {}
        for subject in ordered_subjects:
            subject_data = organized.get(subject) or {}

            items = subject_data.get("_items", [])
            if isinstance(items, list):
                items.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
                subject_data["_items"] = items

            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        sub_items.sort(
                            key=lambda x: x.get("confidence", 0.0), reverse=True
                        )
                        sub_data["_items"] = sub_items

                ordered_subcats = sorted(
                    subcategories.items(),
                    key=lambda kv: (
                        -len((kv[1] or {}).get("_items", []) or []),
                        str(kv[0]),
                    ),
                )
                subject_data["_subcategories"] = {k: v for k, v in ordered_subcats}

            sorted_organized[subject] = subject_data

        return sorted_organized

    def _export_results(self, organized_bookmarks: Dict, output_dir: str):
        """优化的导出处理结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 在导出前获取最终的统计数据
        final_stats = self.get_statistics()

        # 并行导出多种格式以节省时间
        export_tasks = [
            ("html", f"bookmarks_{timestamp}.html"),
            ("json", f"bookmarks_{timestamp}.json"),
            ("markdown", f"report_{timestamp}.md"),
        ]

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            for format_type, filename in export_tasks:
                output_file = os.path.join(output_dir, filename)

                if format_type == "html":
                    future = executor.submit(
                        self.exporter.export_html,
                        organized_bookmarks,
                        output_file,
                        final_stats,
                    )
                elif format_type == "json":
                    future = executor.submit(
                        self.exporter.export_json,
                        organized_bookmarks,
                        output_file,
                        final_stats,
                    )
                elif format_type == "markdown":
                    future = executor.submit(
                        self.exporter.export_markdown,
                        organized_bookmarks,
                        output_file,
                        final_stats,
                    )

                futures.append(future)

            # 等待所有导出完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"导出失败: {e}")

        self.logger.info(f"结果已导出到: {output_dir}")

    def _train_models(self, classified_bookmarks: List[Dict]):
        """训练机器学习模型"""
        if not self.classifier.ml_classifier:
            self.logger.warning("机器学习组件未启用，跳过训练")
            return

        self.logger.info("开始训练机器学习模型...")

        # 准备训练数据
        samples_added = 0
        for bookmark in classified_bookmarks:
            if bookmark.get("confidence", 0.0) > 0.8:  # 只使用高置信度的数据训练
                features = self.classifier.extract_features(
                    bookmark["url"], bookmark["title"]
                )
                self.classifier.ml_classifier.add_training_sample(
                    features, bookmark["category"]
                )
                samples_added += 1

        if samples_added > 50:  # 需要足够的训练数据
            self.logger.info(f"使用 {samples_added} 个样本进行训练...")
            if self.classifier.ml_classifier.train_model():
                self.logger.info(f"模型训练完成。")
            else:
                self.logger.error("模型训练失败。")
        else:
            self.logger.warning(f"训练数据不足 ({samples_added} 个样本)，跳过训练")

    def health_check(self, bookmarks: List[Dict]) -> Dict:
        """对书签进行健康检查"""
        self.logger.info(f"开始健康检查 {len(bookmarks)} 个书签...")

        results = self.health_checker.check_bookmarks(bookmarks)
        summary = self.health_checker.get_summary(results)

        self.logger.info(
            f"健康检查完成: {summary['accessible_count']}/{summary['total_count']} 个链接可访问"
        )

        return summary

    def get_statistics(self) -> Dict:
        """获取处理统计信息"""
        # 确保分类器已经被初始化
        if self._classifier:
            classifier_stats = self.classifier.get_statistics()
        else:
            classifier_stats = {}

        # 计算处理速度和成功率
        processing_time = self.stats.get("processing_time", 0.0)
        processed_bookmarks = self.stats.get("processed_bookmarks", 0)
        total_bookmarks = self.stats.get("total_bookmarks", 1)

        llm_stats = None
        if self.llm_organizer:
            llm_stats = self.llm_organizer.get_stats()

        return {
            **self.stats,
            "classifier_stats": classifier_stats,
            "processing_speed_bps": processed_bookmarks
            / max(processing_time, 0.001),  # bookmarks per second
            "success_rate_percent": (processed_bookmarks / max(total_bookmarks, 1))
            * 100,
            "llm_organizer_stats": llm_stats,
        }
