"""健康检查 - 验证运行环境"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List, Optional

from cleanbookmarks.config import (
    ResourceResolutionError,
    load_json_config,
    resolve_taxonomy_path,
)

logger = logging.getLogger(__name__)


def run_health_check(config_path: Optional[str] = None) -> bool:
    """运行系统健康检查（只读）"""
    print("CleanBookmarks - 健康检查")
    print("=" * 50)
    issues: List[str] = []

    if sys.version_info < (3, 10):
        issues.append(f"[ERROR] Python版本过低: {sys.version_info.major}.{sys.version_info.minor}, 需要 >= 3.10")
    else:
        print(f"[OK] Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    required_packages = [("beautifulsoup4", "bs4"), ("lxml", "lxml"), ("pyyaml", "yaml"), ("chardet", "chardet")]
    optional_packages = [("requests", "requests")]

    for name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"[OK] 依赖: {name}")
        except ImportError:
            issues.append(f"[ERROR] 缺少依赖: {name}")

    for name, import_name in optional_packages:
        try:
            __import__(import_name)
            print(f"[OK] 可选依赖: {name}")
        except ImportError:
            print(f"[WARN] 可选依赖缺失: {name}")

    try:
        config, resolved, explicit = load_json_config(config_path)
        mode = "显式配置" if explicit else "默认配置"
        print(f"[OK] {mode}: {resolved}")
        for section in ["category_rules", "ai_settings"]:
            if section in config:
                print(f"[OK] 配置节: {section}")
            else:
                issues.append(f"[ERROR] 配置文件缺少节: {section}")
        try:
            subjects_path = resolve_taxonomy_path(config, "subjects_file", "taxonomy/subjects.yaml")
            rt_path = resolve_taxonomy_path(config, "resource_types_file", "taxonomy/resource_types.yaml")
            print(f"[OK] taxonomy subjects: {subjects_path}")
            print(f"[OK] taxonomy resource_types: {rt_path}")
        except FileNotFoundError as exc:
            issues.append(f"[ERROR] taxonomy 资源缺失: {exc}")
    except (FileNotFoundError, ValueError, ResourceResolutionError) as exc:
        issues.append(f"[ERROR] 配置加载失败: {exc}")

    examples_dir = Path("examples")
    if examples_dir.exists():
        html_files = [p for p in examples_dir.iterdir() if p.suffix.lower() in {".html", ".htm"}]
        if html_files:
            print(f"[OK] 示例数据: {len(html_files)} 个HTML文件")

    print("\n" + "=" * 50)
    if issues:
        print(f"发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    print("系统健康检查通过!")
    return True
