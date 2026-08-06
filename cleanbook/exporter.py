"""数据导出器 - 支持 HTML/JSON/Markdown 格式"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from cleanbook import __version__
from cleanbook.text_utils import clean_title as clean_emoji_title


class DataExporter:
    """数据导出器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    @property
    def export_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def export_html(self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None):
        html_content = self._generate_html_content(organized_bookmarks, stats)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html_content(self, organized_bookmarks: Dict, stats: Optional[Dict] = None) -> str:
        html_parts = [
            "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
            "<!-- This is an automatically generated file.",
            "     It will be read and overwritten.",
            "     DO NOT EDIT! -->",
            '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
            "<TITLE>Bookmarks</TITLE>",
            "<H1>Bookmarks</H1>",
        ]
        if stats:
            html_parts.append("<!--")
            html_parts.append(f"    Generator: CleanBook v{__version__}")
            html_parts.append(f"    Export Time: {self.export_timestamp}")
            html_parts.append(
                f'    Processed Bookmarks: {stats.get("processed_bookmarks", 0)} / {stats.get("total_bookmarks", 0)}'
            )
            html_parts.append("-->")
        html_parts.append("<DL><p>")
        html_parts.append('    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true">收藏夹栏</H3>')
        html_parts.append("    <DL><p>")

        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            has_sub_items = any(len(sc.get("_items", [])) > 0 for sc in subcategories.values())
            if not items and not has_sub_items:
                continue
            html_parts.append(f"        <DT><H3>{self._escape_html(category)}</H3>")
            html_parts.append("        <DL><p>")
            for item in items:
                html_parts.append(self._format_bookmark_html(item, indent="            "))
            for subcat_name, subcat_data in subcategories.items():
                sub_items = subcat_data.get("_items", [])
                if not sub_items:
                    continue
                html_parts.append(f"            <DT><H3>{self._escape_html(subcat_name)}</H3>")
                html_parts.append("            <DL><p>")
                for item in sub_items:
                    html_parts.append(self._format_bookmark_html(item, indent="                "))
                html_parts.append("            </DL><p>")
            html_parts.append("        </DL><p>")

        html_parts.append("    </DL><p>")
        html_parts.append("</DL><p>")
        html_parts.append("</HTML>")
        return "\n".join(html_parts)

    def _format_bookmark_html(self, item: Dict, indent: str = "        ") -> str:
        url = self._escape_html(item.get("url", ""))
        title = self._escape_html(item.get("title", "无标题"))
        add_date = item.get("add_date", "")
        confidence = item.get("confidence", 0)
        attributes = [f'HREF="{url}"']
        if add_date:
            attributes.append(f'ADD_DATE="{add_date}"')
        confidence_indicator = self._get_confidence_indicator(confidence)
        clean_title_str = clean_emoji_title(title)
        display_title = f"{confidence_indicator} {clean_title_str}" if confidence_indicator else clean_title_str
        return f'{indent}<DT><A {" ".join(attributes)}>{display_title}</A>'

    def _get_confidence_indicator(self, confidence: float) -> str:
        if not self.config.get("show_confidence_indicator", True):
            return ""
        if confidence >= 0.9:
            return "🟢"
        if confidence >= 0.7:
            return "🟡"
        if confidence >= 0.5:
            return "🟠"
        if confidence > 0:
            return "🔴"
        return ""

    def _escape_html(self, text: str) -> str:
        if not text:
            return ""
        return (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#x27;")
        )

    def _category_has_items(self, category_data: Dict) -> bool:
        if category_data.get("_items"):
            return True
        return any(len(sc.get("_items", [])) > 0 for sc in (category_data.get("_subcategories", {}) or {}).values())

    def _prune_empty(self, organized_bookmarks: Dict) -> Dict:
        pruned = {}
        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            filtered_sub = {n: d for n, d in subcategories.items() if len(d.get("_items", [])) > 0}
            if items or filtered_sub:
                pruned[category] = {"_items": items, "_subcategories": filtered_sub}
        return pruned

    def export_json(self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None):
        filtered = self._prune_empty(organized_bookmarks)
        metadata = {
            "export_time": self.export_timestamp,
            "processor_version": __version__,
            "format_version": "3.0",
            "generator": "CleanBook",
            "total_categories": len(filtered),
            "total_bookmarks": self._count_total_bookmarks(filtered),
        }
        data = {"metadata": metadata, "statistics": dict(stats) if isinstance(stats, dict) else {}, "bookmarks": filtered}
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_markdown(self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None):
        md_content = self._generate_markdown_content(organized_bookmarks, stats)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_markdown_content(self, organized_bookmarks: Dict, stats: Optional[Dict] = None) -> str:
        lines = ["# 书签分类报告", "", f"> 生成时间: {self.export_timestamp}", ""]
        if stats:
            lines.append("## 📊 处理统计")
            lines.append("")
            lines.append(f"- **总书签数**: {stats.get('total_bookmarks', 0)}")
            lines.append(f"- **已处理书签**: {stats.get('processed_bookmarks', 0)}")
            lines.append(f"- **移除重复数**: {stats.get('duplicates_removed', 0)}")
            lines.append(f"- **处理时间**: {stats.get('processing_time', 0):.2f} 秒")
            lines.append("")
            classifier_stats = stats.get("classifier_stats", {})
            if classifier_stats:
                lines.append("### 🤖 分类方法统计")
                methods = classifier_stats.get("classification_methods", {})
                if methods:
                    total = methods.get("total", 1)
                    lines.append(f"- **规则引擎**: {methods.get('rule_engine', 0)} ({methods.get('rule_engine', 0) / total:.1%})")
                    lines.append(f"- **机器学习**: {methods.get('ml_classifier', 0)} ({methods.get('ml_classifier', 0) / total:.1%})")
                    lines.append(f"- **未分类**: {methods.get('unclassified (fallback)', 0)} ({methods.get('unclassified (fallback)', 0) / total:.1%})")
                lines.append(f"- **平均置信度**: {classifier_stats.get('average_confidence', 0):.2f}")
                lines.append("")
            categories_found = stats.get("categories_found", {})
            if categories_found:
                lines.append("### 📁 分类分布")
                for category, count in sorted(categories_found.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"  - {category}: {count} 个")
                lines.append("")

        non_empty = [c for c, d in organized_bookmarks.items() if self._category_has_items(d)]
        lines.append("## 📚 目录")
        lines.append("")
        for i, category in enumerate(non_empty, 1):
            lines.append(f"{i}. [{category}](#{self._slugify(category)})")
        lines.append("")

        for category, category_data in organized_bookmarks.items():
            if not self._category_has_items(category_data):
                continue
            lines.append(f"## {category}")
            lines.append("")
            items = category_data.get("_items", [])
            if items:
                for item in items:
                    lines.append(self._format_bookmark_markdown(item))
                lines.append("")
            subcategories = category_data.get("_subcategories", {})
            for subcat_name, subcat_data in subcategories.items():
                sub_items = subcat_data.get("_items", [])
                if not sub_items:
                    continue
                lines.append(f"### {subcat_name}")
                lines.append("")
                for item in sub_items:
                    lines.append(self._format_bookmark_markdown(item))
                lines.append("")

        lines.append("---")
        lines.append(f"*由 CleanBook v{__version__} 生成 - {self.export_timestamp}*")
        return "\n".join(lines)

    def _format_bookmark_markdown(self, item: Dict) -> str:
        url = item.get("url", "")
        title = item.get("title", "无标题")
        confidence = item.get("confidence", 0)
        confidence_indicator = self._get_confidence_indicator(confidence)
        confidence_text = f" ({confidence:.2f})" if confidence > 0 else ""
        clean_title_str = clean_emoji_title(title)
        prefix = f"{confidence_indicator} " if confidence_indicator else ""
        return f"- {prefix}[{clean_title_str}]({url}){confidence_text}"

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", slug)

    def _count_total_bookmarks(self, organized_bookmarks: Dict) -> int:
        total = 0
        for category_data in organized_bookmarks.values():
            total += len(category_data.get("_items", []))
            for subcat_data in (category_data.get("_subcategories", {}) or {}).values():
                total += len(subcat_data.get("_items", []))
        return total

    def export_all_formats(self, organized_bookmarks: Dict, output_dir: str, base_filename: str = "bookmarks", stats: Optional[Dict] = None):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = []
        for fmt, method in [("html", self.export_html), ("json", self.export_json), ("markdown", self.export_markdown)]:
            try:
                output_file = os.path.join(output_dir, f"{base_filename}_{timestamp}.{fmt}")
                method(organized_bookmarks, output_file, stats)
                exported_files.append(output_file)
            except Exception as e:
                print(f"警告: 导出{fmt}格式失败: {e}")
        return exported_files
