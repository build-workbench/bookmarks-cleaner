"""
Report Generator - 报告生成器

负责生成分类报告和统计摘要。
"""

import json
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ReportGenerator:
    """报告生成器

    深度: 中（统一接口，多种格式）
    接口: generate(results) -> Report
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def generate(
        self,
        classified_bookmarks: List[Dict],
        format: str = "all",
        prefix: str = "",
    ) -> Dict[str, Path]:
        """生成报告

        Args:
            classified_bookmarks: 分类后的书签列表
            format: 输出格式 ("json", "markdown", "all")
            prefix: 文件名前缀

        Returns:
            生成的报告文件路径字典
        """
        reports = {}

        # 统计数据
        stats = self._calculate_stats(classified_bookmarks)

        # 生成JSON报告
        if format in ("json", "all"):
            json_path = self._generate_json_report(
                classified_bookmarks, stats, prefix
            )
            reports["json"] = json_path

        # 生成Markdown报告
        if format in ("markdown", "all"):
            md_path = self._generate_markdown_report(
                classified_bookmarks, stats, prefix
            )
            reports["markdown"] = md_path

        self.logger.info(f"生成了 {len(reports)} 个报告文件")
        return reports

    def _calculate_stats(self, bookmarks: List[Dict]) -> Dict:
        """计算统计数据"""
        if not bookmarks:
            return {"total": 0}

        # 分类统计
        categories = [b.get("category", "未分类") for b in bookmarks]
        category_counts = Counter(categories)

        # 置信度统计
        confidences = [
            b.get("confidence", 0) for b in bookmarks if "confidence" in b
        ]
        avg_confidence = (
            sum(confidences) / len(confidences) if confidences else 0
        )

        # 方法统计
        methods = [b.get("method", "unknown") for b in bookmarks]
        method_counts = Counter(methods)

        # 缓存统计
        cached_count = sum(1 for b in bookmarks if b.get("from_cache"))

        return {
            "total": len(bookmarks),
            "categories": dict(category_counts.most_common(20)),
            "avg_confidence": avg_confidence,
            "methods": dict(method_counts),
            "cached_count": cached_count,
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_json_report(
        self,
        bookmarks: List[Dict],
        stats: Dict,
        prefix: str,
    ) -> Path:
        """生成JSON报告"""
        filename = f"{prefix}classification_report.json" if prefix else "classification_report.json"
        path = self.output_dir / filename

        report = {
            "statistics": stats,
            "bookmarks": bookmarks,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.info(f"JSON报告: {path}")
        return path

    def _generate_markdown_report(
        self,
        bookmarks: List[Dict],
        stats: Dict,
        prefix: str,
    ) -> Path:
        """生成Markdown报告"""
        filename = f"{prefix}report.md" if prefix else "report.md"
        path = self.output_dir / filename

        lines = [
            "# 书签分类报告",
            "",
            f"**生成时间**: {stats.get('timestamp', 'N/A')}",
            "",
            "## 统计概览",
            "",
            f"- **总书签数**: {stats.get('total', 0)}",
            f"- **平均置信度**: {stats.get('avg_confidence', 0):.2%}",
            f"- **缓存命中**: {stats.get('cached_count', 0)}",
            "",
            "## 分类分布",
            "",
        ]

        # 分类分布表格
        categories = stats.get("categories", {})
        if categories:
            lines.extend(
                [
                    "| 分类 | 数量 |",
                    "|------|------|",
                ]
            )
            for category, count in list(categories.items())[:20]:
                lines.append(f"| {category} | {count} |")

        # 方法分布
        methods = stats.get("methods", {})
        if methods:
            lines.extend(
                [
                    "",
                    "## 分类方法",
                    "",
                ]
            )
            for method, count in methods.items():
                lines.append(f"- **{method}**: {count}")

        lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.logger.info(f"Markdown报告: {path}")
        return path
