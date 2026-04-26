"""
Enhanced Bookmark Processing System - 增强版书签处理系统

主要改进：
1. 并行处理能力
2. 实时进度显示
3. 增量处理支持
4. 智能去重系统
5. 多格式输出
6. 详细统计分析
"""

import argparse
import glob
import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional, Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
import html
import re

from src import __version__
from src.classifiers.enhanced import ClassificationResult, EnhancedClassifier
from src.utils.emoji_cleaner import clean_title as clean_emoji_title
from src.utils.resource_loader import resolve_config_path


@dataclass
class ProcessingStats:
    """处理统计信息"""

    total_bookmarks: int = 0
    processed_bookmarks: int = 0
    duplicates_removed: int = 0
    errors_count: int = 0
    start_time: datetime = None
    end_time: datetime = None
    categories_found: Dict[str, int] = None
    avg_confidence: float = 0.0
    processing_speed: float = 0.0  # 书签/秒

    def __post_init__(self):
        if self.categories_found is None:
            self.categories_found = {}


class EnhancedBookmarkProcessor:
    """增强版书签处理器"""

    def __init__(self, config_file: str | None = None, max_workers: int = 4):
        resolved_path, _ = resolve_config_path(config_file)
        self.config_file = str(resolved_path)
        self.max_workers = max_workers
        self.classifier = EnhancedClassifier(self.config_file)

        # 处理状态
        self.processed_bookmarks = []
        self.stats = ProcessingStats()
        self.seen_urls = set()
        self.duplicate_hashes = set()

        # 线程安全锁
        self.stats_lock = Lock()
        self.seen_urls_lock = Lock()

        # 设置日志
        self.logger = self._setup_logger()

        # 加载学习数据
        self.classifier.load_learning_data()

    def _setup_logger(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # 文件输出
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler(
                f'logs/processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                encoding="utf-8",
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        return logger

    def load_bookmarks_from_files(self, input_files: List[str]) -> List[Dict]:
        """从多个HTML文件加载书签"""
        all_bookmarks = []

        self.logger.info(f"开始加载 {len(input_files)} 个书签文件...")

        for file_path in input_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                soup = BeautifulSoup(content, "lxml")
                links = soup.find_all("a")

                file_bookmarks = []
                for link in links:
                    url = link.get("href", "").strip()
                    title = (link.string or link.get_text() or url).strip()

                    if url and title and self._is_valid_url(url):
                        file_bookmarks.append(
                            {
                                "url": url,
                                "title": title,
                                "source_file": file_path,
                                "add_date": link.get("add_date", ""),
                                "last_modified": link.get("last_modified", ""),
                            }
                        )

                all_bookmarks.extend(file_bookmarks)
                self.logger.info(f"从 {file_path} 加载了 {len(file_bookmarks)} 个书签")

            except Exception as e:
                self.logger.error(f"处理文件 {file_path} 时出错: {e}")

        self.logger.info(f"总共加载了 {len(all_bookmarks)} 个书签")
        return all_bookmarks

    def _is_valid_url(self, url: str) -> bool:
        """验证URL是否有效"""
        if not url:
            return False

        # 过滤掉无效的URL
        invalid_prefixes = [
            "javascript:",
            "data:",
            "chrome:",
            "about:",
            "file:",
            "mailto:",
        ]
        for prefix in invalid_prefixes:
            if url.lower().startswith(prefix):
                return False

        # 检查是否为有效的HTTP/HTTPS URL
        return url.startswith(("http://", "https://"))

    def _generate_content_hash(self, url: str, title: str) -> str:
        """生成内容哈希用于去重"""
        # 标准化URL
        normalized_url = self._normalize_url(url)

        # 标准化标题
        normalized_title = self._normalize_title(title)

        # 生成哈希
        content = f"{normalized_url}::{normalized_title}"
        return hashlib.md5(content.encode()).hexdigest()

    def _normalize_url(self, url: str) -> str:
        """标准化URL"""
        try:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(url.lower())

            # 移除www前缀
            netloc = parsed.netloc.replace("www.", "")

            # 移除尾部斜杠
            path = parsed.path.rstrip("/")

            # 忽略常见的跟踪参数
            query = parsed.query
            if query:
                tracking_params = [
                    "utm_source",
                    "utm_medium",
                    "utm_campaign",
                    "utm_term",
                    "utm_content",
                    "fbclid",
                    "gclid",
                    "ref",
                    "source",
                    "from",
                ]
                query_parts = []
                for param in query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if key not in tracking_params:
                            query_parts.append(param)
                query = "&".join(query_parts)

            return urlunparse((parsed.scheme, netloc, path, "", query, ""))

        except Exception:
            return url.lower()

    def _normalize_title(self, title: str) -> str:
        """标准化标题"""
        if not title:
            return ""

        # 去除HTML实体
        title = html.unescape(title)
        # 先移除前缀 emoji 指示符，避免叠加影响（统一模块）
        title = clean_emoji_title(title)

        # 应用清理规则
        config = self.classifier.config
        cleaning_rules = config.get("title_cleaning_rules", {})

        # 替换规则
        for old, new in cleaning_rules.get("replacements", {}).items():
            title = title.replace(old, new)

        # 前缀清理
        for prefix in cleaning_rules.get("prefixes", []):
            if title.startswith(prefix):
                title = title[len(prefix) :].strip()

        # 后缀清理
        for suffix in cleaning_rules.get("suffixes", []):
            if title.endswith(suffix):
                title = title[: -len(suffix)].strip()

        return title.strip()

    def _is_duplicate(self, bookmark: Dict) -> bool:
        """检查是否为重复书签"""
        content_hash = self._generate_content_hash(bookmark["url"], bookmark["title"])

        if content_hash in self.duplicate_hashes:
            return True

        self.duplicate_hashes.add(content_hash)
        return False

    def _process_single_bookmark(self, bookmark: Dict) -> Optional[Dict]:
        """处理单个书签"""
        try:
            # 检查重复
            if self._is_duplicate(bookmark):
                with self.stats_lock:
                    self.stats.duplicates_removed += 1
                return None

            # 分类
            result = self.classifier.classify(
                bookmark["url"],
                bookmark["title"],
                context={"source_file": bookmark.get("source_file")},
            )

            # 构建结果
            processed_bookmark = {
                "url": bookmark["url"],
                "title": bookmark["title"],
                "category": result.category,
                "confidence": result.confidence,
                "alternatives": result.alternative_categories,
                "reasoning": result.reasoning,
                "features_used": result.features_used,
                "processing_time": result.processing_time,
                "source_file": bookmark.get("source_file", ""),
                "add_date": bookmark.get("add_date", ""),
                "last_modified": bookmark.get("last_modified", ""),
            }

            # 更新统计
            with self.stats_lock:
                self.stats.processed_bookmarks += 1
                self.stats.categories_found[result.category] = (
                    self.stats.categories_found.get(result.category, 0) + 1
                )

            return processed_bookmark

        except Exception as e:
            self.logger.error(f"处理书签失败 {bookmark.get('url', 'unknown')}: {e}")
            with self.stats_lock:
                self.stats.errors_count += 1
            return None

    def process_bookmarks(
        self, input_files: List[str], show_progress: bool = True
    ) -> List[Dict]:
        """主处理方法 - 支持并行处理"""
        self.logger.info("开始处理书签...")
        self.stats.start_time = datetime.now()

        # 加载书签
        all_bookmarks = self.load_bookmarks_from_files(input_files)
        self.stats.total_bookmarks = len(all_bookmarks)

        if not all_bookmarks:
            self.logger.error("没有找到有效的书签")
            return []

        # 并行处理
        processed_bookmarks = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交任务
            future_to_bookmark = {
                executor.submit(self._process_single_bookmark, bookmark): bookmark
                for bookmark in all_bookmarks
            }

            # 处理结果
            for future in as_completed(future_to_bookmark):
                try:
                    result = future.result()
                    if result:
                        processed_bookmarks.append(result)

                    # 显示进度
                    if show_progress and self.stats.processed_bookmarks % 50 == 0:
                        progress = (
                            (
                                self.stats.processed_bookmarks
                                + self.stats.duplicates_removed
                                + self.stats.errors_count
                            )
                            / self.stats.total_bookmarks
                            * 100
                        )
                        self.logger.info(
                            f"处理进度: {progress:.1f}% ({self.stats.processed_bookmarks} 处理完成, {self.stats.duplicates_removed} 重复, {self.stats.errors_count} 错误)"
                        )

                except Exception as e:
                    self.logger.error(f"获取处理结果时出错: {e}")
                    with self.stats_lock:
                        self.stats.errors_count += 1

        # 完成统计
        self.stats.end_time = datetime.now()
        processing_time = (self.stats.end_time - self.stats.start_time).total_seconds()
        self.stats.processing_speed = (
            len(processed_bookmarks) / processing_time if processing_time > 0 else 0
        )
        self.stats.avg_confidence = (
            sum(b["confidence"] for b in processed_bookmarks) / len(processed_bookmarks)
            if processed_bookmarks
            else 0
        )

        self.processed_bookmarks = processed_bookmarks

        self.logger.info(f"处理完成: {len(processed_bookmarks)} 个书签分类完成")
        self.logger.info(f"处理速度: {self.stats.processing_speed:.2f} 书签/秒")
        self.logger.info(f"平均置信度: {self.stats.avg_confidence:.3f}")

        return processed_bookmarks

    def organize_bookmarks(self, processed_bookmarks: List[Dict]) -> Dict:
        """组织书签为层次结构"""
        organized = {}

        # 获取分类顺序
        category_order = self.classifier.config.get("category_order", [])

        for bookmark in processed_bookmarks:
            category = bookmark["category"]

            # 处理嵌套分类（限制最多两级）
            if "/" in category:
                raw_parts = [p.strip() for p in category.split("/") if p.strip()]
                if len(raw_parts) > 2:
                    parts = [raw_parts[0], "/".join(raw_parts[1:])]
                else:
                    parts = raw_parts
                current = organized

                for i, part in enumerate(parts):
                    if part not in current:
                        current[part] = {} if i < len(parts) - 1 else {"_items": []}
                    if i == len(parts) - 1:
                        if "_items" not in current[part]:
                            current[part]["_items"] = []
                        current[part]["_items"].append(bookmark)
                    else:
                        current = current[part]
            else:
                if category not in organized:
                    organized[category] = {"_items": []}
                organized[category]["_items"].append(bookmark)

        # 排序书签（按置信度降序）
        def sort_items(node):
            if isinstance(node, dict):
                if "_items" in node:
                    node["_items"].sort(key=lambda x: x["confidence"], reverse=True)
                for key, value in node.items():
                    if key != "_items":
                        sort_items(value)

        sort_items(organized)

        return organized

    def generate_html_output(self, organized_bookmarks: Dict, output_file: str):
        """生成增强版HTML输出"""
        self.logger.info(f"生成HTML输出: {output_file}")

        lines = [
            "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
            '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
            "<TITLE>Enhanced Bookmark Classification</TITLE>",
            "<H1>🚀 智能书签分类系统</H1>",
            f"<P>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</P>",
            f"<P>总计: {self.stats.processed_bookmarks} 个书签, 平均置信度: {self.stats.avg_confidence:.3f}</P>",
            "<DL><p>",
        ]

        def write_category(name: str, data: Dict, indent: int = 1):
            ind = "    " * indent
            timestamp = str(int(time.time()))

            lines.append(
                f'{ind}<DT><H3 ADD_DATE="{timestamp}">{html.escape(name)}</H3>'
            )
            lines.append(f"{ind}<DL><p>")

            # 子分类
            subcats = sorted([k for k in data.keys() if k != "_items"])
            for subcat in subcats:
                write_category(subcat, data[subcat], indent + 1)

            # 书签项目
            if "_items" in data:
                show_conf = self.classifier.config.get(
                    "show_confidence_indicator", False
                )
                for item in data["_items"]:
                    confidence = item["confidence"]
                    # 清理已有 emoji 前缀（统一模块）
                    clean_title = clean_emoji_title(item["title"])

                    # 置信度指示器
                    if show_conf:
                        if confidence >= 0.9:
                            indicator = "🔥"
                        elif confidence >= 0.7:
                            indicator = "📌"
                        elif confidence >= 0.5:
                            indicator = "⭐"
                        else:
                            indicator = "❓"
                        title_final = f"{indicator} {html.escape(clean_title)}"
                    else:
                        title_final = html.escape(clean_title)

                    url_escaped = html.escape(item["url"], quote=True)
                    lines.append(
                        f'{ind}    <DT><A HREF="{url_escaped}" ADD_DATE="{timestamp}">{title_final}</A>'
                    )

            lines.append(f"{ind}</DL><p>")

        # 按配置的顺序处理分类
        category_order = self.classifier.config.get("category_order", [])

        for category in category_order:
            if category in organized_bookmarks:
                write_category(category, organized_bookmarks[category])

        # 处理其他分类
        for category in sorted(organized_bookmarks.keys()):
            if category not in category_order:
                write_category(category, organized_bookmarks[category])

        lines.append("</DL><p>")

        # 写入文件
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.logger.info(f"HTML文件已保存: {output_file}")

    def generate_markdown_output(self, organized_bookmarks: Dict, output_file: str):
        """生成增强版Markdown输出"""
        self.logger.info(f"生成Markdown输出: {output_file}")

        lines = [
            "# 🚀 智能书签分类报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**处理统计**: {self.stats.processed_bookmarks} 个书签, 平均置信度: {self.stats.avg_confidence:.3f}  ",
            f"**处理速度**: {self.stats.processing_speed:.2f} 书签/秒  ",
            f"**去除重复**: {self.stats.duplicates_removed} 个",
            "",
            "## 📊 分类统计",
            "",
        ]

        # 分类统计
        for category, count in sorted(
            self.stats.categories_found.items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"- **{category}**: {count} 个")

        lines.extend(["", "---", ""])

        def write_category(name: str, data: Dict, level: int = 2):
            prefix = "#" * min(level, 6)
            lines.append(f"{prefix} {name}")
            lines.append("")

            # 子分类
            subcats = sorted([k for k in data.keys() if k != "_items"])
            for subcat in subcats:
                write_category(subcat, data[subcat], level + 1)

            # 书签项目
            if "_items" in data:
                show_conf = self.classifier.config.get(
                    "show_confidence_indicator", False
                )
                for item in data["_items"]:
                    confidence = item["confidence"]
                    # 清理标题中的 emoji 前缀（统一模块）
                    clean_title = clean_emoji_title(item["title"])

                    # 置信度指示器（受配置开关控制）
                    if show_conf:
                        if confidence >= 0.9:
                            indicator = "🔥"
                        elif confidence >= 0.7:
                            indicator = "📌"
                        elif confidence >= 0.5:
                            indicator = "⭐"
                        else:
                            indicator = "❓"
                        prefix_emoji = f"{indicator} "
                    else:
                        prefix_emoji = ""

                    lines.append(
                        f"- {prefix_emoji}[{clean_title}]({item['url']}) *({confidence:.3f})*"
                    )

                lines.append("")

        # 按顺序处理分类
        category_order = self.classifier.config.get("category_order", [])

        for category in category_order:
            if category in organized_bookmarks:
                write_category(category, organized_bookmarks[category])

        for category in sorted(organized_bookmarks.keys()):
            if category not in category_order:
                write_category(category, organized_bookmarks[category])

        # 添加详细统计
        lines.extend(
            [
                "## 📈 处理详情",
                "",
                f"- **总书签数**: {self.stats.total_bookmarks}",
                f"- **成功处理**: {self.stats.processed_bookmarks}",
                f"- **重复移除**: {self.stats.duplicates_removed}",
                f"- **处理错误**: {self.stats.errors_count}",
                f"- **处理时间**: {(self.stats.end_time - self.stats.start_time).total_seconds():.2f} 秒",
                f"- **缓存命中**: {self.classifier.get_stats().get('cache_hits', 0)}",
                "",
            ]
        )

        # 写入文件
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.logger.info(f"Markdown文件已保存: {output_file}")

    def generate_json_report(self, organized_bookmarks: Dict, output_file: str):
        """生成JSON格式的详细报告"""
        self.logger.info(f"生成JSON报告: {output_file}")

        report = {
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "processor_version": __version__,
                "config_file": self.config_file,
            },
            "statistics": {
                "total_bookmarks": self.stats.total_bookmarks,
                "processed_bookmarks": self.stats.processed_bookmarks,
                "duplicates_removed": self.stats.duplicates_removed,
                "errors_count": self.stats.errors_count,
                "processing_time_seconds": (
                    self.stats.end_time - self.stats.start_time
                ).total_seconds(),
                "processing_speed": self.stats.processing_speed,
                "average_confidence": self.stats.avg_confidence,
                "category_distribution": dict(self.stats.categories_found),
            },
            "classifier_stats": self.classifier.get_stats(),
            "bookmarks": organized_bookmarks,
            "low_confidence_items": [
                {
                    "url": item["url"],
                    "title": item["title"],
                    "category": item["category"],
                    "confidence": item["confidence"],
                    "alternatives": item["alternatives"][:3],
                }
                for item in self.processed_bookmarks
                if item["confidence"] < 0.6
            ],
        }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.info(f"JSON报告已保存: {output_file}")

    def save_learning_data(self):
        """保存学习数据"""
        self.classifier.save_learning_data()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="增强版书签分类处理系统",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-i", "--input", nargs="+", default=[], help="输入的HTML书签文件路径"
    )
    parser.add_argument(
        "-c", "--config", default=None, help="配置文件路径；默认使用内置配置"
    )
    parser.add_argument("-o", "--output-dir", default="output", help="输出目录")
    parser.add_argument(
        "--html-output", default="bookmarks_enhanced.html", help="HTML输出文件名"
    )
    parser.add_argument(
        "--md-output", default="bookmarks_enhanced.md", help="Markdown输出文件名"
    )
    parser.add_argument(
        "--json-output", default="bookmarks_report.json", help="JSON报告文件名"
    )
    parser.add_argument("--workers", type=int, default=4, help="并行处理线程数")
    parser.add_argument("--no-progress", action="store_true", help="不显示处理进度")
    parser.add_argument("--save-learning", action="store_true", help="保存学习数据")

    args = parser.parse_args()

    # 获取输入文件
    input_files = args.input if args.input else glob.glob("examples/*.html")

    if not input_files:
        if os.path.exists("bookmarks_2025_7_1.html"):
            input_files = ["bookmarks_2025_7_1.html"]
        else:
            print("❌ 错误: 未找到输入文件")
            print("请将书签文件放在 examples/ 目录下，或使用 -i 参数指定文件")
            return

    print(f"🚀 开始处理书签文件: {input_files}")
    print(f"📊 使用配置文件: {args.config}")
    print(f"⚡ 并行线程数: {args.workers}")

    # 初始化处理器
    processor = EnhancedBookmarkProcessor(args.config, args.workers)

    try:
        # 处理书签
        processed_bookmarks = processor.process_bookmarks(
            input_files, show_progress=not args.no_progress
        )

        if not processed_bookmarks:
            print("❌ 没有成功处理任何书签")
            return

        # 组织书签
        organized_bookmarks = processor.organize_bookmarks(processed_bookmarks)

        # 生成输出
        os.makedirs(args.output_dir, exist_ok=True)

        html_path = os.path.join(args.output_dir, args.html_output)
        md_path = os.path.join(args.output_dir, args.md_output)
        json_path = os.path.join(args.output_dir, args.json_output)

        processor.generate_html_output(organized_bookmarks, html_path)
        processor.generate_markdown_output(organized_bookmarks, md_path)
        processor.generate_json_report(organized_bookmarks, json_path)

        # 保存学习数据
        if args.save_learning:
            processor.save_learning_data()

        # 显示最终统计
        stats = processor.stats
        print(f"\n✅ 处理完成!")
        print(f"📈 总计: {stats.total_bookmarks} 个书签")
        print(f"✨ 成功处理: {stats.processed_bookmarks} 个")
        print(f"🔄 去除重复: {stats.duplicates_removed} 个")
        print(f"❌ 处理错误: {stats.errors_count} 个")
        print(f"⚡ 处理速度: {stats.processing_speed:.2f} 书签/秒")
        print(f"🎯 平均置信度: {stats.avg_confidence:.3f}")
        print(f"💾 输出保存至: {args.output_dir}")

        # 显示分类统计
        print(f"\n📊 分类分布:")
        for category, count in sorted(
            stats.categories_found.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"  - {category}: {count} 个")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断处理")
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
        logging.exception("处理错误详情:")


if __name__ == "__main__":
    main()
