"""书签处理器 - 核心处理流程编排"""

from __future__ import annotations

import logging
import os
import time
from typing import Dict, List, Optional

from cleanbook.classifier import BookmarkClassifier
from cleanbook.config import load_json_config, resolve_config_path
from cleanbook.deduplicator import BookmarkDeduplicator
from cleanbook.exporter import DataExporter
from cleanbook.loader import BookmarkLoader
from cleanbook.organizer import OrganizationPipeline
from cleanbook.taxonomy import TaxonomyService
from cleanbook.text_utils import normalize_category_config, normalize_category_string

logger = logging.getLogger(__name__)


class BookmarkProcessor:
    """书签处理器 - 门面入口

    编排 load -> dedup -> classify -> organize -> export 流程。
    """

    MAX_WORKERS_LIMIT = 32

    def __init__(
        self,
        config_path: Optional[str] = None,
        max_workers: int = 4,
        use_ml: bool = True,
        confidence_threshold: Optional[float] = None,
    ):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.max_workers = min(max_workers, self.MAX_WORKERS_LIMIT)
        self.use_ml = use_ml
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)

        # 加载配置
        raw_config, _, _ = load_json_config(self.config_path)
        self.config = normalize_category_config(raw_config)
        if self.confidence_threshold is not None:
            self.config.setdefault("ai_settings", {})["confidence_threshold"] = self.confidence_threshold

        # 初始化组件
        self.classifier = BookmarkClassifier(
            config_path=self.config_path,
            enable_ml=use_ml,
            config=self.config,
        )
        self.standardizer = TaxonomyService(self.config)
        self.loader = BookmarkLoader(max_workers=min(self.max_workers, 8))
        self.deduplicator = BookmarkDeduplicator()
        self.organization = OrganizationPipeline(self.standardizer)
        self.exporter = DataExporter(config=self.config)

        self.stats = self._init_stats()

    def _init_stats(self) -> Dict:
        return {
            "total_bookmarks": 0,
            "processed_bookmarks": 0,
            "duplicates_removed": 0,
            "errors": 0,
            "processing_time": 0.0,
            "categories_found": {},
            "files_processed": 0,
        }

    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
    ) -> Dict:
        """处理书签文件：加载 -> 去重 -> 分类 -> 组织 -> 导出"""
        start_time = time.time()
        self.stats = self._init_stats()
        self.logger.info(f"开始处理 {len(input_files)} 个文件")
        os.makedirs(output_dir, exist_ok=True)

        # 1. 加载
        all_bookmarks, load_stats = self.loader.load_from_files(input_files, limit=limit)
        self.stats["files_processed"] = load_stats["files_loaded"]
        self.stats["total_bookmarks"] = len(all_bookmarks)
        if not all_bookmarks:
            self.logger.warning("没有找到有效的书签")
            return self.stats

        # 2. 去重
        unique_bookmarks, duplicates, dedup_stats = self._deduplicate(all_bookmarks)
        self.stats["duplicates_removed"] = dedup_stats["duplicates_removed"]

        # 3. 分类
        self.logger.info(f"开始分类 {len(unique_bookmarks)} 个书签...")
        classified_bookmarks, class_stats = self._classify_batch(unique_bookmarks)
        self.stats["processed_bookmarks"] = class_stats["classified_count"]
        self.stats["errors"] += class_stats["errors"]
        self.stats["categories_found"] = class_stats["categories_found"]

        # 4. 训练（可选）
        if train_models:
            self._train_models(classified_bookmarks)

        # 5. 组织
        organized_bookmarks, _ = self.organization.organize(classified_bookmarks, self.config)

        # 6. 导出
        self.exporter.export_all_formats(organized_bookmarks, output_dir, stats=self.stats)

        self.stats["processing_time"] = time.time() - start_time
        self.logger.info(f"处理完成: {self.stats['processed_bookmarks']} 个书签已分类")
        return self.stats

    def _deduplicate(self, bookmarks: List[Dict]):
        """两阶段去重：快速 URL 去重 + 高级相似度去重"""
        seen_urls = set()
        unique: List[Dict] = []
        fast_duplicates: List[Dict] = []
        for bookmark in bookmarks:
            url = bookmark.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(bookmark)
            else:
                fast_duplicates.append(bookmark)

        advanced_unique, advanced_duplicates = self.deduplicator.remove_duplicates(unique)
        all_duplicates = fast_duplicates + advanced_duplicates

        stats = {
            "input_count": len(bookmarks),
            "output_count": len(advanced_unique),
            "duplicates_removed": len(all_duplicates),
            "fast_duplicates_removed": len(fast_duplicates),
            "advanced_duplicates_removed": len(advanced_duplicates),
        }
        return advanced_unique, all_duplicates, stats

    def _classify_batch(self, bookmarks: List[Dict]) -> tuple:
        """并行批量分类"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        classified: List[Dict] = []
        errors = 0
        categories_found: Dict[str, int] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_bookmark = {
                executor.submit(self._classify_single, b): b for b in bookmarks
            }
            for future in as_completed(future_to_bookmark):
                bookmark = future_to_bookmark[future]
                try:
                    result = future.result(timeout=30)
                    if result:
                        classified.append(result)
                        category = result.get("category", "未分类")
                        categories_found[category] = categories_found.get(category, 0) + 1
                except Exception as e:
                    self.logger.error(f"分类失败 {bookmark.get('url', 'unknown')}: {e}")
                    errors += 1

        stats = {
            "classified_count": len(classified),
            "cache_hits": 0,
            "errors": errors,
            "processing_time": 0.0,
            "categories_found": categories_found,
        }
        return classified, stats

    def _classify_single(self, bookmark: Dict) -> Optional[Dict]:
        """分类单个书签"""
        try:
            result = self.classifier.classify(bookmark["url"], bookmark["title"])
            return {
                **bookmark,
                "category": normalize_category_string(result.category),
                "subcategory": result.subcategory,
                "confidence": result.confidence,
                "alternatives": result.alternatives,
                "reasoning": result.reasoning,
                "method": result.method,
                "processing_time": result.processing_time,
                "facets": result.facets,
            }
        except Exception as e:
            self.logger.debug(f"分类失败 [{bookmark.get('url', 'unknown')}]: {e}")
            return None

    def _train_models(self, classified_bookmarks: List[Dict]):
        """使用高置信度结果训练 ML 模型"""
        if not self.classifier.ml_classifier:
            self.logger.warning("机器学习组件未启用，跳过训练")
            return
        self.logger.info("开始训练机器学习模型...")
        samples = 0
        for bookmark in classified_bookmarks:
            if bookmark.get("confidence", 0.0) > 0.8:
                try:
                    features = self.classifier.extract_features(bookmark["url"], bookmark["title"])
                    self.classifier.ml_classifier.online_learn(features, bookmark["category"])
                    samples += 1
                except Exception as e:
                    self.logger.debug(f"训练样本添加失败: {e}")
        self.logger.info(f"训练完成: 添加了 {samples} 个样本")

    def get_statistics(self) -> Dict:
        return self.stats.copy()

    def get_classifier_statistics(self) -> Dict:
        return self.classifier.get_statistics()
