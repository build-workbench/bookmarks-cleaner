"""
Taxonomy Standardizer - 分类标准化器

注意: 此模块已废弃，请使用 src.services.taxonomy_service.TaxonomyService。
TaxonomyService 现在包含所有标准化方法。

此模块仅为向后兼容保留，将在未来版本中移除。
"""

import warnings

# 发出废弃警告
warnings.warn(
    "TaxonomyStandardizer 已废弃，请使用 src.services.taxonomy_service.TaxonomyService。"
    "此模块将在未来版本中移除。",
    DeprecationWarning,
    stacklevel=2,
)

# 为向后兼容，从 TaxonomyService 重新导出
from src.services.taxonomy_service import TaxonomyService as TaxonomyStandardizer

__all__ = ["TaxonomyStandardizer"]
