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


def read_json_config_file(path: Path) -> Dict[str, Any]:
    """从指定路径读取 JSON 配置（不经过资源解析）"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"配置文件顶层必须是对象: {path}")
    return data


def write_json_config_file(path: Path, config: Dict[str, Any]) -> None:
    """以 UTF-8 写 JSON 配置（保留缩进与原结构）"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")


def backup_config_file(path: Path, keep: int = 5) -> Optional[Path]:
    """备份配置文件为 <name>.llm-backup-<timestamp>.json，仅保留最近 keep 份。

    返回备份路径；文件不存在时返回 None。
    """
    if not path.is_file():
        return None
    from datetime import datetime
    # 含微秒，避免同秒内多次备份相互覆盖
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup = path.with_name(f"{path.stem}.llm-backup-{ts}{path.suffix}")
    backup.write_bytes(path.read_bytes())

    # 清理旧备份，只保留最近 keep 份
    backups = sorted(path.parent.glob(f"{path.stem}.llm-backup-*{path.suffix}"))
    for old in backups[:-keep]:
        old.unlink(missing_ok=True)
    return backup


def apply_category_updates(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """把 LLM 建议的规则增量应用到配置（纯函数，不写盘）。

    支持两类保守更新：
    - category_updates: [{category, add_keywords}] 给现有类目追加关键词
    - add_categories:   [{category, keywords}]     新增类目（含初始规则）

    只做增量，绝不删除/合并现有规则。
    """
    result = dict(config)
    category_rules = dict(result.get("category_rules", {}) or {})
    category_order = list(result.get("category_order", []) or [])

    def _existing_keywords(cat_key: str):
        cat_data = category_rules.get(cat_key) or {}
        if not isinstance(cat_data, dict):
            return set()
        kws = set()
        for rule in cat_data.get("rules", []) or []:
            for kw in (rule or {}).get("keywords", []) or []:
                kws.add(kw)
        return kws

    def _append_rule(cat_key: str, keywords: list):
        cat_data = category_rules.setdefault(cat_key, {"rules": []})
        if not isinstance(cat_data.get("rules"), list):
            cat_data["rules"] = []
        existing = _existing_keywords(cat_key)
        new_kws = [k for k in keywords if k and k not in existing]
        if new_kws:
            cat_data["rules"].append({"match": "any", "keywords": new_kws, "weight": 1.0})

    for update in (updates.get("category_updates") or []):
        if not isinstance(update, dict):
            continue
        cat = (update.get("category") or "").strip()
        if not cat:
            continue
        add_kws = update.get("add_keywords") or []
        if not isinstance(add_kws, list):
            continue
        if cat in category_rules:
            _append_rule(cat, add_kws)
        else:
            # 类目不存在则退化为新增类目
            category_rules.setdefault(cat, {"rules": []})
            _append_rule(cat, add_kws)
            if cat not in category_order:
                category_order.append(cat)

    for new_cat in (updates.get("add_categories") or []):
        if not isinstance(new_cat, dict):
            continue
        cat = (new_cat.get("category") or "").strip()
        if not cat:
            continue
        if cat not in category_rules:
            category_rules.setdefault(cat, {"rules": []})
        _append_rule(cat, new_cat.get("keywords") or [])
        if cat not in category_order:
            category_order.append(cat)

    result["category_rules"] = category_rules
    result["category_order"] = category_order
    return result
