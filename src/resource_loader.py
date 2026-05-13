from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from importlib import resources
except ImportError:  # pragma: no cover
    resources = None  # type: ignore[assignment]


class ResourceResolutionError(RuntimeError):
    """Raised when packaged or explicit runtime resources cannot be resolved."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _candidate_repo_path(*parts: str) -> Path:
    return _repo_root().joinpath(*parts)


def _packaged_path(*parts: str) -> Optional[Path]:
    if resources is None:
        return None
    package = "src.resources"
    target = resources.files(package)
    for part in parts:
        target = target.joinpath(part)
    if not target.is_file():
        return None
    with resources.as_file(target) as file_path:
        return Path(file_path)


def default_config_path() -> Path:
    packaged = _packaged_path("config.json")
    if packaged is not None:
        return packaged

    repo_config = _candidate_repo_path("config.json")
    if repo_config.is_file():
        return repo_config

    raise ResourceResolutionError("无法定位默认配置文件 config.json")


def resolve_config_path(config_path: Optional[str] = None) -> Tuple[Path, bool]:
    if config_path:
        explicit = Path(config_path).expanduser()
        if not explicit.is_absolute():
            explicit = Path.cwd() / explicit
        explicit = explicit.resolve()
        if not explicit.is_file():
            raise FileNotFoundError(f"配置文件不存在: {explicit}")
        return explicit, True

    return default_config_path(), False


def load_json_config(
    config_path: Optional[str] = None,
) -> Tuple[Dict[str, Any], Path, bool]:
    """加载 JSON 配置文件

    .. deprecated::
        推荐使用 :class:`~src.config_manager.EnhancedConfigManager`，
        它提供配置验证、动态重载、环境变量覆盖等功能。

        迁移示例::

            # 旧方式
            from src.utils.resource_loader import load_json_config
            config, path, explicit = load_json_config(config_path)

            # 新方式
            from src.config_manager import EnhancedConfigManager
            manager = EnhancedConfigManager(config_path)
            config = manager.config
    """
    warnings.warn(
        "load_json_config 已弃用，推荐使用 EnhancedConfigManager。"
        "详见 https://github.com/your-repo/wiki/config-migration",
        DeprecationWarning,
        stacklevel=2,
    )

    path, explicit = resolve_config_path(config_path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"配置文件不是合法 JSON: {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"配置文件顶层必须是对象: {path}")

    return data, path, explicit


def resolve_taxonomy_path(
    config: Optional[Dict[str, Any]], key: str, default_relative_path: str
) -> Path:
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
    if str(raw_value) == default_relative_path and packaged is not None:
        return packaged

    repo_candidate = _candidate_repo_path(*Path(default_relative_path).parts)
    if str(raw_value) == default_relative_path and repo_candidate.is_file():
        return repo_candidate

    raise FileNotFoundError(f"无法定位 taxonomy 资源: {raw_value}")
