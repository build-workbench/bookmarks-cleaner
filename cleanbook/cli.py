"""CleanBook CLI 入口"""

from __future__ import annotations

import argparse
import glob
import logging
import sys
from pathlib import Path

from cleanbook import __version__
from cleanbook.config import ResourceResolutionError, resolve_config_path
from cleanbook.processor import BookmarkProcessor


def setup_logging(log_level: str = "INFO", use_file: bool = False):
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if use_file:
        import os
        os.makedirs("logs", exist_ok=True)
        handlers.insert(0, logging.FileHandler("logs/cleanbook.log", encoding="utf-8"))
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description=f"CleanBook v{__version__} - 书签清理与分类",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i bookmarks.html -o output/
  %(prog)s -i examples/demo_bookmarks.html --no-ml
  %(prog)s --health-check
        """,
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-i", "--input", nargs="+", help="输入的HTML书签文件")
    parser.add_argument("-o", "--output", default="output", help="输出目录")
    parser.add_argument("-c", "--config", default=None, help="配置文件路径")
    parser.add_argument("--health-check", action="store_true", help="运行健康检查")
    parser.add_argument("--train", action="store_true", help="训练机器学习模型")
    parser.add_argument("--workers", type=int, default=4, help="并行处理线程数")
    parser.add_argument("--threshold", type=float, default=0.7, help="分类置信度阈值")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--no-ml", action="store_true", help="禁用机器学习")
    parser.add_argument("--limit", type=int, default=0, help="限制处理的书签数量（调试用）")

    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        config_path, _ = resolve_config_path(args.config)
        use_file_logging = bool(args.input)
        setup_logging(args.log_level, use_file=use_file_logging)
        logger = logging.getLogger(__name__)

        if args.health_check:
            from cleanbook.health import run_health_check
            ok = run_health_check(str(config_path))
            sys.exit(0 if ok else 1)

        if args.input:
            input_files = []
            for pattern in args.input:
                if "*" in pattern or "?" in pattern:
                    expanded = glob.glob(pattern)
                    if expanded:
                        input_files.extend(expanded)
                    else:
                        logger.warning(f"没有找到匹配模式的文件: {pattern}")
                else:
                    if Path(pattern).is_file():
                        input_files.append(pattern)
                    else:
                        logger.warning(f"文件不存在: {pattern}")

            if not input_files:
                logger.error("没有找到有效的输入文件")
                sys.exit(1)

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
