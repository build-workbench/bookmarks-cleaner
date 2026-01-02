"""
Taxonomy Service - 分类体系动态管理服务
支持分类的添加、重命名、合并和迁移脚本导出
"""

import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml


class TaxonomyService:
    """分类体系动态管理服务"""
    
    # 分类名称验证正则：字母、数字、中文、空格、连字符，最多50字符
    VALID_NAME_PATTERN = re.compile(r'^[\w\u4e00-\u9fff][\w\u4e00-\u9fff\s\-]{0,49}$')
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化分类体系服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.taxonomy_path = self.config.get('taxonomy_path', 'taxonomy/subjects.yaml')
        self.migrations_path = self.config.get('migrations_path', 'taxonomy/migrations')
        
        # 分类层级结构
        self._hierarchy: Dict = {}
        
        # 变更日志
        self._change_log: List[Dict] = []
        
        self.logger = logging.getLogger(__name__)
        
        # 加载分类体系
        self._load_taxonomy()
    
    def _load_taxonomy(self):
        """加载分类体系"""
        if not os.path.exists(self.taxonomy_path):
            self._hierarchy = {'subjects': []}
            return
        
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                self._hierarchy = yaml.safe_load(f) or {'subjects': []}
        except Exception as e:
            self.logger.error(f"Failed to load taxonomy: {e}")
            self._hierarchy = {'subjects': []}
    
    def _save_taxonomy(self):
        """保存分类体系"""
        try:
            os.makedirs(os.path.dirname(self.taxonomy_path), exist_ok=True)
            
            with open(self.taxonomy_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self._hierarchy,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False
                )
        except Exception as e:
            self.logger.error(f"Failed to save taxonomy: {e}")
            raise
    
    def validate_name(self, name: str) -> bool:
        """
        验证分类名称
        
        Args:
            name: 分类名称
            
        Returns:
            名称是否有效
        """
        if not name or len(name) > 50:
            return False
        return bool(self.VALID_NAME_PATTERN.match(name))
    
    def add_category(
        self,
        name: str,
        parent: Optional[str] = None,
        variants: List[str] = None,
        description: str = ""
    ) -> bool:
        """
        添加新分类
        
        Args:
            name: 分类名称
            parent: 父分类名称（可选）
            variants: 变体名称列表
            description: 分类描述
            
        Returns:
            添加是否成功
        """
        if not self.validate_name(name):
            self.logger.error(f"Invalid category name: {name}")
            return False
        
        # 检查是否已存在
        if self.get_category(name) is not None:
            self.logger.warning(f"Category already exists: {name}")
            return False
        
        new_entry = {
            'preferred': name,
            'variants': variants or [],
            'description': description
        }
        
        if parent:
            # 添加到父分类下
            parent_entry = self._find_category_entry(parent)
            if parent_entry is None:
                self.logger.error(f"Parent category not found: {parent}")
                return False
            
            if 'children' not in parent_entry:
                parent_entry['children'] = []
            parent_entry['children'].append(new_entry)
        else:
            # 添加为顶级分类
            self._hierarchy.setdefault('subjects', []).append(new_entry)
        
        self._record_change('add', name, None, {'parent': parent})
        self._save_taxonomy()
        
        self.logger.info(f"Added category: {name}")
        return True
    
    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        重命名分类
        
        Args:
            old_name: 旧名称
            new_name: 新名称
            
        Returns:
            重命名是否成功
        """
        if not self.validate_name(new_name):
            self.logger.error(f"Invalid new category name: {new_name}")
            return False
        
        entry = self._find_category_entry(old_name)
        if entry is None:
            self.logger.error(f"Category not found: {old_name}")
            return False
        
        # 检查新名称是否已存在
        if old_name != new_name and self.get_category(new_name) is not None:
            self.logger.error(f"Category already exists: {new_name}")
            return False
        
        # 更新名称
        entry['preferred'] = new_name
        
        # 将旧名称添加为变体
        if 'variants' not in entry:
            entry['variants'] = []
        if old_name not in entry['variants']:
            entry['variants'].append(old_name)
        
        self._record_change('rename', old_name, new_name)
        self._save_taxonomy()
        
        self.logger.info(f"Renamed category: {old_name} -> {new_name}")
        return True
    
    def merge_categories(self, source: str, target: str) -> bool:
        """
        合并分类
        
        Args:
            source: 源分类（将被删除）
            target: 目标分类（保留）
            
        Returns:
            合并是否成功
        """
        source_entry = self._find_category_entry(source)
        target_entry = self._find_category_entry(target)
        
        if source_entry is None:
            self.logger.error(f"Source category not found: {source}")
            return False
        
        if target_entry is None:
            self.logger.error(f"Target category not found: {target}")
            return False
        
        if source == target:
            self.logger.warning("Cannot merge category with itself")
            return False
        
        # 合并变体
        target_variants = set(target_entry.get('variants', []))
        target_variants.add(source)
        target_variants.update(source_entry.get('variants', []))
        target_entry['variants'] = list(target_variants)
        
        # 合并子分类
        if 'children' in source_entry:
            if 'children' not in target_entry:
                target_entry['children'] = []
            target_entry['children'].extend(source_entry['children'])
        
        # 删除源分类
        self._remove_category_entry(source)
        
        self._record_change('merge', source, target)
        self._save_taxonomy()
        
        self.logger.info(f"Merged category: {source} -> {target}")
        return True
    
    def delete_category(self, name: str) -> bool:
        """
        删除分类
        
        Args:
            name: 分类名称
            
        Returns:
            删除是否成功
        """
        entry = self._find_category_entry(name)
        if entry is None:
            self.logger.error(f"Category not found: {name}")
            return False
        
        self._remove_category_entry(name)
        
        self._record_change('delete', name, None)
        self._save_taxonomy()
        
        self.logger.info(f"Deleted category: {name}")
        return True
    
    def get_category(self, name: str) -> Optional[Dict]:
        """
        获取分类信息
        
        Args:
            name: 分类名称
            
        Returns:
            分类信息字典，如果不存在则返回 None
        """
        entry = self._find_category_entry(name)
        if entry is None:
            return None
        
        return {
            'name': entry.get('preferred', name),
            'variants': entry.get('variants', []),
            'description': entry.get('description', ''),
            'has_children': 'children' in entry
        }
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有分类名称
        
        Returns:
            分类名称列表
        """
        categories = []
        self._collect_categories(self._hierarchy.get('subjects', []), categories)
        return categories
    
    def _collect_categories(self, subjects: List[Dict], result: List[str]):
        """递归收集所有分类名称"""
        for subject in subjects:
            name = subject.get('preferred', '')
            if name:
                result.append(name)
            
            # 递归处理子分类
            if 'children' in subject:
                self._collect_categories(subject['children'], result)
    
    def get_hierarchy(self) -> Dict:
        """
        获取完整的分类层级结构
        
        Returns:
            层级结构字典
        """
        return self._hierarchy.copy()
    
    def _find_category_entry(self, name: str, subjects: List[Dict] = None) -> Optional[Dict]:
        """
        查找分类条目
        
        Args:
            name: 分类名称
            subjects: 要搜索的分类列表
            
        Returns:
            分类条目字典
        """
        if subjects is None:
            subjects = self._hierarchy.get('subjects', [])
        
        for subject in subjects:
            # 检查首选名称
            if subject.get('preferred') == name:
                return subject
            
            # 检查变体名称
            if name in subject.get('variants', []):
                return subject
            
            # 递归搜索子分类
            if 'children' in subject:
                result = self._find_category_entry(name, subject['children'])
                if result is not None:
                    return result
        
        return None
    
    def _remove_category_entry(self, name: str, subjects: List[Dict] = None) -> bool:
        """
        移除分类条目
        
        Args:
            name: 分类名称
            subjects: 要搜索的分类列表
            
        Returns:
            是否成功移除
        """
        if subjects is None:
            subjects = self._hierarchy.get('subjects', [])
        
        for i, subject in enumerate(subjects):
            if subject.get('preferred') == name:
                subjects.pop(i)
                return True
            
            # 递归搜索子分类
            if 'children' in subject:
                if self._remove_category_entry(name, subject['children']):
                    return True
        
        return False
    
    def _record_change(self, action: str, source: str, target: Optional[str], extra: Dict = None):
        """
        记录变更
        
        Args:
            action: 操作类型
            source: 源分类
            target: 目标分类
            extra: 额外信息
        """
        change = {
            'action': action,
            'source': source,
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'extra': extra or {}
        }
        self._change_log.append(change)
    
    def get_change_log(self) -> List[Dict]:
        """获取变更日志"""
        return self._change_log.copy()
    
    def clear_change_log(self):
        """清空变更日志"""
        self._change_log.clear()
    
    def export_migrations(self) -> str:
        """
        导出迁移脚本
        
        Returns:
            迁移脚本文件路径
        """
        os.makedirs(self.migrations_path, exist_ok=True)
        
        migration_content = "# Taxonomy Migration Script\n"
        migration_content += f"# Generated at: {datetime.now().isoformat()}\n\n"
        
        for change in self._change_log:
            action = change['action']
            source = change['source']
            target = change.get('target')
            timestamp = change['timestamp']
            
            migration_content += f"# {timestamp}\n"
            
            if action == 'add':
                parent = change.get('extra', {}).get('parent', '')
                if parent:
                    migration_content += f"ADD_CATEGORY: {source} UNDER {parent}\n"
                else:
                    migration_content += f"ADD_CATEGORY: {source}\n"
            elif action == 'rename':
                migration_content += f"RENAME: {source} -> {target}\n"
            elif action == 'merge':
                migration_content += f"MERGE: {source} -> {target}\n"
            elif action == 'delete':
                migration_content += f"DELETE: {source}\n"
            
            migration_content += "\n"
        
        filename = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.migrations_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        
        self.logger.info(f"Exported migration script: {filepath}")
        return filepath
    
    def resolve_category(self, name: str) -> str:
        """
        解析分类名称（处理变体和别名）
        
        Args:
            name: 输入的分类名称
            
        Returns:
            标准化的分类名称
        """
        entry = self._find_category_entry(name)
        if entry is not None:
            return entry.get('preferred', name)
        return name
    
    def get_variants(self, name: str) -> List[str]:
        """
        获取分类的所有变体名称
        
        Args:
            name: 分类名称
            
        Returns:
            变体名称列表
        """
        entry = self._find_category_entry(name)
        if entry is None:
            return []
        return entry.get('variants', [])
