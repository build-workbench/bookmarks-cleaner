"""
ExportPipeline - 导出处理管道

编排多格式导出，支持并行导出。

特性：
- 并行导出多种格式
- 支持 HTML、JSON、Markdown
- 详细的导出统计
"""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.data.exporter import DataExporter


class ExportPipeline:
    """导出处理管道
    
    深度: 高（简单接口，复杂的并行导出逻辑）
    接口: export_all(organized_bookmarks, output_dir, stats) -> (exported_files, stats)
    
    示例:
        pipeline = ExportPipeline(exporter)
        
        # 导出所有格式
        exported_files, stats = pipeline.export_all(organized_bookmarks, "output")
        print(f"导出了 {len(exported_files)} 个文件")
    """
    
    # 支持的导出格式及其对应的方法名
    SUPPORTED_FORMATS = {
        "html": "export_html",
        "json": "export_json",
        "markdown": "export_markdown",
    }
    
    def __init__(
        self,
        exporter: DataExporter,
        default_formats: Optional[List[str]] = None,
        max_workers: int = 3,
    ):
        """初始化导出管道
        
        Args:
            exporter: 数据导出器实例
            default_formats: 默认导出格式列表
            max_workers: 并行导出的最大线程数
        """
        self.exporter = exporter
        self.default_formats = default_formats or ["html", "json", "markdown"]
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.stats = {
            "exported_files": [],
            "failed_formats": [],
            "export_time": 0.0,
        }
    
    def export_all(
        self,
        organized_bookmarks: Dict,
        output_dir: str,
        stats: Optional[Dict] = None,
        formats: Optional[List[str]] = None,
        base_filename: str = "bookmarks"
    ) -> Tuple[List[str], Dict]:
        """导出所有格式
        
        Args:
            organized_bookmarks: 组织后的书签字典
            output_dir: 输出目录
            stats: 附加的统计信息
            formats: 要导出的格式列表（默认使用 default_formats）
            base_filename: 基础文件名
            
        Returns:
            (exported_files, stats) 元组
        """
        self._reset_stats()
        
        # 确定要导出的格式
        export_formats = formats or self.default_formats
        
        # 验证格式
        for fmt in export_formats:
            if fmt not in self.SUPPORTED_FORMATS:
                raise ValueError(f"不支持的导出格式: {fmt}")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        import time
        start_time = time.time()
        
        # 构建导出任务
        export_tasks = []
        for fmt in export_formats:
            filename = f"{base_filename}_{timestamp}.{fmt}"
            output_file = os.path.join(output_dir, filename)
            export_tasks.append((fmt, output_file))
        
        # 并行导出
        exported_files: List[str] = []
        failed_formats: List[str] = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for fmt, output_file in export_tasks:
                # 获取导出方法
                method_name = self.SUPPORTED_FORMATS[fmt]
                export_method = getattr(self.exporter, method_name)
                
                # 提交导出任务
                future = executor.submit(
                    export_method,
                    organized_bookmarks,
                    output_file,
                    stats
                )
                futures[future] = (fmt, output_file)
            
            # 收集结果
            for future in as_completed(futures):
                fmt, output_file = futures[future]
                try:
                    future.result()
                    exported_files.append(output_file)
                    self.logger.info(f"导出 {fmt} 格式成功: {output_file}")
                except Exception as e:
                    failed_formats.append(fmt)
                    self.logger.error(f"导出 {fmt} 格式失败: {e}")
        
        # 更新统计
        self.stats["exported_files"] = exported_files
        self.stats["failed_formats"] = failed_formats
        self.stats["export_time"] = time.time() - start_time
        
        self.logger.info(f"结果已导出到: {output_dir}")
        
        return exported_files, self.stats.copy()
    
    def export_single(
        self,
        organized_bookmarks: Dict,
        output_file: str,
        format_type: str,
        stats: Optional[Dict] = None
    ) -> bool:
        """导出单个格式
        
        Args:
            organized_bookmarks: 组织后的书签字典
            output_file: 输出文件路径
            format_type: 格式类型（html/json/markdown）
            stats: 附加的统计信息
            
        Returns:
            是否成功导出
        """
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的导出格式: {format_type}")
        
        try:
            # 获取导出方法
            method_name = self.SUPPORTED_FORMATS[format_type]
            export_method = getattr(self.exporter, method_name)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            
            # 执行导出
            export_method(organized_bookmarks, output_file, stats)
            self.logger.info(f"导出 {format_type} 格式成功: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"导出 {format_type} 格式失败: {e}")
            return False
    
    def _reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "exported_files": [],
            "failed_formats": [],
            "export_time": 0.0,
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
