"""分类法服务 - 受控词表标准化"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from cleanbook.config import resolve_taxonomy_path
from cleanbook.text_utils import strip_prefix

logger = logging.getLogger(__name__)


class TaxonomyService:
    """分类法标准化服务

    提供 subject / resource_type 的标准化和推导。
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.taxonomy_path = resolve_taxonomy_path(
            self.config, "subjects_file", "taxonomy/subjects.yaml"
        )
        self._hierarchy: Dict = {}
        self._resource_types_map: Dict[str, str] = {}
        self._load_taxonomy()
        self._load_resource_types()

    def _load_taxonomy(self):
        if not self.taxonomy_path.exists():
            self._hierarchy = {"subjects": []}
            return
        try:
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                self._hierarchy = yaml.safe_load(f) or {"subjects": []}
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            self._hierarchy = {"subjects": []}

    def _load_resource_types(self):
        self._resource_types_map = {}
        try:
            rt_path = resolve_taxonomy_path(
                self.config, "resource_types_file", "taxonomy/resource_types.yaml"
            )
            if Path(rt_path).exists():
                with open(rt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                rts = data.get("resource_types", {}) or {}
                for key, meta in rts.items():
                    key_l = str(key).strip().lower()
                    if key_l:
                        self._resource_types_map[key_l] = key
                    for v in (meta or {}).get("variants", []) or []:
                        v = str(v).strip()
                        if v:
                            self._resource_types_map[v.lower()] = key
        except Exception as e:
            logger.debug(f"Failed to load resource types: {e}")

    def _find_category_entry(self, name: str) -> Optional[Dict]:
        if not name:
            return None
        cleaned = strip_prefix(name)
        low = cleaned.lower()
        for entry in self._hierarchy.get("subjects", []):
            preferred = entry.get("preferred", "")
            if preferred.lower() == low:
                return entry
            for v in entry.get("variants", []):
                if str(v).lower() == low:
                    return entry
        return None

    def normalize_subject(self, text: str) -> Optional[str]:
        if not text:
            return None
        cleaned = strip_prefix(text)
        entry = self._find_category_entry(cleaned)
        if entry is not None:
            return entry.get("preferred", cleaned)
        return cleaned

    def normalize_resource_type(self, text: str) -> Optional[str]:
        if not text:
            return None
        cleaned = strip_prefix(text)
        return self._resource_types_map.get(cleaned.lower())

    def derive_from_category(
        self, category: str, content_type: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """从分类字符串推导 (subject, resource_type)"""
        if not category:
            return None, None
        cat = str(category).strip()
        main, sub = (cat.split("/", 1) + [""])[:2] if "/" in cat else (cat, None)
        main, sub = main.strip(), (sub.strip() if sub else None)

        subject = self.normalize_subject(main)
        resource_type = self.normalize_resource_type(sub) if sub else None

        if not resource_type and content_type:
            ct_map = {
                "code_repository": "code_repository",
                "documentation": "documentation",
                "video": "video",
                "academic_paper": "paper",
                "news": "news",
                "online_tool": "tool",
                "webpage": "webpage",
            }
            resource_type = ct_map.get(content_type)
        return subject, resource_type
