"""组织与排序管道 - 按 subject/resource_type 两级组织"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from cleanbook.taxonomy import TaxonomyService


class OrganizationPipeline:
    """组织分类后的书签为层次结构"""

    def __init__(self, standardizer: TaxonomyService):
        self.standardizer = standardizer
        self.logger = logging.getLogger(__name__)
        self.stats = {"total_subjects": 0, "total_resource_types": 0, "total_bookmarks": 0}

    def organize(self, classified_bookmarks: List[Dict], config: Dict) -> Tuple[Dict, Dict]:
        self._reset_stats()
        if not classified_bookmarks:
            return {}, self.stats.copy()
        organized = self._organize_by_subject_and_type(classified_bookmarks)
        sorted_organized = self._sort_organized_structure(organized, config)
        self._update_stats(sorted_organized)
        return sorted_organized, self.stats.copy()

    def _organize_by_subject_and_type(self, classified_bookmarks: List[Dict]) -> Dict[str, Dict]:
        organized: Dict[str, Dict] = {}
        for bookmark in classified_bookmarks:
            category = (bookmark.get("category") or "").strip()
            subcategory = (bookmark.get("subcategory") or "").strip() or None
            derived_subject, derived_rt = self.standardizer.derive_from_category(category, content_type=None)
            subject = derived_subject or self.standardizer.normalize_subject(category) or "其他"

            facets = bookmark.get("facets") or {}
            facet_rt_hint = facets.get("resource_type_hint") if isinstance(facets, dict) else None
            facet_rt_std = self.standardizer.normalize_resource_type(facet_rt_hint) if facet_rt_hint else None
            resource_type = facet_rt_std or self.standardizer.normalize_resource_type(subcategory) or derived_rt

            if subject not in organized:
                organized[subject] = {"_items": [], "_subcategories": {}}
            if resource_type:
                if resource_type not in organized[subject]["_subcategories"]:
                    organized[subject]["_subcategories"][resource_type] = {"_items": []}
                organized[subject]["_subcategories"][resource_type]["_items"].append(bookmark)
            else:
                organized[subject]["_items"].append(bookmark)
        return organized

    def _sort_organized_structure(self, organized: Dict[str, Dict], config: Dict) -> Dict[str, Dict]:
        if not organized:
            return {}

        def _count_subject(subject_data: Dict) -> int:
            total = len(subject_data.get("_items", []) or [])
            for sub_data in (subject_data.get("_subcategories", {}) or {}).values():
                total += len((sub_data or {}).get("_items", []) or [])
            return total

        category_order = config.get("category_order")
        preferred_subject_order: List[str] = []
        if isinstance(category_order, list):
            for raw in category_order:
                if not raw:
                    continue
                subj = self.standardizer.normalize_subject(str(raw))
                if subj and subj not in preferred_subject_order:
                    preferred_subject_order.append(subj)
        preferred_subject_order = [s for s in preferred_subject_order if s in organized]

        ordered_subjects: List[str] = list(preferred_subject_order)
        remaining = [s for s in organized if s not in ordered_subjects]
        remaining.sort(key=lambda s: (-_count_subject(organized.get(s) or {}), str(s)))
        ordered_subjects.extend(remaining)

        sorted_organized: Dict[str, Dict] = {}
        for subject in ordered_subjects:
            subject_data = organized.get(subject) or {}
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                items.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
                subject_data["_items"] = items
            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        sub_items.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
                ordered_subcats = sorted(
                    subcategories.items(),
                    key=lambda kv: (-len((kv[1] or {}).get("_items", []) or []), str(kv[0])),
                )
                subject_data["_subcategories"] = {k: v for k, v in ordered_subcats}
            sorted_organized[subject] = subject_data
        return sorted_organized

    def _update_stats(self, organized: Dict[str, Dict]) -> None:
        total_bookmarks = 0
        total_resource_types = 0
        for subject_data in organized.values():
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                total_bookmarks += len(items)
            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                total_resource_types += len(subcategories)
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        total_bookmarks += len(sub_items)
        self.stats["total_subjects"] = len(organized)
        self.stats["total_resource_types"] = total_resource_types
        self.stats["total_bookmarks"] = total_bookmarks

    def _reset_stats(self):
        self.stats = {"total_subjects": 0, "total_resource_types": 0, "total_bookmarks": 0}
