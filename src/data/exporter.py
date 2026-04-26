"""
Data Exporter - 数据导出器
支持多种格式的书签导出（HTML/JSON/Markdown/CSV/XML/OPML）
"""

import csv
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional
from xml.dom import minidom

from src import __version__
from src.utils.emoji_cleaner import clean_title as clean_emoji_title


class DataExporter:
    """数据导出器 - 支持多种格式的书签导出"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.supported_formats = ["html", "json", "markdown", "csv", "xml", "opml"]

    @property
    def export_timestamp(self) -> str:
        """每次访问时返回当前时间，确保导出时间戳始终准确。"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def export_html(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出HTML格式 - 可导入浏览器"""
        html_content = self._generate_html_content(organized_bookmarks, stats)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html_content(
        self, organized_bookmarks: Dict, stats: Optional[Dict] = None
    ) -> str:
        """生成符合浏览器收藏夹栏规范的HTML内容，用于完全覆盖"""
        html_parts = []

        # HTML标准头部
        html_parts.append("<!DOCTYPE NETSCAPE-Bookmark-file-1>")
        html_parts.append("<!-- This is an automatically generated file.")
        html_parts.append("     It will be read and overwritten.")
        html_parts.append("     DO NOT EDIT! -->")
        html_parts.append(
            '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
        )
        html_parts.append("<TITLE>Bookmarks</TITLE>")
        html_parts.append("<H1>Bookmarks</H1>")

        # 添加统计信息注释
        if stats:
            html_parts.append("<!--")
            html_parts.append(f"    Generator: AI智能书签分类系统 v{__version__}")
            html_parts.append(f"    Export Time: {self.export_timestamp}")
            html_parts.append(
                f'    Processed Bookmarks: {stats.get("processed_bookmarks", 0)} / {stats.get("total_bookmarks", 0)}'
            )

            classifier_stats = stats.get("classifier_stats", {})
            if classifier_stats:
                methods = classifier_stats.get("classification_methods", {})
                if methods:
                    html_parts.append("    Classification Stats:")
                    html_parts.append(
                        f'      - Rule Engine: {methods.get("rule_engine", 0)}'
                    )
                    html_parts.append(
                        f'      - ML Classifier: {methods.get("ml_classifier", 0)}'
                    )
                    html_parts.append(
                        f'      - Unclassified: {methods.get("unclassified (fallback)", 0)}'
                    )
            if stats.get("llm_organizer_used"):
                llm_stats = stats.get("llm_organizer_stats", {})
                html_parts.append("    LLM Organizer: enabled")
                if llm_stats:
                    html_parts.append(
                        f'      - Calls: {llm_stats.get("calls", 0)} (cache_hits: {llm_stats.get("cache_hits", 0)})'
                    )
                llm_meta = stats.get("llm_organizer_meta")
                if llm_meta:
                    model = llm_meta.get("llm_model", "")
                    html_parts.append(f"      - Model: {model}")
                    primary_order = llm_meta.get("primary_order") or []
                    if primary_order:
                        html_parts.append(
                            f'      - Primary Order: {", ".join(primary_order[:8])}'
                        )
            html_parts.append("-->")

        html_parts.append("<DL><p>")

        # 创建一个"收藏夹栏"文件夹
        html_parts.append('    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true">收藏夹栏</H3>')
        html_parts.append("    <DL><p>")

        # 直接在收藏夹栏内生成分类文件夹（跳过空分类/子分类）
        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            has_sub_items = any(
                len(sc.get("_items", [])) > 0 for sc in subcategories.values()
            )
            if not items and not has_sub_items:
                continue

            html_parts.append(f"        <DT><H3>{self._escape_html(category)}</H3>")
            html_parts.append("        <DL><p>")

            # 直接在分类下的书签
            for item in items:
                html_parts.append(
                    self._format_bookmark_html(item, indent="            ")
                )

            # 子分类
            for subcat_name, subcat_data in subcategories.items():
                sub_items = subcat_data.get("_items", [])
                if not sub_items:
                    continue
                html_parts.append(
                    f"            <DT><H3>{self._escape_html(subcat_name)}</H3>"
                )
                html_parts.append("            <DL><p>")
                for item in sub_items:
                    html_parts.append(
                        self._format_bookmark_html(item, indent="                ")
                    )
                html_parts.append("            </DL><p>")

            html_parts.append("        </DL><p>")

        # 闭合所有标签
        html_parts.append("    </DL><p>")  # 闭合收藏夹栏
        html_parts.append("</DL><p>")  # 闭合根
        html_parts.append("</HTML>")

        return "\n".join(html_parts)

    def _format_bookmark_html(self, item: Dict, indent: str = "        ") -> str:
        """格式HTML书签项"""
        url = self._escape_html(item.get("url", ""))
        title = self._escape_html(item.get("title", "无标题"))
        add_date = item.get("add_date", "")
        confidence = item.get("confidence", 0)

        # 构建属性
        attributes = [f'HREF="{url}"']
        if add_date:
            attributes.append(f'ADD_DATE="{add_date}"')

        # 添加置信度信息到标题
        confidence_indicator = self._get_confidence_indicator(confidence)

        # 使用统一的清理工具，移除开头指示符，避免累加
        clean_title = clean_emoji_title(title)

        display_title = (
            f"{confidence_indicator} {clean_title}"
            if confidence_indicator
            else clean_title
        )

        return f'{indent}<DT><A {" ".join(attributes)}>{display_title}</A>'

    def _get_confidence_indicator(self, confidence: float) -> str:
        """获取置信度指示符"""
        if not self.config.get("show_confidence_indicator", True):
            return ""

        if confidence >= 0.9:
            return "🟢"
        elif confidence >= 0.7:
            return "🟡"
        elif confidence >= 0.5:
            return "🟠"
        elif confidence > 0:
            return "🔴"
        return ""

    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    def _category_has_items(self, category_data: Dict) -> bool:
        """判断分类是否包含任何书签项（自身或子分类）。"""
        items = category_data.get("_items", [])
        if items:
            return True
        subcategories = category_data.get("_subcategories", {})
        return any(len(sc.get("_items", [])) > 0 for sc in subcategories.values())

    def _prune_empty(self, organized_bookmarks: Dict) -> Dict:
        """移除空的分类与空的子分类。"""
        pruned = {}
        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            filtered_sub = {
                name: data
                for name, data in subcategories.items()
                if len(data.get("_items", [])) > 0
            }
            if items or filtered_sub:
                pruned[category] = {"_items": items, "_subcategories": filtered_sub}
        return pruned

    def export_json(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出JSON格式 - 详细数据"""
        filtered = self._prune_empty(organized_bookmarks)
        metadata = {
            "export_time": self.export_timestamp,
            "processor_version": __version__,
            "format_version": "2.0",
            "generator": "AI智能书签分类系统",
            "total_categories": len(filtered),
            "total_bookmarks": self._count_total_bookmarks(filtered),
        }
        statistics = dict(stats) if isinstance(stats, dict) else {}

        if isinstance(stats, dict):
            meta = stats.get("llm_organizer_meta")
            if meta:
                metadata["llm_organizer"] = meta
            llm_stats = stats.get("llm_organizer_stats")
            if llm_stats:
                statistics["llm_organizer"] = llm_stats

        data = {"metadata": metadata, "statistics": statistics, "bookmarks": filtered}

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def export_markdown(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出Markdown格式 - 可读性强"""
        md_content = self._generate_markdown_content(organized_bookmarks, stats)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_markdown_content(
        self, organized_bookmarks: Dict, stats: Optional[Dict] = None
    ) -> str:
        """生成Markdown内容"""
        lines = []

        # 文档头部
        lines.append("# AI智能书签分类报告")
        lines.append("")
        lines.append(f"> 生成时间: {self.export_timestamp}")
        lines.append("")

        # 统计信息
        if stats:
            lines.append("## 📊 处理统计")
            lines.append("")
            lines.append(f"- **总书签数**: {stats.get('total_bookmarks', 0)}")
            lines.append(f"- **已处理书签**: {stats.get('processed_bookmarks', 0)}")
            lines.append(f"- **移除重复数**: {stats.get('duplicates_removed', 0)}")
            lines.append(f"- **处理时间**: {stats.get('processing_time', 0):.2f} 秒")
            lines.append(
                f"- **处理速度**: {stats.get('processing_speed_bps', 0):.2f} 书签/秒"
            )
            lines.append("")

            if stats.get("llm_organizer_used"):
                lines.append(f"- **LLM 深度整理**: ✅ 已启用")
                llm_meta = stats.get("llm_organizer_meta", {})
                llm_stats = stats.get("llm_organizer_stats", {})
                model = (
                    llm_meta.get("llm_model") if isinstance(llm_meta, dict) else None
                )
                if model:
                    lines.append(f"  - 使用模型: {model}")
                if llm_meta:
                    primary_order = llm_meta.get("primary_order") or []
                    if primary_order:
                        joined = ", ".join(primary_order[:8])
                        lines.append(f"  - 主分类顺序: {joined}")
                if llm_stats:
                    lines.append(
                        f"  - 调用次数: {llm_stats.get('calls', 0)} (缓存命中 {llm_stats.get('cache_hits', 0)})"
                    )
                lines.append("")
            else:
                lines.append(f"- **LLM 深度整理**: ❌ 未启用或调用失败")
                lines.append("")

            # 分类方法统计
            classifier_stats = stats.get("classifier_stats", {})
            if classifier_stats:
                lines.append("### 🤖 分类方法统计")
                methods = classifier_stats.get("classification_methods", {})
                if methods:
                    total = methods.get("total", 1)
                    lines.append(
                        f"- **规则引擎**: {methods.get('rule_engine', 0)} ({methods.get('rule_engine', 0) / total:.1%})"
                    )
                    lines.append(
                        f"- **机器学习**: {methods.get('ml_classifier', 0)} ({methods.get('ml_classifier', 0) / total:.1%})"
                    )
                    lines.append(
                        f"- **未分类**: {methods.get('unclassified (fallback)', 0)} ({methods.get('unclassified (fallback)', 0) / total:.1%})"
                    )
                lines.append(
                    f"- **平均置信度**: {classifier_stats.get('average_confidence', 0):.2f}"
                )
                lines.append("")

            # 分类分布
            categories_found = stats.get("categories_found", {})
            if categories_found:
                lines.append(f"### 📁 分类分布")
                for category, count in sorted(
                    categories_found.items(), key=lambda x: x[1], reverse=True
                ):
                    lines.append(f"  - {category}: {count} 个")

            lines.append("")

        # 目录（仅非空分类）
        lines.append("## 📚 目录")
        lines.append("")
        non_empty_categories = [
            c for c, d in organized_bookmarks.items() if self._category_has_items(d)
        ]
        for i, category in enumerate(non_empty_categories, 1):
            lines.append(f"{i}. [{category}](#{self._slugify(category)})")
        lines.append("")

        # 分类内容（仅非空分类/子分类）
        for category, category_data in organized_bookmarks.items():
            if not self._category_has_items(category_data):
                continue
            lines.append(f"## {category}")
            lines.append("")

            # 直接在分类下的书签
            items = category_data.get("_items", [])
            if items:
                for item in items:
                    lines.append(self._format_bookmark_markdown(item))
                lines.append("")

            # 子分类
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

        # 页脚
        lines.append("---")
        lines.append(
            f"*由 AI智能书签分类系统 v{__version__} 生成 - {self.export_timestamp}*"
        )

        return "\n".join(lines)

    def _format_bookmark_markdown(self, item: Dict) -> str:
        """格式Markdown书签项"""
        url = item.get("url", "")
        title = item.get("title", "无标题")
        confidence = item.get("confidence", 0)

        confidence_indicator = self._get_confidence_indicator(confidence)
        confidence_text = f" ({confidence:.2f})" if confidence > 0 else ""
        clean_title = clean_emoji_title(title)
        prefix = f"{confidence_indicator} " if confidence_indicator else ""
        return f"- {prefix}[{clean_title}]({url}){confidence_text}"

    def _slugify(self, text: str) -> str:
        """将文本转换为适合作Markdown锦点的格式"""
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug

    def export_csv(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出CSV格式 - 适合数据分析"""
        with open(output_file, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = [
                "category",
                "subcategory",
                "title",
                "url",
                "confidence",
                "method",
                "add_date",
                "source_file",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for category, category_data in organized_bookmarks.items():
                items = category_data.get("_items", [])
                for item in items:
                    writer.writerow(
                        {
                            "category": category,
                            "subcategory": "",
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "confidence": item.get("confidence", 0),
                            "method": item.get("method", ""),
                            "add_date": item.get("add_date", ""),
                            "source_file": item.get("source_file", ""),
                        }
                    )

                subcategories = category_data.get("_subcategories", {})
                for subcat_name, subcat_data in subcategories.items():
                    sub_items = subcat_data.get("_items", [])
                    for item in sub_items:
                        writer.writerow(
                            {
                                "category": category,
                                "subcategory": subcat_name,
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "confidence": item.get("confidence", 0),
                                "method": item.get("method", ""),
                                "add_date": item.get("add_date", ""),
                                "source_file": item.get("source_file", ""),
                            }
                        )

    def export_xml(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出XML格式 - 结构化数据"""
        root = ET.Element("bookmarks")
        root.set("version", "2.0")
        root.set("generator", "AI智能书签分类系统")
        root.set("export_time", self.export_timestamp)

        if stats:
            stats_elem = ET.SubElement(root, "statistics")
            for key, value in stats.items():
                if isinstance(value, dict):
                    dict_elem = ET.SubElement(stats_elem, key)
                    for sub_key, sub_value in value.items():
                        sub_elem = ET.SubElement(dict_elem, "item")
                        sub_elem.set("name", str(sub_key))
                        sub_elem.text = str(sub_value)
                else:
                    stat_elem = ET.SubElement(stats_elem, key)
                    stat_elem.text = str(value)

        bookmarks_elem = ET.SubElement(root, "categories")

        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            has_sub_items = any(
                len(sc.get("_items", [])) > 0 for sc in subcategories.values()
            )
            if not items and not has_sub_items:
                continue
            category_elem = ET.SubElement(bookmarks_elem, "category")
            category_elem.set("name", category)

            if items:
                items_elem = ET.SubElement(category_elem, "items")
                for item in items:
                    self._add_bookmark_xml(items_elem, item)

            filtered_sub = {
                n: d for n, d in subcategories.items() if len(d.get("_items", [])) > 0
            }
            if filtered_sub:
                subcats_elem = ET.SubElement(category_elem, "subcategories")
                for subcat_name, subcat_data in filtered_sub.items():
                    subcat_elem = ET.SubElement(subcats_elem, "subcategory")
                    subcat_elem.set("name", subcat_name)
                    sub_items = subcat_data.get("_items", [])
                    sub_items_elem = ET.SubElement(subcat_elem, "items")
                    for item in sub_items:
                        self._add_bookmark_xml(sub_items_elem, item)

        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_str)

    def _add_bookmark_xml(self, parent: ET.Element, item: Dict):
        """添加书签XML元素"""
        bookmark_elem = ET.SubElement(parent, "bookmark")
        bookmark_elem.set("url", item.get("url", ""))
        bookmark_elem.set("title", item.get("title", ""))
        if item.get("confidence"):
            bookmark_elem.set("confidence", str(item["confidence"]))
        if item.get("method"):
            bookmark_elem.set("method", item["method"])
        if item.get("add_date"):
            bookmark_elem.set("add_date", item["add_date"])
        if item.get("source_file"):
            bookmark_elem.set("source_file", item["source_file"])

    def export_opml(
        self, organized_bookmarks: Dict, output_file: str, stats: Optional[Dict] = None
    ):
        """导出OPML格式 - RSS/阅读器兼容"""
        root = ET.Element("opml")
        root.set("version", "2.0")

        head = ET.SubElement(root, "head")
        ET.SubElement(head, "title").text = "AI智能书签分类结果"
        ET.SubElement(head, "dateCreated").text = self.export_timestamp
        ET.SubElement(head, "generator").text = f"AI智能书签分类系统 v{__version__}"

        body = ET.SubElement(root, "body")

        for category, category_data in organized_bookmarks.items():
            items = category_data.get("_items", [])
            subcategories = category_data.get("_subcategories", {})
            has_sub_items = any(
                len(sc.get("_items", [])) > 0 for sc in subcategories.values()
            )
            if not items and not has_sub_items:
                continue
            category_outline = ET.SubElement(body, "outline")
            category_outline.set("text", category)
            category_outline.set("title", category)

            for item in items:
                item_outline = ET.SubElement(category_outline, "outline")
                item_outline.set("text", item.get("title", ""))
                item_outline.set("title", item.get("title", ""))
                item_outline.set("type", "link")
                item_outline.set("url", item.get("url", ""))

            for subcat_name, subcat_data in subcategories.items():
                sub_items = subcat_data.get("_items", [])
                if not sub_items:
                    continue
                subcat_outline = ET.SubElement(category_outline, "outline")
                subcat_outline.set("text", subcat_name)
                subcat_outline.set("title", subcat_name)
                for item in sub_items:
                    item_outline = ET.SubElement(subcat_outline, "outline")
                    item_outline.set("text", item.get("title", ""))
                    item_outline.set("title", item.get("title", ""))
                    item_outline.set("type", "link")
                    item_outline.set("url", item.get("url", ""))

        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_str)

    def _count_total_bookmarks(self, organized_bookmarks: Dict) -> int:
        """计算总书签数量"""
        total = 0
        for category_data in organized_bookmarks.values():
            total += len(category_data.get("_items", []))
            subcategories = category_data.get("_subcategories", {})
            for subcat_data in subcategories.values():
                total += len(subcat_data.get("_items", []))
        return total

    def export_all_formats(
        self,
        organized_bookmarks: Dict,
        output_dir: str,
        base_filename: str = "bookmarks",
        stats: Optional[Dict] = None,
    ):
        """导出所有支持的格式"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        export_methods = {
            "html": self.export_html,
            "json": self.export_json,
            "markdown": self.export_markdown,
            "csv": self.export_csv,
            "xml": self.export_xml,
            "opml": self.export_opml,
        }

        exported_files = []

        for format_name, export_method in export_methods.items():
            try:
                output_file = os.path.join(
                    output_dir, f"{base_filename}_{timestamp}.{format_name}"
                )
                export_method(organized_bookmarks, output_file, stats)
                exported_files.append(output_file)
            except Exception as e:
                print(f"警告: 导出{format_name}格式失败: {e}")

        return exported_files
