"""
测试 Taxonomy 合并后的 TaxonomyService
"""

import pytest


class TestTaxonomyServiceNormalization:
    """测试 TaxonomyService 的标准化方法"""

    @pytest.fixture
    def taxonomy_service(self):
        """创建 TaxonomyService"""
        from src.services.taxonomy_service import TaxonomyService
        return TaxonomyService()

    def test_normalize_subject(self, taxonomy_service):
        """标准化主题分类"""
        # 测试已知分类
        result = taxonomy_service.normalize_subject("技术")
        assert result is not None

        # 测试空输入
        assert taxonomy_service.normalize_subject("") is None
        assert taxonomy_service.normalize_subject(None) is None

    def test_normalize_resource_type(self, taxonomy_service):
        """标准化资源类型"""
        result = taxonomy_service.normalize_resource_type("documentation")
        # 结果取决于 taxonomy/resource_types.yaml 的内容
        # 空输入返回 None
        assert taxonomy_service.normalize_resource_type("") is None
        assert taxonomy_service.normalize_resource_type(None) is None

    def test_derive_from_category(self, taxonomy_service):
        """从分类字符串推导"""
        # 测试带子分类的分类
        subject, rtype = taxonomy_service.derive_from_category("技术/文档")
        assert subject is not None

        # 测试不带子分类
        subject, rtype = taxonomy_service.derive_from_category("技术")
        assert subject is not None
        assert rtype is None

        # 测试空输入
        subject, rtype = taxonomy_service.derive_from_category("")
        assert subject is None
        assert rtype is None

    def test_derive_from_category_with_content_type(self, taxonomy_service):
        """从分类和内容类型推导"""
        subject, rtype = taxonomy_service.derive_from_category(
            "技术", content_type="documentation"
        )
        assert subject is not None
        # 内容类型推断
        assert rtype == "documentation"


class TestTaxonomyStandardizerDeprecation:
    """测试 TaxonomyStandardizer 废弃警告"""

    def test_import_shows_deprecation_warning(self):
        """导入时显示废弃警告"""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # 强制重新导入以触发警告
            import importlib
            import src.utils.standardizer
            importlib.reload(src.utils.standardizer)
            # 检查是否有废弃警告
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) >= 1
            assert "TaxonomyStandardizer" in str(deprecation_warnings[0].message)

    def test_taxonomystandardizer_is_taxonomyservice(self):
        """TaxonomyStandardizer 是 TaxonomyService 的别名"""
        from src.utils.standardizer import TaxonomyStandardizer
        from src.services.taxonomy_service import TaxonomyService

        # 检查它们是同一个类
        assert TaxonomyStandardizer is TaxonomyService


class TestTaxonomyServiceBackwardCompatibility:
    """测试向后兼容性"""

    def test_old_import_still_works(self):
        """旧的导入路径仍然工作"""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from src.utils.standardizer import TaxonomyStandardizer

            # 可以实例化
            service = TaxonomyStandardizer()
            assert service is not None

            # 有必要的方法
            assert hasattr(service, "normalize_subject")
            assert hasattr(service, "normalize_resource_type")
            assert hasattr(service, "derive_from_category")
