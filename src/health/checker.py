"""
Health Checker - 系统健康检查

检查系统各组件的运行状态和配置有效性。
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

from src.utils.resource_loader import load_json_config, resolve_taxonomy_path, ResourceResolutionError


def run_health_check(config_path: Optional[str] = None):
    """运行系统健康检查（只读）。"""
    logger = logging.getLogger(__name__)

    print("AI智能书签分类系统 - 健康检查")
    print("=" * 50)

    issues: List[str] = []

    python_version = sys.version_info
    if python_version < (3, 10):
        issues.append(f"[ERROR] Python版本过低: {python_version.major}.{python_version.minor}, 需要 >= 3.10")
    else:
        print(f"[OK] Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    required_packages = [
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("rich", "rich"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
    ]

    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"[OK] 依赖包: {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            issues.append(f"[ERROR] 缺少依赖包: {package_name}")

    if missing_packages:
        print("\n安装缺少的依赖包:")
        print(f"pip install {' '.join(missing_packages)}")

    try:
        config, resolved_config, explicit = load_json_config(config_path)
        mode = "显式配置" if explicit else "默认配置"
        print(f"[OK] {mode}: {resolved_config}")

        for section in ["category_rules", "ai_settings"]:
            if section in config:
                print(f"[OK] 配置节: {section}")
            else:
                issues.append(f"[ERROR] 配置文件缺少节: {section}")

        try:
            subjects_path = resolve_taxonomy_path(config, "subjects_file", "taxonomy/subjects.yaml")
            resource_types_path = resolve_taxonomy_path(config, "resource_types_file", "taxonomy/resource_types.yaml")
            print(f"[OK] taxonomy subjects: {subjects_path}")
            print(f"[OK] taxonomy resource_types: {resource_types_path}")
        except FileNotFoundError as exc:
            issues.append(f"[ERROR] taxonomy 资源缺失: {exc}")
    except (FileNotFoundError, ValueError, ResourceResolutionError) as exc:
        issues.append(f"[ERROR] 配置加载失败: {exc}")

    core_modules = [
        "src.ai_classifier",
        "src.bookmark_processor",
        "src.rule_engine",
        "src.cli_interface",
        "src.enhanced_cli",
    ]

    for module in core_modules:
        try:
            __import__(module)
            print(f"[OK] 核心模块: {module}")
        except ImportError as e:
            issues.append(f"[ERROR] 模块导入失败: {module} - {e}")
            logger.debug("Health check import failure", exc_info=e)

    examples_dir = Path("examples")
    if examples_dir.exists():
        html_files = [p for p in examples_dir.iterdir() if p.suffix.lower() in {".html", ".htm"}]
        if html_files:
            print(f"[OK] 示例数据: 找到 {len(html_files)} 个HTML文件")
        else:
            print("[WARN] 示例目录存在，但没有HTML书签文件")
    else:
        print("[WARN] 示例目录不存在: examples")

    print("\n" + "=" * 50)
    if issues:
        print(f"[ERROR] 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   {issue}")
        print("\n请解决以上问题后重新运行系统")
        return False

    print("[OK] 系统健康检查通过!")
    print("系统已准备就绪，可以开始使用")
    return True


if __name__ == "__main__":
    run_health_check()
