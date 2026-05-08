"""
BookmarkProcessorCoordinator - 书签处理器协调层

协调各个 Pipeline 模块完成整个书签处理流程。

特性：
- 使用 Pipeline 模块进行职责分离
- 保持向后兼容的接口
- 详细的处理统计
"""

from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Tuple

from src.data.deduplicator import BookmarkDeduplicator
from src.data.exporter import DataExporter
from src.pipelines.bookmark_loader import BookmarkLoader
from src.pipelines.classification_pipeline import ClassificationPipeline
from src.pipelines.deduplication_pipeline import DeduplicationPipeline
from src.pipelines.export_pipeline import ExportPipeline
from src.pipelines.feedback_pipeline import FeedbackPipeline
from src.pipelines.organization_pipeline import OrganizationPipeline
from src.utils.standardizer import TaxonomyStandardizer


class BookmarkProcessorCoordinator:
    """书签处理器协调层
    
    深度: 高（简单接口，复杂的 Pipeline 协调逻辑）
    接口: process_files(...) -> stats
    
    示例:
        coordinator = BookmarkProcessorCoordinator(config, classifier)
        
        # 处理文件
        stats = coordinator.process_files(
            input_files=["bookmarks.html"],
            output_dir="output"
        )
        print(f"处理了 {stats['processed_bookmarks']} 个书签")
    """
    
    def __init__(
        self,
        config: Dict,
        config_path: Optional[str] = None,
        classifier=None,
        max_workers: int = 4,
        confidence_threshold: Optional[float] = None,
    ):
        """初始化协调层
        
        Args:
            config: 配置字典
            config_path: 配置文件路径
            classifier: AI 分类器
            max_workers: 最大并行线程数
            confidence_threshold: 置信度阈值
        """
        self.config = config
        self.config_path = config_path
        self.max_workers = max_workers
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)
        
        # 初始化标准化器
        self.standardizer = TaxonomyStandardizer(config)
        
        # 初始化各个 Pipeline
        self.loader = BookmarkLoader(max_workers=min(max_workers, 8))
        self.deduplication = DeduplicationPipeline()
        self.organization = OrganizationPipeline(self.standardizer)
        
        # 延迟初始化的组件
        self._classifier = classifier
        self._classification_pipeline: Optional[ClassificationPipeline] = None
        self._export_pipeline: Optional[ExportPipeline] = None
        self._feedback_pipeline: Optional[FeedbackPipeline] = None
        
        # 统计信息
        self.stats = self._init_stats()
    
    def _init_stats(self) -> Dict:
        """初始化统计信息"""
        return {
            "total_bookmarks": 0,
            "processed_bookmarks": 0,
            "duplicates_removed": 0,
            "errors": 0,
            "processing_time": 0.0,
            "categories_found": {},
            "files_processed": 0,
            "llm_organizer_used": False,
        }
    
    @property
    def classification_pipeline(self) -> ClassificationPipeline:
        """延迟初始化分类管道"""
        if self._classification_pipeline is None:
            if self._classifier is None:
                raise ValueError("分类器未初始化")
            self._classification_pipeline = ClassificationPipeline(
                config=self.config,
                classifier=self._classifier,
                max_workers=self.max_workers,
                confidence_threshold=self.confidence_threshold,
            )
        return self._classification_pipeline
    
    @property
    def export_pipeline(self) -> ExportPipeline:
        """延迟初始化导出管道"""
        if self._export_pipeline is None:
            exporter = DataExporter(config=self.config)
            self._export_pipeline = ExportPipeline(exporter=exporter)
        return self._export_pipeline
    
    @property
    def feedback_pipeline(self) -> FeedbackPipeline:
        """延迟初始化反馈管道"""
        if self._feedback_pipeline is None:
            self._feedback_pipeline = FeedbackPipeline(
                config=self.config,
                classifier=self._classifier,
            )
        return self._feedback_pipeline
    
    def process_files(
        self,
        input_files: List[str],
        output_dir: str = "output",
        train_models: bool = False,
        limit: int = 0,
        review_queue_path: Optional[str] = None,
    ) -> Dict:
        """处理多个书签文件
        
        Args:
            input_files: HTML 文件路径列表
            output_dir: 输出目录
            train_models: 是否训练模型
            limit: 限制处理的书签数量
            review_queue_path: 复核队列输出路径
            
        Returns:
            处理统计信息
        """
        import time
        start_time = time.time()
        
        # 重置统计
        self.stats = self._init_stats()
        
        self.logger.info(f"开始处理 {len(input_files)} 个文件")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 阶段 1: 加载书签
        all_bookmarks, load_stats = self.loader.load_from_files(
            input_files, limit=limit
        )
        self.stats["files_processed"] = load_stats["files_loaded"]
        self.stats["total_bookmarks"] = len(all_bookmarks)
        
        if not all_bookmarks:
            self.logger.warning("没有找到有效的书签")
            return self.stats
        
        # 阶段 2: 去重
        unique_bookmarks, duplicates, dedup_stats = self.deduplication.deduplicate(
            all_bookmarks
        )
        self.stats["duplicates_removed"] = dedup_stats["duplicates_removed"]
        
        # 阶段 3: 分类
        self.logger.info(f"开始分类 {len(unique_bookmarks)} 个书签...")
        classified_bookmarks, class_stats = self.classification_pipeline.classify_batch(
            unique_bookmarks
        )
        self.stats["processed_bookmarks"] = class_stats["classified_count"]
        self.stats["errors"] += class_stats["errors"]
        self.stats["categories_found"] = class_stats["categories_found"]
        
        # 阶段 3.5: 训练模型（可选）
        if train_models:
            self.classification_pipeline.train_models(classified_bookmarks)
        
        # 阶段 4: 组织
        organized_bookmarks, org_stats = self.organization.organize(
            classified_bookmarks, self.config
        )
        
        # 阶段 5: 导出复核队列（可选）
        if review_queue_path:
            self.feedback_pipeline.export_review_queue(
                classified_bookmarks, review_queue_path
            )
        
        # 阶段 6: 导出结果
        self.export_pipeline.export_all(
            organized_bookmarks, output_dir, stats=self.stats
        )
        
        # 更新统计
        self.stats["processing_time"] = time.time() - start_time
        
        self.logger.info(
            f"处理完成: {self.stats['processed_bookmarks']} 个书签已分类"
        )
        
        return self.stats
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
