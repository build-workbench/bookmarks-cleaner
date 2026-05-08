"""
OrganizationPipeline - 组织与排序管道

使用 TaxonomyStandardizer 将分类后的书签组织成层次结构。

特性：
- 按 subject/resource_type 两级组织
- 使用受控词表标准化
- 支持配置的排序顺序
- 详细的组织统计
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from src.utils.standardizer import TaxonomyStandardizer


class OrganizationPipeline:
    """组织与排序管道
    
    深度: 高（简单接口，复杂的组织和排序逻辑）
    接口: organize(classified_bookmarks, config) -> (organized_bookmarks, stats)
    
    示例:
        pipeline = OrganizationPipeline(standardizer)
        
        # 组织书签
        organized, stats = pipeline.organize(classified_bookmarks, config)
        print(f"组织了 {stats['total_subjects']} 个主题")
    """
    
    def __init__(self, standardizer: TaxonomyStandardizer):
        """初始化组织管道
        
        Args:
            standardizer: 分类法标准化器
        """
        self.standardizer = standardizer
        self.logger = logging.getLogger(__name__)
        
        # 统计信息
        self.stats = {
            "total_subjects": 0,
            "total_resource_types": 0,
            "total_bookmarks": 0,
        }
    
    def organize(
        self,
        classified_bookmarks: List[Dict],
        config: Dict
    ) -> Tuple[Dict, Dict]:
        """组织分类后的书签
        
        Args:
            classified_bookmarks: 已分类的书签列表
            config: 配置字典（包含 category_order 等）
            
        Returns:
            (organized_bookmarks, stats) 元组
        """
        self._reset_stats()
        
        if not classified_bookmarks:
            return {}, self.stats.copy()
        
        # 第一阶段：按 subject/resource_type 两级组织
        organized = self._organize_by_subject_and_type(classified_bookmarks)
        
        # 第二阶段：排序
        sorted_organized = self._sort_organized_structure(organized, config)
        
        # 更新统计
        self._update_stats(sorted_organized)
        
        return sorted_organized, self.stats.copy()
    
    def _organize_by_subject_and_type(
        self,
        classified_bookmarks: List[Dict]
    ) -> Dict[str, Dict]:
        """按 subject -> resource_type 两级组织"""
        organized: Dict[str, Dict] = {}
        
        for bookmark in classified_bookmarks:
            category = (bookmark.get("category") or "").strip()
            subcategory = (bookmark.get("subcategory") or "").strip() or None
            
            # 从分类派生 subject / resource_type
            derived_subject, derived_rt = self.standardizer.derive_from_category(
                category, content_type=None
            )
            
            # 标准化 subject 与 resource_type
            subject = (
                derived_subject
                or self.standardizer.normalize_subject(category)
                or "其他"
            )
            
            # 优先使用规则引擎提供的 resource_type 分面提示
            facets = bookmark.get("facets") or {}
            facet_rt_hint = (
                facets.get("resource_type_hint") if isinstance(facets, dict) else None
            )
            facet_rt_std = (
                self.standardizer.normalize_resource_type(facet_rt_hint)
                if facet_rt_hint
                else None
            )
            resource_type = (
                facet_rt_std
                or self.standardizer.normalize_resource_type(subcategory)
                or derived_rt
            )
            
            # 初始化 subject 节点
            if subject not in organized:
                organized[subject] = {"_items": [], "_subcategories": {}}
            
            # 放入 resource_type 子类或直接归于 subject
            if resource_type:
                if resource_type not in organized[subject]["_subcategories"]:
                    organized[subject]["_subcategories"][resource_type] = {"_items": []}
                organized[subject]["_subcategories"][resource_type]["_items"].append(
                    bookmark
                )
            else:
                organized[subject]["_items"].append(bookmark)
        
        return organized
    
    def _sort_organized_structure(
        self,
        organized: Dict[str, Dict],
        config: Dict
    ) -> Dict[str, Dict]:
        """统一的排序逻辑，保证导出结果有序"""
        if not organized:
            return {}
        
        def _count_subject(subject_data: Dict) -> int:
            total = 0
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                total += len(items)
            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        total += len(sub_items)
            return total
        
        # 获取配置的分类顺序
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
        
        # 构建排序后的主题列表
        ordered_subjects: List[str] = []
        ordered_subjects.extend(preferred_subject_order)
        
        remaining = [s for s in organized.keys() if s not in ordered_subjects]
        remaining.sort(key=lambda s: (-_count_subject(organized.get(s) or {}), str(s)))
        ordered_subjects.extend(remaining)
        
        # 排序并构建结果
        sorted_organized: Dict[str, Dict] = {}
        for subject in ordered_subjects:
            subject_data = organized.get(subject) or {}
            
            # 按置信度排序 items
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                items.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
                subject_data["_items"] = items
            
            # 排序子分类
            subcategories = subject_data.get("_subcategories", {})
            if isinstance(subcategories, dict):
                # 按置信度排序每个子分类的 items
                for sub_data in subcategories.values():
                    sub_items = (sub_data or {}).get("_items", [])
                    if isinstance(sub_items, list):
                        sub_items.sort(
                            key=lambda x: x.get("confidence", 0.0), reverse=True
                        )
                        sub_data["_items"] = sub_items
                
                # 按数量排序子分类
                ordered_subcats = sorted(
                    subcategories.items(),
                    key=lambda kv: (
                        -len((kv[1] or {}).get("_items", []) or []),
                        str(kv[0]),
                    ),
                )
                subject_data["_subcategories"] = {k: v for k, v in ordered_subcats}
            
            sorted_organized[subject] = subject_data
        
        return sorted_organized
    
    def _update_stats(self, organized: Dict[str, Dict]) -> None:
        """更新统计信息"""
        total_bookmarks = 0
        total_resource_types = 0
        
        for subject_data in organized.values():
            # 统计直接 items
            items = subject_data.get("_items", [])
            if isinstance(items, list):
                total_bookmarks += len(items)
            
            # 统计子分类
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
    
    def _reset_stats(self) -> None:
        """重置统计信息"""
        self.stats = {
            "total_subjects": 0,
            "total_resource_types": 0,
            "total_bookmarks": 0,
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
