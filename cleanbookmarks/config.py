"""配置与资源加载"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from importlib import resources
except ImportError:  # pragma: no cover
    resources = None  # type: ignore[assignment]


class ResourceResolutionError(RuntimeError):
    """资源解析失败"""


def _packaged_path(*parts: str) -> Optional[Path]:
    """在打包资源中查找文件，返回一个长期有效的路径副本。

    源码树运行时包内资源是真实文件，直接返回；wheel/zip 安装时资源是
    虚拟的，需用 as_file() 物化，并立刻 copy 到持久位置（as_file 退出
    会清理临时文件）。
    """
    if resources is None:
        return None
    package = "cleanbookmarks.resources"
    target = resources.files(package)
    for part in parts:
        target = target.joinpath(part)
    if not target.is_file():
        return None
    try:
        with resources.as_file(target) as file_path:
            resolved = Path(file_path).resolve()
            # 真实文件（源码树/editable 安装）直接返回，避免每次复制临时文件
            if resolved.is_file():
                return resolved
            # 虚拟资源（wheel）必须复制，as_file 退出会删除临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=target.name) as tmp:
                tmp.write(resolved.read_bytes())
                return Path(tmp.name)
    except (AttributeError, TypeError, OSError):
        # as_file 不可用时（极端环境）退回直接路径
        return Path(target)


def default_config_path() -> Path:
    packaged = _packaged_path("config.json")
    if packaged is not None:
        return packaged
    raise ResourceResolutionError("无法定位默认配置文件 config.json")


def resolve_config_path(config_path: Optional[str] = None) -> Tuple[Path, bool]:
    """解析配置文件路径，返回 (path, is_explicit)"""
    if config_path:
        explicit = Path(config_path).expanduser()
        if not explicit.is_absolute():
            explicit = Path.cwd() / explicit
        explicit = explicit.resolve()
        if not explicit.is_file():
            raise FileNotFoundError(f"配置文件不存在: {explicit}")
        return explicit, True
    return default_config_path(), False


def load_json_config(config_path: Optional[str] = None) -> Tuple[Dict[str, Any], Path, bool]:
    """加载 JSON 配置文件，返回 (config, path, is_explicit)"""
    path, explicit = resolve_config_path(config_path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"配置文件顶层必须是对象: {path}")
    return data, path, explicit


def resolve_taxonomy_path(
    config: Optional[Dict[str, Any]], key: str, default_relative_path: str
) -> Path:
    """解析 taxonomy 资源路径"""
    taxonomy_cfg = (config or {}).get("taxonomy", {}) or {}
    raw_value = taxonomy_cfg.get(key) or default_relative_path
    candidate = Path(str(raw_value)).expanduser()

    if candidate.is_absolute():
        return candidate.resolve()
    if candidate.is_file():
        return candidate.resolve()
    if str(raw_value) != default_relative_path:
        return (Path.cwd() / candidate).resolve()

    packaged = _packaged_path(*Path(default_relative_path).parts)
    if packaged is not None:
        return packaged
    raise FileNotFoundError(f"无法定位 taxonomy 资源: {raw_value}")
