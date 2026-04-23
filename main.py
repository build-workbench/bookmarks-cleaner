"""
AI Bookmark Classifier - Main Entry Point
AI智能书签分类器 - 主入口

这是新一代基于AI的智能书签分类系统的主入口文件。
"""

import argparse
import glob
import logging
import os
import sys
from pathlib import Path

from src import __version__
from src.bookmark_processor import BookmarkProcessor
from src.cli_interface import CLIInterface
from src.resource_loader import ResourceResolutionError, resolve_config_path


def setup_logging(log_level: str = "INFO", use_file: bool = False):
    """设置日志"""
    handlers = [logging.StreamHandler()]
    if use_file:
        os.makedirs("logs", exist_ok=True)
        handlers.insert(
            0, logging.FileHandler("logs/ai_classifier.log", encoding="utf-8")
        )

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI智能书签分类系统 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --interactive                          # 启动交互模式
  %(prog)s -i bookmarks.html                     # 处理单个文件
  %(prog)s -i examples/demo_bookmarks.html --train   # 处理示例书签并训练模型
  %(prog)s --health-check                        # 运行健康检查
        """,
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-i", "--input", nargs="+", help="输入的HTML书签文件")
    parser.add_argument("-o", "--output", default="output", help="输出目录")
    parser.add_argument(
        "-c", "--config", default=None, help="配置文件路径；默认使用内置配置"
    )

    parser.add_argument("--interactive", action="store_true", help="启动交互模式")
    parser.add_argument("--train", action="store_true", help="训练机器学习模型")
    parser.add_argument("--health-check", action="store_true", help="运行健康检查")

    parser.add_argument("--workers", type=int, default=4, help="并行处理线程数")
    parser.add_argument("--threshold", type=float, default=0.7, help="分类置信度阈值")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"]
    )
    parser.add_argument("--no-ml", action="store_true", help="禁用机器学习功能")
    parser.add_argument(
        "--limit", type=int, default=0, help="限制处理的书签数量（调试用）"
    )

    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        config_path, _ = resolve_config_path(args.config)
        use_file_logging = bool(args.input or args.interactive)
        setup_logging(args.log_level, use_file=use_file_logging)
        logger = logging.getLogger(__name__)

        if args.interactive:
            cli = CLIInterface(config_path=str(config_path))
            cli.run()
            return

        if args.health_check:
            from src.health_checker import run_health_check

            ok = run_health_check(str(config_path))
            if not ok:
                sys.exit(1)
            return

        if args.input:
            input_files = []
            for pattern in args.input:
                if ("*" in pattern or "?" in pattern) and (
                    pattern.startswith('"') and pattern.endswith('"')
                ):
                    pattern = pattern.strip('"')

                if "*" in pattern or "?" in pattern:
                    p = Path(pattern)
                    directory = p.parent
                    glob_pattern = p.name

                    if directory.is_dir():
                        expanded = [str(f) for f in directory.glob(glob_pattern)]
                        if expanded:
                            input_files.extend(expanded)
                        else:
                            logger.warning(
                                f"在目录 '{directory}' 中没有找到匹配 '{glob_pattern}' 的文件"
                            )
                    else:
                        expanded_fallback = glob.glob(pattern)
                        if expanded_fallback:
                            input_files.extend(expanded_fallback)
                        else:
                            logger.warning(f"没有找到匹配模式的文件: {pattern}")
                else:
                    if Path(pattern).is_file():
                        input_files.append(pattern)
                    else:
                        logger.warning(f"文件不存在或不是一个有效文件: {pattern}")

            if not input_files:
                logger.error("没有找到有效的输入文件")
                return

            logger.info(f"将处理 {len(input_files)} 个文件: {input_files}")

            processor = BookmarkProcessor(
                config_path=str(config_path),
                max_workers=args.workers,
                use_ml=not args.no_ml,
                confidence_threshold=args.threshold,
            )

            results = processor.process_files(
                input_files=input_files,
                output_dir=args.output,
                train_models=args.train,
                limit=args.limit if args.limit and args.limit > 0 else 0,
            )

            logger.info(f"处理完成: {results['processed_bookmarks']} 个书签已分类")
            return

        parser.print_help()

    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(1)
    except (FileNotFoundError, ValueError, ResourceResolutionError) as e:
        logging.getLogger(__name__).error(f"配置或资源错误: {e}")
        if args.log_level == "DEBUG":
            raise
        sys.exit(2)
    except ImportError as e:
        logging.getLogger(__name__).error(f"依赖缺失: {e}")
        if args.log_level == "DEBUG":
            raise
        sys.exit(3)
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        if args.log_level == "DEBUG":
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
