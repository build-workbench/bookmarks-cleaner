"""
config - 项目配置目录

包含分类法定义、Agent配置等配置文件
"""

import os
from pathlib import Path

def get_config_dir() -> Path:
    """返回配置目录路径"""
    return Path(__file__).parent


def get_taxonomy_path(filename: str = "subjects.yaml") -> Path:
    """获取分类法文件路径"""
    return get_config_dir() / "taxonomy" / filename
