"""
Category Utilities - 分类名称规范化工具

提供分类名称前缀清理、规范化等共享函数，
消除 ai_classifier.py 与 bookmark_processor.py 之间的重复代码。

注意：此模块现在使用 TextCleaner 实现，保持向后兼容。
"""

from typing import Dict

# 从 TextCleaner 导入实现
from src.utils.text_cleaner import TextCleaner, strip_prefix

# 创建默认实例
_default_cleaner = TextCleaner()


def strip_category_prefix(text: str) -> str:
    """移除分类名称中的 emoji 等非文字前缀，保留中文/字母/数字起始的内容。"""
    return _default_cleaner.strip_prefix(text)


def normalize_category_string(category: str) -> str:
    """规范化单个分类字符串（支持 '主类/子类' 格式）。"""
    if not category:
        return ""
    cat = str(category).strip()
    if not cat:
        return ""
    if "/" in cat:
        main, sub = cat.split("/", 1)
        main_n = strip_category_prefix(main)
        sub_n = strip_category_prefix(sub)
        return f"{main_n}/{sub_n}" if sub_n else main_n
    return strip_category_prefix(cat)


def normalize_category_config(config: Dict) -> Dict:
    """规范化配置字典中所有分类相关的键名（category_order / domain_grouping_rules / priority_rules / category_rules）。"""
    if not isinstance(config, dict):
        return {}

    normalized = dict(config)

    order = normalized.get("category_order")
    if isinstance(order, list):
        normalized["category_order"] = [
            strip_category_prefix(x) for x in order if str(x).strip()
        ]

    dgr = normalized.get("domain_grouping_rules")
    if isinstance(dgr, dict):
        new_dgr: Dict = {}
        for k, v in dgr.items():
            nk = strip_category_prefix(k)
            if not nk:
                continue
            if nk in new_dgr and isinstance(new_dgr[nk], list) and isinstance(v, list):
                new_dgr[nk].extend(v)
            else:
                new_dgr[nk] = v
        normalized["domain_grouping_rules"] = new_dgr

    pr = normalized.get("priority_rules")
    if isinstance(pr, dict):
        new_pr = {}
        for k, v in pr.items():
            nk = normalize_category_string(k)
            if not nk:
                continue
            new_pr[nk] = v
        normalized["priority_rules"] = new_pr

    cr = normalized.get("category_rules")
    if isinstance(cr, dict):
        new_cr = {}
        for k, v in cr.items():
            nk = normalize_category_string(k)
            if not nk:
                continue
            new_cr[nk] = v
        normalized["category_rules"] = new_cr

    return normalized
