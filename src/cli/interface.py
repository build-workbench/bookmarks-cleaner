"""
CLI Interface - 交互式命令行界面

提供现代化的交互式用户界面
"""

import json
import logging
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich import print as rprint
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.tree import Tree

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("警告: rich库未安装，将使用基础CLI界面")

from ..classifiers.ai import AIBookmarkClassifier
from ..bookmark_processor import BookmarkProcessor
from ..utils.resource_loader import resolve_config_path


class CLIInterface:
    """CLI交互界面"""

    def __init__(self, config_path: str | None = None):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.console = Console() if RICH_AVAILABLE else None
        self.processor = None
        self.classifier = None
        self.logger = logging.getLogger(__name__)

    def run(self):
        """运行交互界面"""
        self._print_welcome()

        try:
            while True:
                choice = self._show_main_menu()

                if choice == "q":
                    break
                elif choice == "1":
                    self._process_bookmarks()
                elif choice == "2":
                    self._view_results()
                elif choice == "3":
                    self._manage_models()
                elif choice == "4":
                    self._health_check()
                elif choice == "5":
                    self._show_statistics()
                elif choice == "6":
                    self._settings()
                elif choice == "h":
                    self._show_help()

                if choice != "q":
                    self._pause()

        except KeyboardInterrupt:
            self._info("程序被用户中断")
        except (ValueError, TypeError, IOError) as e:
            self._error(f"程序执行出错: {e}")
        finally:
            self._info("感谢使用AI智能书签分类系统!")

    def _print_welcome(self):
        """打印欢迎信息"""
        welcome_text = """
🚀 AI智能书签分类系统 v2.0

基于人工智能的下一代书签管理工具
- 🧠 AI智能分类算法
- ⚡ 高性能并行处理
- 🎯 个性化推荐系统
- 🔍 智能去重检测
- 📊 详细统计分析
        """

        if RICH_AVAILABLE:
            panel = Panel(welcome_text.strip(), border_style="blue", title="欢迎")
            self.console.print(panel)
        else:
            print("=" * 50)
            print(welcome_text.strip())
            print("=" * 50)

    def _show_main_menu(self) -> str:
        """显示主菜单"""
        options = {
            "1": "📂 处理书签文件",
            "2": "📊 查看处理结果",
            "3": "🤖 模型管理",
            "4": "🏥 健康检查",
            "5": "📈 统计分析",
            "6": "⚙️ 设置",
            "h": "❓ 帮助",
            "q": "🚪 退出",
        }

        if RICH_AVAILABLE:
            self.console.print("\n[bold cyan]主菜单[/bold cyan]")
            for key, desc in options.items():
                self.console.print(f"  [green]{key}[/green]: {desc}")

            return Prompt.ask(
                "请选择操作", choices=list(options.keys()), show_choices=False
            )
        else:
            print("\n主菜单:")
            for key, desc in options.items():
                print(f"  {key}: {desc}")

            while True:
                choice = input("请选择操作: ").strip().lower()
                if choice in options:
                    return choice
                print("无效选择，请重试")

    def _process_bookmarks(self):
        """处理书签文件"""
        self._info("书签处理")

        # 选择输入文件
        input_files = self._select_input_files()
        if not input_files:
            self._warning("没有选择输入文件")
            return

        # 选择输出目录
        output_dir = self._get_output_directory()

        # 处理选项
        use_ml = self._confirm("是否启用机器学习分类?", default=True)
        train_models = (
            self._confirm("是否训练模型?", default=False) if use_ml else False
        )
        workers = self._get_worker_count()

        # 初始化处理器
        self.processor = BookmarkProcessor(
            config_path=self.config_path, max_workers=workers, use_ml=use_ml
        )

        # 开始处理
        self._info(f"开始处理 {len(input_files)} 个文件...")

        try:
            if RICH_AVAILABLE:
                with Progress(
                    TextColumn("[bold blue]处理"),
                    BarColumn(bar_width=None),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    TimeRemainingColumn(),
                    console=self.console,
                ) as progress:
                    task = progress.add_task("处理中...", total=1)
                    stats = self.processor.process_files(
                        input_files=input_files,
                        output_dir=output_dir,
                        train_models=train_models,
                    )
                    progress.update(task, advance=1)
            else:
                stats = self.processor.process_files(
                    input_files=input_files,
                    output_dir=output_dir,
                    train_models=train_models,
                )

            self._show_processing_results(stats)

        except (ValueError, IOError, AttributeError) as e:
            self._error(f"处理失败: {e}")

    def _select_input_files(self) -> List[str]:
        """选择输入文件"""
        default_path = "examples"
        if RICH_AVAILABLE:
            raw = Prompt.ask(
                "输入HTML书签文件/目录（可用逗号分隔多个文件）", default=default_path
            )
        else:
            raw = (
                input(f"输入HTML书签文件/目录（默认: {default_path}）: ").strip()
                or default_path
            )

        raw = (raw or "").strip()
        if not raw:
            return []

        candidates: List[str] = []

        if "," in raw and not os.path.exists(raw):
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            candidates.extend(parts)
        else:
            candidates.append(raw)

        files: List[str] = []
        allowed_exts = (".html", ".htm")
        for p in candidates:
            p = os.path.expanduser(p)
            if os.path.isfile(p):
                if p.lower().endswith(allowed_exts):
                    files.append(p)
                else:
                    self._warning(f"跳过非HTML文件: {p}")
                continue

            if os.path.isdir(p):
                html_files = sorted(
                    [f for f in os.listdir(p) if f.lower().endswith(allowed_exts)]
                )
                if not html_files:
                    self._warning(f"目录中没有找到HTML文件: {p}")
                    continue
                self._info(f"在目录 {p} 找到 {len(html_files)} 个HTML文件")
                for fname in html_files:
                    full = os.path.join(p, fname)
                    if self._confirm(f"处理文件 {fname}?", default=True):
                        files.append(full)
                continue

            self._warning(f"路径不存在: {p}")

        deduped: List[str] = []
        seen = set()
        for fp in files:
            if fp in seen:
                continue
            seen.add(fp)
            deduped.append(fp)

        return deduped

    def _get_output_directory(self) -> str:
        """获取输出目录"""
        if RICH_AVAILABLE:
            return Prompt.ask("输出目录", default="output")
        else:
            output = input("输出目录 (默认: output): ").strip()
            return output if output else "output"

    def _get_worker_count(self) -> int:
        """获取工作线程数"""
        if RICH_AVAILABLE:
            return int(Prompt.ask("并行线程数", default="4"))
        else:
            while True:
                try:
                    count = input("并行线程数 (默认: 4): ").strip()
                    return int(count) if count else 4
                except ValueError:
                    print("请输入有效数字")

    def _show_processing_results(self, stats: Dict):
        """显示处理结果"""
        total = stats.get("total_bookmarks", 0)
        processed = stats.get("processed_bookmarks", 0)
        duplicates = stats.get("duplicates_removed", 0)
        errors = stats.get("errors", 0)
        processing_time = stats.get("processing_time", 0.0) or 0.0
        speed = stats.get("processing_speed_bps")
        if speed is None:
            speed = stats.get("processing_speed")
        if speed is None:
            speed = (processed / processing_time) if processing_time else 0.0

        if RICH_AVAILABLE:
            table = Table(title="处理结果统计", border_style="green")
            table.add_column("指标", style="cyan")
            table.add_column("值", style="yellow")

            metrics = [
                ("总书签数", total),
                ("成功处理", processed),
                ("去除重复", duplicates),
                ("处理错误", errors),
                ("处理时间", f"{processing_time:.2f}秒"),
                ("处理速度", f"{float(speed):.1f} 书签/秒"),
            ]

            for metric, value in metrics:
                table.add_row(metric, str(value))

            self.console.print(table)
        else:
            print("\n处理结果统计:")
            print(f"  总书签数: {total}")
            print(f"  成功处理: {processed}")
            print(f"  去除重复: {duplicates}")
            print(f"  处理错误: {errors}")
            print(f"  处理时间: {processing_time:.2f}秒")
            print(f"  处理速度: {float(speed):.1f} 书签/秒")

    def _view_results(self):
        """查看处理结果"""
        self._info("查看处理结果")

        output_dir = "output"
        if not os.path.exists(output_dir):
            self._warning("没有找到输出目录")
            return

        files = [
            f for f in os.listdir(output_dir) if f.endswith((".html", ".json", ".md"))
        ]
        if not files:
            self._warning("没有找到结果文件")
            return

        # 显示文件列表
        self._info("可用的结果文件:")
        for i, file in enumerate(files, 1):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            print(f"  {i}. {file} ({size} 字节)")

        # 选择文件查看
        try:
            if RICH_AVAILABLE:
                choice = int(Prompt.ask(f"选择文件 (1-{len(files)})", default="1"))
            else:
                choice = int(input(f"选择文件 (1-{len(files)}): ") or "1")

            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]
                self._view_file_content(os.path.join(output_dir, selected_file))
        except ValueError:
            self._error("无效的选择")

    def _view_file_content(self, file_path: str):
        """查看文件内容"""
        try:
            if file_path.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "statistics" in data:
                    self._show_json_statistics(data["statistics"])
                else:
                    print("JSON内容预览:")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000] + "...")

            elif file_path.endswith(".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print("Markdown内容预览:")
                print(content[:1000] + "..." if len(content) > 1000 else content)

            else:
                self._info(f"文件路径: {file_path}")
                self._info(f"文件大小: {os.path.getsize(file_path)} 字节")

        except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
            self._error(f"读取文件失败: {e}")

    def _show_json_statistics(self, stats: Dict):
        """显示JSON统计信息"""
        if RICH_AVAILABLE:
            table = Table(title="统计信息", border_style="blue")
            table.add_column("指标", style="cyan")
            table.add_column("值", style="yellow")

            for key, value in stats.items():
                if isinstance(value, dict):
                    value = json.dumps(value, ensure_ascii=False)
                table.add_row(key.replace("_", " ").title(), str(value))

            self.console.print(table)
        else:
            print("统计信息:")
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

    def _manage_models(self):
        """管理AI模型"""
        self._info("AI模型管理")

        model_options = {
            "1": "📊 查看模型状态",
            "2": "💾 保存当前模型",
            "3": "📂 加载已保存模型",
            "4": "🎯 重新训练模型",
            "5": "🧹 清理模型缓存",
        }

        choice = self._show_menu(model_options, "模型管理菜单")

        if choice == "1":
            self._show_model_status()
        elif choice == "2":
            self._save_model()
        elif choice == "3":
            self._load_model()
        elif choice == "4":
            self._retrain_model()
        elif choice == "5":
            self._clear_model_cache()

    def _health_check(self):
        """健康检查"""
        self._info("书签健康检查")
        self._warning("此功能需要网络连接，可能需要较长时间")

        if not self._confirm("继续进行健康检查?"):
            return

        source_options = {
            "1": "从HTML书签文件读取",
            "2": "从输出JSON报告读取",
            "q": "取消",
        }
        choice = self._show_menu(source_options, "选择健康检查数据来源")
        if choice == "q":
            return

        processor = self._get_processor()

        bookmarks: List[Dict] = []
        if choice == "1":
            input_files = self._select_input_files()
            if not input_files:
                self._warning("没有选择输入文件")
                return
            for fp in input_files:
                try:
                    bookmarks.extend(processor._load_bookmarks_from_file(fp))
                except (FileNotFoundError, IOError, ValueError) as e:
                    self._warning(f"读取失败 {fp}: {e}")

        elif choice == "2":
            report_path = self._select_output_json_report()
            if not report_path:
                return
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                organized = data.get("bookmarks") if isinstance(data, dict) else None
                bookmarks = self._flatten_organized_bookmarks(organized)
            except (json.JSONDecodeError, IOError, KeyError) as e:
                self._error(f"读取JSON报告失败: {e}")
                return

        if not bookmarks:
            self._warning("没有可检查的书签")
            return

        self._info(f"开始检查 {len(bookmarks)} 个链接...")
        try:
            results = processor.health_checker.check_bookmarks(bookmarks)
            summary = processor.health_checker.get_summary(results)
            self._show_health_summary(summary)
        except (IOError, AttributeError, ConnectionError) as e:
            self._error(f"健康检查失败: {e}")

    def _show_statistics(self):
        """显示统计信息"""
        self._info("系统统计信息")

        if self.processor:
            stats = self.processor.get_statistics()
            self._show_processing_results(stats)
        else:
            self._warning("尚未处理任何书签文件")

    def _settings(self):
        """设置管理"""
        self._info("系统设置")

        settings_options = {
            "1": "📝 查看当前配置",
            "2": "✏️ 修改配置",
            "3": "🔄 重载配置",
            "4": "💾 导出配置",
        }

        choice = self._show_menu(settings_options, "设置菜单")

        if choice == "1":
            self._show_current_config()
        elif choice == "2":
            self._modify_config()
        elif choice == "3":
            self._reload_config()
        elif choice == "4":
            self._export_config()

    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🚀 AI智能书签分类系统帮助

主要功能:
📂 处理书签文件 - 批量处理浏览器导出的书签
📊 查看处理结果 - 查看分类结果和统计报告
🤖 模型管理 - 管理AI分类模型
🏥 健康检查 - 检查书签链接有效性
📈 统计分析 - 查看详细处理统计
⚙️ 设置 - 管理系统配置

使用流程:
1. 选择浏览器导出的HTML书签文件或包含HTML文件的目录（可用逗号分隔多个路径，支持 .html/.htm）
2. 选择"处理书签文件"开始智能分类
3. 查看生成的HTML、JSON、Markdown结果文件
4. 根据需要调整配置和重新训练模型

更多信息请查看项目文档。
        """

        if RICH_AVAILABLE:
            panel = Panel(help_text.strip(), title="帮助信息", border_style="green")
            self.console.print(panel)
        else:
            print(help_text)

    # 辅助方法
    def _show_menu(self, options: Dict[str, str], title: str) -> str:
        """显示菜单并获取选择"""
        if RICH_AVAILABLE:
            self.console.print(f"\n[bold magenta]{title}[/bold magenta]")
            for key, desc in options.items():
                self.console.print(f"  [green]{key}[/green]: {desc}")

            return Prompt.ask(
                "请选择", choices=list(options.keys()), show_choices=False
            )
        else:
            print(f"\n{title}:")
            for key, desc in options.items():
                print(f"  {key}: {desc}")

            while True:
                choice = input("请选择: ").strip()
                if choice in options:
                    return choice
                print("无效选择，请重试")

    def _confirm(self, question: str, default: bool = True) -> bool:
        """确认对话"""
        if RICH_AVAILABLE:
            return Confirm.ask(question, default=default)
        else:
            default_text = "Y/n" if default else "y/N"
            response = input(f"{question} [{default_text}]: ").strip().lower()

            if not response:
                return default

            return response in ["y", "yes", "是", "true", "1"]

    def _info(self, message: str):
        """信息消息"""
        if RICH_AVAILABLE:
            self.console.print(f"ℹ️  [blue]{message}[/blue]")
        else:
            print(f"ℹ️  {message}")

    def _warning(self, message: str):
        """警告消息"""
        if RICH_AVAILABLE:
            self.console.print(f"⚠️  [yellow]{message}[/yellow]")
        else:
            print(f"⚠️  {message}")

    def _error(self, message: str):
        """错误消息"""
        if RICH_AVAILABLE:
            self.console.print(f"❌ [red]{message}[/red]")
        else:
            print(f"❌ {message}")

    def _success(self, message: str):
        """成功消息"""
        if RICH_AVAILABLE:
            self.console.print(f"✅ [green]{message}[/green]")
        else:
            print(f"✅ {message}")

    def _pause(self):
        """暂停等待用户输入"""
        input("\n按Enter继续...")

    # 占位符方法 - 待实现
    def _show_model_status(self):
        classifier = self._get_classifier()
        stats = classifier.get_statistics()
        ml = classifier.ml_classifier
        ml_enabled = ml is not None
        ml_trained = bool(getattr(ml, "is_trained", False)) if ml_enabled else False
        ml_stats = ml.get_stats() if ml_enabled else {}

        if RICH_AVAILABLE:
            table = Table(title="模型状态", border_style="blue")
            table.add_column("项目", style="cyan")
            table.add_column("值", style="yellow")
            table.add_row("ML已启用", str(ml_enabled))
            table.add_row("ML已训练", str(ml_trained))
            table.add_row("缓存命中", str(stats.get("cache_hits", 0)))
            table.add_row("缓存命中率", f"{stats.get('cache_hit_rate', 0) * 100:.1f}%")
            table.add_row("平均置信度", f"{stats.get('average_confidence', 0):.3f}")
            methods = stats.get("classification_methods", {})
            if isinstance(methods, dict):
                table.add_row("规则引擎", str(methods.get("rule_engine", 0)))
                table.add_row("ML分类", str(methods.get("ml_classifier", 0)))
                table.add_row("语义分析", str(methods.get("semantic_analyzer", 0)))
                table.add_row("用户画像", str(methods.get("user_profiler", 0)))
                table.add_row("LLM", str(methods.get("llm", 0)))
                table.add_row("未分类", str(methods.get("unclassified (fallback)", 0)))
            self.console.print(table)
            if ml_stats:
                self.console.print(
                    Panel(
                        json.dumps(ml_stats, ensure_ascii=False, indent=2)[:2000],
                        title="ML统计",
                        border_style="green",
                    )
                )
        else:
            print("\n模型状态:")
            print(f"  ML已启用: {ml_enabled}")
            print(f"  ML已训练: {ml_trained}")
            print(f"  缓存命中: {stats.get('cache_hits', 0)}")
            print(f"  缓存命中率: {stats.get('cache_hit_rate', 0) * 100:.1f}%")
            print(f"  平均置信度: {stats.get('average_confidence', 0):.3f}")
            if ml_stats:
                print("  ML统计:")
                print(json.dumps(ml_stats, ensure_ascii=False, indent=2)[:2000])

    def _save_model(self):
        classifier = self._get_classifier()
        default_path = "models/ai_classifier.json"
        if RICH_AVAILABLE:
            path = Prompt.ask("保存模型到", default=default_path)
        else:
            path = input(f"保存模型到 (默认: {default_path}): ").strip() or default_path
        try:
            classifier.save_model(path)
            self._success(f"模型已保存到: {path}")
        except (IOError, pickle.PickleError, AttributeError) as e:
            self._error(f"模型保存失败: {e}")

    def _load_model(self):
        classifier = self._get_classifier()
        default_path = "models/ai_classifier.json"
        if RICH_AVAILABLE:
            path = Prompt.ask("从路径加载模型", default=default_path)
        else:
            path = (
                input(f"从路径加载模型 (默认: {default_path}): ").strip()
                or default_path
            )
        try:
            classifier.load_model(path)
            self._success(f"模型已加载: {path}")
        except (FileNotFoundError, pickle.PickleError, json.JSONDecodeError) as e:
            self._error(f"模型加载失败: {e}")

    def _retrain_model(self):
        classifier = self._get_classifier()
        ml = classifier.ml_classifier
        if not ml:
            self._warning("机器学习组件未启用")
            return

        report_path = self._select_output_json_report()
        if not report_path:
            return

        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self._error(f"读取JSON报告失败: {e}")
            return

        organized = data.get("bookmarks") if isinstance(data, dict) else None
        bookmarks = self._flatten_organized_bookmarks(organized)
        if not bookmarks:
            self._warning("报告中没有找到书签数据")
            return

        reset = self._confirm("是否清空当前训练缓存并从零开始训练?", default=True)
        if reset and hasattr(ml, "ml_classifier"):
            try:
                ml.ml_classifier.training_data.clear()
                ml.ml_classifier.training_labels.clear()
            except (AttributeError, TypeError) as e:
                self.logger.debug(f"清空训练缓存失败: {e}")

        if RICH_AVAILABLE:
            min_conf = float(Prompt.ask("训练最小置信度", default="0.8"))
        else:
            min_conf = float(input("训练最小置信度 (默认: 0.8): ").strip() or "0.8")

        samples_added = 0
        for bm in bookmarks:
            if not isinstance(bm, dict):
                continue
            url = (bm.get("url") or "").strip()
            title = (bm.get("title") or "").strip()
            category = (bm.get("category") or "").strip()
            if not url or not title or not category or category == "未分类":
                continue

            conf_raw = bm.get("confidence", 0.0)
            try:
                confidence = float(conf_raw) if conf_raw is not None else 0.0
            except (TypeError, ValueError):
                confidence = 0.0

            if confidence < min_conf:
                continue

            features = classifier.extract_features(url, title)
            ml.add_training_sample(features, category)
            samples_added += 1

        self._info(f"已收集训练样本: {samples_added}")
        if samples_added < 10 and not self._confirm(
            "训练数据可能不足，仍然继续训练?", default=False
        ):
            return

        try:
            ok = ml.train_model()
        except (ValueError, RuntimeError, AttributeError) as e:
            self._error(f"训练失败: {e}")
            return

        if ok:
            self._success("模型训练完成并已保存")
        else:
            self._error("模型训练失败")

    def _clear_model_cache(self):
        cleared = []
        if self.processor is not None:
            try:
                self.processor._classification_cache.clear()
                self.processor._url_validation_cache.clear()
                cleared.append("处理器缓存")
            except (AttributeError, TypeError) as e:
                self.logger.debug(f"清理处理器缓存失败: {e}")

        classifier = self.classifier
        if classifier is None and self.processor is not None:
            try:
                classifier = self.processor.classifier
            except (AttributeError, TypeError):
                classifier = None

        if classifier is not None:
            try:
                classifier.feature_cache.clear()
                classifier.classification_cache.clear()
                cleared.append("分类器缓存")
            except (AttributeError, TypeError) as e:
                self.logger.debug(f"清理分类器缓存失败: {e}")

        if cleared:
            self._success(f"已清理: {', '.join(cleared)}")
        else:
            self._warning("没有可清理的缓存")

    def _show_current_config(self):
        config_path = self.config_path

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self._error(f"读取配置失败: {e}")
            return

        display = raw
        try:
            display = self._get_processor().config
        except (AttributeError, TypeError, ValueError):
            display = raw

        ai = display.get("ai_settings", {}) if isinstance(display, dict) else {}
        llm = display.get("llm", {}) if isinstance(display, dict) else {}
        order = display.get("category_order", []) if isinstance(display, dict) else []

        if RICH_AVAILABLE:
            table = Table(title="当前配置（部分）", border_style="magenta")
            table.add_column("键", style="cyan")
            table.add_column("值", style="yellow")
            table.add_row(
                "show_confidence_indicator",
                str(display.get("show_confidence_indicator")),
            )
            table.add_row(
                "ai_settings.confidence_threshold", str(ai.get("confidence_threshold"))
            )
            table.add_row("ai_settings.max_workers", str(ai.get("max_workers")))
            table.add_row(
                "ai_settings.use_semantic_analysis",
                str(ai.get("use_semantic_analysis")),
            )
            table.add_row(
                "ai_settings.use_user_profiling", str(ai.get("use_user_profiling"))
            )
            table.add_row("llm.enable", str(llm.get("enable")))
            table.add_row("llm.provider", str(llm.get("provider")))
            table.add_row("llm.base_url", str(llm.get("base_url")))
            table.add_row("llm.model", str(llm.get("model")))
            if isinstance(order, list) and order:
                table.add_row("category_order", ", ".join([str(x) for x in order]))
            self.console.print(table)
        else:
            print("\n当前配置（部分）:")
            print(
                f"  show_confidence_indicator: {display.get('show_confidence_indicator')}"
            )
            print(
                f"  ai_settings.confidence_threshold: {ai.get('confidence_threshold')}"
            )
            print(f"  ai_settings.max_workers: {ai.get('max_workers')}")
            print(
                f"  ai_settings.use_semantic_analysis: {ai.get('use_semantic_analysis')}"
            )
            print(f"  ai_settings.use_user_profiling: {ai.get('use_user_profiling')}")
            print(f"  llm.enable: {llm.get('enable')}")
            print(f"  llm.provider: {llm.get('provider')}")
            print(f"  llm.base_url: {llm.get('base_url')}")
            print(f"  llm.model: {llm.get('model')}")
            if isinstance(order, list) and order:
                print(f"  category_order: {', '.join([str(x) for x in order])}")

    def _modify_config(self):
        config_path = self.config_path

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self._error(f"读取配置失败: {e}")
            return

        ai = config.setdefault("ai_settings", {})
        llm = config.setdefault("llm", {})

        edit_options = {
            "1": "show_confidence_indicator",
            "2": "ai_settings.confidence_threshold",
            "3": "ai_settings.max_workers",
            "4": "ai_settings.use_semantic_analysis",
            "5": "ai_settings.use_user_profiling",
            "6": "llm.enable",
            "7": "llm.provider",
            "8": "llm.base_url",
            "9": "llm.model",
            "10": "llm.api_key_env",
        }

        choice = self._show_menu(edit_options, "选择要修改的配置项")

        try:
            if choice == "1":
                config["show_confidence_indicator"] = self._confirm(
                    f"show_confidence_indicator (当前: {config.get('show_confidence_indicator')})",
                    default=bool(config.get("show_confidence_indicator", True)),
                )
            elif choice == "2":
                current = ai.get("confidence_threshold", 0.7)
                val = (
                    float(
                        Prompt.ask("confidence_threshold (0-1)", default=str(current))
                    )
                    if RICH_AVAILABLE
                    else float(
                        input(f"confidence_threshold (0-1) (默认: {current}): ")
                        or current
                    )
                )
                ai["confidence_threshold"] = max(0.0, min(1.0, val))
            elif choice == "3":
                current = ai.get("max_workers", 4)
                val = (
                    int(Prompt.ask("max_workers", default=str(current)))
                    if RICH_AVAILABLE
                    else int(input(f"max_workers (默认: {current}): ") or current)
                )
                ai["max_workers"] = max(1, val)
            elif choice == "4":
                ai["use_semantic_analysis"] = self._confirm(
                    f"use_semantic_analysis (当前: {ai.get('use_semantic_analysis')})",
                    default=bool(ai.get("use_semantic_analysis", True)),
                )
            elif choice == "5":
                ai["use_user_profiling"] = self._confirm(
                    f"use_user_profiling (当前: {ai.get('use_user_profiling')})",
                    default=bool(ai.get("use_user_profiling", True)),
                )
            elif choice == "6":
                llm["enable"] = self._confirm(
                    f"llm.enable (当前: {llm.get('enable')})",
                    default=bool(llm.get("enable", False)),
                )
            elif choice == "7":
                current = llm.get("provider", "openai")
                llm["provider"] = (
                    Prompt.ask("llm.provider", default=str(current))
                    if RICH_AVAILABLE
                    else (
                        input(f"llm.provider (默认: {current}): ").strip()
                        or str(current)
                    )
                )
            elif choice == "8":
                current = llm.get("base_url", "https://api.openai.com")
                llm["base_url"] = (
                    Prompt.ask("llm.base_url", default=str(current))
                    if RICH_AVAILABLE
                    else (
                        input(f"llm.base_url (默认: {current}): ").strip()
                        or str(current)
                    )
                )
            elif choice == "9":
                current = llm.get("model", "")
                llm["model"] = (
                    Prompt.ask("llm.model", default=str(current))
                    if RICH_AVAILABLE
                    else (
                        input(f"llm.model (默认: {current}): ").strip() or str(current)
                    )
                )
            elif choice == "10":
                current = llm.get("api_key_env", "OPENAI_API_KEY")
                llm["api_key_env"] = (
                    Prompt.ask("llm.api_key_env", default=str(current))
                    if RICH_AVAILABLE
                    else (
                        input(f"llm.api_key_env (默认: {current}): ").strip()
                        or str(current)
                    )
                )

        except (KeyError, TypeError, ValueError) as e:
            self._error(f"配置修改失败: {e}")
            return

        if not self._confirm("确认写入 config.json?", default=False):
            self._info("已取消写入")
            return

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self._success("配置已更新")
        except (IOError, PermissionError) as e:
            self._error(f"写入配置失败: {e}")

    def _reload_config(self):
        self.processor = None
        self.classifier = None
        self._success("配置已重载（下次操作将重新加载配置）")

    def _export_config(self):
        config_path = self.config_path

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = os.path.join("output", f"config_export_{ts}.json")
        if RICH_AVAILABLE:
            out_path = Prompt.ask("导出到", default=default_path)
        else:
            out_path = input(f"导出到 (默认: {default_path}): ").strip() or default_path

        try:
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            with open(config_path, "r", encoding="utf-8") as rf:
                content = rf.read()
            with open(out_path, "w", encoding="utf-8") as wf:
                wf.write(content)
            self._success(f"配置已导出: {out_path}")
        except (IOError, PermissionError) as e:
            self._error(f"配置导出失败: {e}")

    def _get_processor(self) -> BookmarkProcessor:
        if self.processor is None:
            self.processor = BookmarkProcessor(config_path=self.config_path)
        return self.processor

    def _get_classifier(self) -> AIBookmarkClassifier:
        if self.processor is not None:
            try:
                self.classifier = self.processor.classifier
                return self.classifier
            except (AttributeError, TypeError) as e:
                self.logger.debug(f"获取分类器失败: {e}")
        if self.classifier is None:
            self.classifier = AIBookmarkClassifier(config_path=self.config_path)
        return self.classifier

    def _select_output_json_report(self) -> Optional[str]:
        output_dir = "output"
        if RICH_AVAILABLE:
            output_dir = Prompt.ask("结果目录", default=output_dir)
        else:
            output_dir = input(f"结果目录 (默认: {output_dir}): ").strip() or output_dir

        if not os.path.isdir(output_dir):
            self._warning("没有找到输出目录")
            return None

        files = sorted(
            [f for f in os.listdir(output_dir) if f.lower().endswith(".json")]
        )
        if not files:
            self._warning("没有找到JSON报告")
            return None

        self._info("可用的JSON报告:")
        for i, file in enumerate(files, 1):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            print(f"  {i}. {file} ({size} 字节)")

        try:
            if RICH_AVAILABLE:
                choice = int(Prompt.ask(f"选择文件 (1-{len(files)})", default="1"))
            else:
                choice = int(input(f"选择文件 (1-{len(files)}): ") or "1")
            if 1 <= choice <= len(files):
                return os.path.join(output_dir, files[choice - 1])
        except (ValueError, TypeError):
            self._error("无效的选择")
            return None

        return None

    def _flatten_organized_bookmarks(self, organized) -> List[Dict]:
        items: List[Dict] = []
        if not isinstance(organized, dict):
            return items
        for _, category_data in organized.items():
            if not isinstance(category_data, dict):
                continue
            for item in category_data.get("_items", []) or []:
                if isinstance(item, dict):
                    items.append(item)
            subs = category_data.get("_subcategories", {}) or {}
            if isinstance(subs, dict):
                for _, sub_data in subs.items():
                    if not isinstance(sub_data, dict):
                        continue
                    for item in sub_data.get("_items", []) or []:
                        if isinstance(item, dict):
                            items.append(item)
        return items

    def _show_health_summary(self, summary: Dict):
        if not isinstance(summary, dict):
            self._warning("健康检查摘要格式异常")
            return

        if RICH_AVAILABLE:
            table = Table(title="健康检查摘要", border_style="green")
            table.add_column("指标", style="cyan")
            table.add_column("值", style="yellow")
            table.add_row("总数", str(summary.get("total_count", 0)))
            table.add_row("可访问", str(summary.get("accessible_count", 0)))
            table.add_row("错误", str(summary.get("error_count", 0)))
            table.add_row("警告", str(summary.get("warning_count", 0)))
            table.add_row(
                "平均响应时间(ms)", str(summary.get("average_response_time", 0))
            )
            table.add_row("摘要", str(summary.get("summary", "")))
            self.console.print(table)

            broken = summary.get("broken_bookmarks", [])
            if isinstance(broken, list) and broken:
                self.console.print(
                    Panel(
                        json.dumps(broken, ensure_ascii=False, indent=2)[:2000],
                        title="不可用链接(前N条)",
                        border_style="red",
                    )
                )
            slow = summary.get("slow_bookmarks", [])
            if isinstance(slow, list) and slow:
                self.console.print(
                    Panel(
                        json.dumps(slow, ensure_ascii=False, indent=2)[:2000],
                        title="慢速链接(前N条)",
                        border_style="yellow",
                    )
                )
        else:
            print("\n健康检查摘要:")
            print(f"  总数: {summary.get('total_count', 0)}")
            print(f"  可访问: {summary.get('accessible_count', 0)}")
            print(f"  错误: {summary.get('error_count', 0)}")
            print(f"  警告: {summary.get('warning_count', 0)}")
            print(f"  平均响应时间(ms): {summary.get('average_response_time', 0)}")
            print(f"  摘要: {summary.get('summary', '')}")
