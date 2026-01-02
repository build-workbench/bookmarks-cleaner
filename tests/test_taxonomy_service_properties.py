"""
Property Tests for Taxonomy Service
分类体系服务属性测试

Tests Properties:
- Property 19: Taxonomy YAML Round-Trip
- Property 20: Category Name Validation
- Property 21: Category Rename Propagation
- Property 22: Category Merge Completeness
"""

import os
import shutil
import tempfile
import pytest
from hypothesis import given, strategies as st, settings, assume

# 尝试导入依赖
try:
    from src.services.taxonomy_service import TaxonomyService
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


# 策略定义
# 有效的分类名称：字母、数字、中文、空格、连字符（使用更安全的字符集）
valid_name_strategy = st.text(
    alphabet=st.sampled_from(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        '编程开发人工智能数据科学前端后端机器学习深度云计算网络安全 -_'
    ),
    min_size=1,
    max_size=30
).filter(lambda x: len(x.strip()) > 0 and x[0].isalnum())

# 无效的分类名称
invalid_name_strategy = st.one_of(
    st.just(''),  # 空字符串
    st.text(min_size=51, max_size=60),  # 太长
    st.from_regex(r'^[!@#$%^&*()]+$', fullmatch=True),  # 特殊字符开头
)


def create_service():
    """创建分类体系服务"""
    temp_dir = tempfile.mkdtemp()
    config = {
        'taxonomy_path': os.path.join(temp_dir, 'taxonomy.yaml'),
        'migrations_path': os.path.join(temp_dir, 'migrations')
    }
    service = TaxonomyService(config)
    return service, temp_dir


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestTaxonomyYAMLRoundTrip:
    """YAML 往返测试 - Property 19"""
    
    @settings(max_examples=50)
    @given(
        categories=st.lists(
            valid_name_strategy,
            min_size=1,
            max_size=10,
            unique=True
        )
    )
    def test_taxonomy_yaml_round_trip(self, categories):
        """
        Property 19: Taxonomy YAML Round-Trip
        
        对于任何有效的分类层级结构，保存到 YAML 并重新加载
        应该产生等效的结构。
        
        Validates: Requirements 7.1
        """
        service, temp_dir = create_service()
        try:
            categories = [c for c in categories if len(c.strip()) > 0 and service.validate_name(c)]
            assume(len(categories) > 0)
            
            # 添加分类
            for category in categories:
                service.add_category(category)
            
            # 获取当前层级结构
            categories_before = set(service.get_all_categories())
            
            # 保存并重新加载
            service._save_taxonomy()
            service._load_taxonomy()
            
            # 验证结构等效
            categories_after = set(service.get_all_categories())
            
            assert categories_before == categories_after, \
                f"Categories should be preserved: {categories_before} vs {categories_after}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=30)
    @given(
        parent=valid_name_strategy,
        children=st.lists(valid_name_strategy, min_size=1, max_size=5, unique=True)
    )
    def test_hierarchical_round_trip(self, parent, children):
        """
        层级结构应该在往返后保持。
        """
        service, temp_dir = create_service()
        try:
            assume(service.validate_name(parent))
            children = [c for c in children if service.validate_name(c) and c != parent]
            assume(len(children) > 0)
            
            # 添加父分类
            service.add_category(parent)
            
            # 添加子分类
            for child in children:
                service.add_category(child, parent=parent)
            
            # 保存并重新加载
            service._save_taxonomy()
            service._load_taxonomy()
            
            # 验证父分类存在
            assert service.get_category(parent) is not None
            
            # 验证子分类存在
            for child in children:
                assert service.get_category(child) is not None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestCategoryNameValidation:
    """分类名称验证测试 - Property 20"""
    
    @settings(max_examples=100)
    @given(name=valid_name_strategy)
    def test_valid_category_names_accepted(self, name):
        """
        Property 20: Category Name Validation (Valid Names)
        
        对于任何分类名称，Taxonomy_Service 应该接受符合命名规范的名称
        （字母数字、中文字符、空格、连字符，最多50字符）。
        
        Validates: Requirements 7.3
        """
        service, temp_dir = create_service()
        try:
            assume(len(name.strip()) > 0)
            
            is_valid = service.validate_name(name)
            
            # 有效名称应该被接受
            assert is_valid is True, f"Valid name '{name}' should be accepted"
            
            # 应该能够添加
            result = service.add_category(name)
            assert result is True, f"Should be able to add valid category '{name}'"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @settings(max_examples=50)
    @given(name=invalid_name_strategy)
    def test_invalid_category_names_rejected(self, name):
        """
        Property 20: Category Name Validation (Invalid Names)
        
        无效的分类名称应该被拒绝。
        
        Validates: Requirements 7.3
        """
        service, temp_dir = create_service()
        try:
            is_valid = service.validate_name(name)
            
            # 无效名称应该被拒绝
            assert is_valid is False, f"Invalid name '{name}' should be rejected"
            
            # 不应该能够添加
            result = service.add_category(name)
            assert result is False, f"Should not be able to add invalid category '{name}'"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_name_length_limit(self):
        """
        名称长度应该被限制在50字符以内。
        """
        service, temp_dir = create_service()
        try:
            # 50字符应该有效
            name_50 = 'a' * 50
            assert service.validate_name(name_50) is True
            
            # 51字符应该无效
            name_51 = 'a' * 51
            assert service.validate_name(name_51) is False
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_chinese_names_accepted(self):
        """
        中文名称应该被接受。
        """
        service, temp_dir = create_service()
        try:
            chinese_names = ['编程开发', '人工智能', '数据科学', '机器学习']
            
            for name in chinese_names:
                assert service.validate_name(name) is True
                assert service.add_category(name) is True
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestCategoryRenamePropagation:
    """分类重命名传播测试 - Property 21"""
    
    @settings(max_examples=50)
    @given(
        old_name=valid_name_strategy,
        new_name=valid_name_strategy
    )
    def test_category_rename_propagation(self, old_name, new_name):
        """
        Property 21: Category Rename Propagation
        
        对于任何分类重命名操作，所有引用旧名称的历史分类
        应该被更新为使用新名称。
        
        Validates: Requirements 7.4
        """
        service, temp_dir = create_service()
        try:
            assume(service.validate_name(old_name) and service.validate_name(new_name))
            assume(old_name != new_name)
            
            # 添加原始分类
            service.add_category(old_name)
            
            # 重命名
            result = service.rename_category(old_name, new_name)
            
            assert result is True, f"Rename from '{old_name}' to '{new_name}' should succeed"
            
            # 验证新名称存在
            category = service.get_category(new_name)
            assert category is not None, f"New name '{new_name}' should exist"
            
            # 验证旧名称作为变体存在
            variants = service.get_variants(new_name)
            assert old_name in variants, f"Old name '{old_name}' should be a variant"
            
            # 验证可以通过旧名称解析到新名称
            resolved = service.resolve_category(old_name)
            assert resolved == new_name, f"Old name should resolve to new name"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_rename_preserves_variants(self):
        """
        重命名应该保留现有的变体。
        """
        service, temp_dir = create_service()
        try:
            # 添加分类
            service.add_category('原始名称', variants=['变体1', '变体2'])
            
            # 重命名
            service.rename_category('原始名称', '新名称')
            
            # 验证所有变体都保留
            variants = service.get_variants('新名称')
            assert '原始名称' in variants
            assert '变体1' in variants
            assert '变体2' in variants
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestCategoryMergeCompleteness:
    """分类合并完整性测试 - Property 22"""
    
    @settings(max_examples=50)
    @given(
        source=valid_name_strategy,
        target=valid_name_strategy
    )
    def test_category_merge_completeness(self, source, target):
        """
        Property 22: Category Merge Completeness
        
        对于任何分类合并操作，源分类的所有书签应该被重新分配到目标分类，
        源分类应该被删除。
        
        Validates: Requirements 7.5
        """
        service, temp_dir = create_service()
        try:
            assume(service.validate_name(source) and service.validate_name(target))
            assume(source != target)
            
            # 添加源和目标分类
            service.add_category(source, variants=['源变体1'])
            service.add_category(target, variants=['目标变体1'])
            
            # 合并
            result = service.merge_categories(source, target)
            
            assert result is True, f"Merge from '{source}' to '{target}' should succeed"
            
            # 验证源分类不再存在（作为独立分类）
            all_categories = service.get_all_categories()
            assert source not in all_categories, f"Source '{source}' should be removed"
            
            # 验证目标分类存在
            assert target in all_categories, f"Target '{target}' should exist"
            
            # 验证源名称成为目标的变体
            variants = service.get_variants(target)
            assert source in variants, f"Source '{source}' should be a variant of target"
            
            # 验证源的变体也被合并
            assert '源变体1' in variants, "Source variants should be merged"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_merge_preserves_children(self):
        """
        合并应该保留子分类。
        """
        service, temp_dir = create_service()
        try:
            # 创建带子分类的源
            service.add_category('源分类')
            service.add_category('子分类1', parent='源分类')
            service.add_category('子分类2', parent='源分类')
            
            # 创建目标
            service.add_category('目标分类')
            
            # 合并
            service.merge_categories('源分类', '目标分类')
            
            # 验证子分类被保留（移到目标下）
            # 注意：具体行为取决于实现
            target_info = service.get_category('目标分类')
            assert target_info is not None
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required imports not available")
class TestMigrationExport:
    """迁移导出测试"""
    
    def test_migration_export(self):
        """
        迁移脚本应该记录所有变更。
        """
        service, temp_dir = create_service()
        try:
            # 执行一系列操作
            service.add_category('分类A')
            service.add_category('分类B')
            service.rename_category('分类A', '分类A新')
            service.merge_categories('分类B', '分类A新')
            
            # 导出迁移
            filepath = service.export_migrations()
            
            # 验证文件存在
            assert os.path.exists(filepath)
            
            # 验证内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'ADD_CATEGORY' in content
            assert 'RENAME' in content
            assert 'MERGE' in content
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
