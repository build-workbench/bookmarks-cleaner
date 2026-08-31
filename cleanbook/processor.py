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
        confidence_threshold: Optional[float] = None,
    ):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.max_workers = min(max_workers, self.MAX_WORKERS_LIMIT)
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
            config=self.config,
        )
        self.standardizer = TaxonomyService(self.config)
        title_rules = self.config.get("title_cleaning_rules")
        self.loader = BookmarkLoader(
            max_workers=min(self.max_workers, 8),
            title_rules=title_rules if isinstance(title_rules, dict) else None,
        )
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

        # 4. 组织
        organized_bookmarks, org_stats = self.organization.organize(classified_bookmarks, self.config)
        self.stats["subjects_found"] = org_stats.get("total_subjects", 0)

        # 5. 导出（附带分类器统计，供 markdown 报告使用）
        self.stats["classifier_stats"] = self.classifier.get_statistics()
        self.exporter.export_all_formats(organized_bookmarks, output_dir, stats=self.stats)

        self.stats["processing_time"] = time.time() - start_time
        self.logger.info(f"处理完成: {self.stats['processed_bookmarks']} 个书签已分类")
        return self.stats

    def _deduplicate(self, bookmarks: List[Dict]):
        """去重：由 BookmarkDeduplicator 统一处理（精确 URL 匹配 + 相似度检测）"""
        unique, duplicates = self.deduplicator.remove_duplicates(bookmarks)
        stats = {
            "input_count": len(bookmarks),
            "output_count": len(unique),
            "duplicates_removed": len(duplicates),
        }
        return unique, duplicates, stats

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
                    else:
                        # _classify_single 内部异常返回 None，同样计入错误
                        self.logger.debug(f"分类返回空结果 {bookmark.get('url', 'unknown')}")
                        errors += 1
                except Exception as e:
                    self.logger.error(f"分类失败 {bookmark.get('url', 'unknown')}: {e}")
                    errors += 1

        stats = {
            "classified_count": len(classified),
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

    def get_statistics(self) -> Dict:
        return self.stats.copy()

    def get_classifier_statistics(self) -> Dict:
        return self.classifier.get_statistics()
