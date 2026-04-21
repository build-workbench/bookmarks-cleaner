#!/usr/bin/env python3
"""
自动更新项目中的导入路径
"""

import os
import re
from pathlib import Path

# 导入映射表：旧模块名 -> 新导入路径
IMPORT_MAP = {
    # 分类器
    "ai_classifier": ("src.classifiers.ai", "AIBookmarkClassifier"),
    "ml_classifier": ("src.classifiers.ml", "MLClassifier"),
    "llm_classifier": ("src.classifiers.llm", "LLMClassifier"),
    "enhanced_classifier": ("src.classifiers.enhanced", "EnhancedClassifier"),
    # 引擎
    "rule_engine": ("src.engines.rules", "RuleEngine"),
    "semantic_analyzer": ("src.engines.semantic", "SemanticAnalyzer"),
    "url_analyzer": ("src.engines.url", "URLAnalyzer"),
    "smart_rule_loader": ("src.engines.smart_loader", "SmartRuleLoader"),
    # LLM
    "llm_organizer": ("src.llm.organizer", "LLMBookmarkOrganizer"),
    "llm_prompt_builder": ("src.llm.prompt_builder", "LLMPromptBuilder"),
    "llm_second_pass_prompt": ("src.llm.second_pass", "SecondPassPrompt"),
    "export_llm_prompt": ("src.llm.exporter", "PromptExporter"),
    # 健康检查
    "health_checker": ("src.health.checker", "HealthChecker"),
    "bookmark_health_checker": ("src.health.bookmark_checker", "BookmarkHealthChecker"),
    # 数据
    "data_exporter": ("src.data.exporter", "DataExporter"),
    "deduplicator": ("src.data.deduplicator", "BookmarkDeduplicator"),
    # 工具
    "config_manager": ("src.utils.config", "ConfigManager"),
    "category_utils": ("src.utils.category", "CategoryUtils"),
    "url_analyzer_old": ("src.utils.url", "URLAnalyzer"),
    "resource_loader": ("src.utils.resource_loader", None),
    "emoji_cleaner": ("src.utils.emoji_cleaner", None),
    "taxonomy_standardizer": ("src.utils.standardizer", "TaxonomyStandardizer"),
    "user_profiler": ("src.utils.profiler", "UserProfiler"),
    "advanced_features": ("src.utils.advanced", "AdvancedFeatures"),
    "performance_optimizer": ("src.utils.optimizer", "PerformanceOptimizer"),
    "placeholder_modules": ("src.utils.placeholders", None),
    "enhanced_clean_tidy": ("src.utils.clean_tidy", "EnhancedCleanTidy"),
    # 核心
    "bookmark_processor": ("src.core.processor", "BookmarkProcessor"),
    "data_exporter_old": ("src.core.exporter", "DataExporter"),
    "deduplicator_old": ("src.core.deduplicator", "BookmarkDeduplicator"),
    # CLI
    "cli_interface": ("src.cli.interface", "CLIInterface"),
    "enhanced_cli": ("src.cli.enhanced", "EnhancedCLI"),
}


def update_file_imports(filepath):
    """更新单个文件的导入"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 替换 from .xxx import 模式
    for old_mod, (new_mod, _) in IMPORT_MAP.items():
        # from .xxx import
        pattern = rf"from \.{old_mod} import"
        replacement = f"from {new_mod} import"
        content = re.sub(pattern, replacement, content)

        # import .xxx
        pattern = rf"import \.{old_mod}"
        replacement = f"import {new_mod}"
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    src_dir = Path("/home/shane/dev/bookmarks-cleaner/src")

    # 更新所有 Python 文件
    updated = 0
    for pyfile in src_dir.rglob("*.py"):
        if pyfile.name == "update_imports.py":
            continue
        if update_file_imports(pyfile):
            print(f"Updated: {pyfile.relative_to(src_dir.parent)}")
            updated += 1

    print(f"\nTotal files updated: {updated}")


if __name__ == "__main__":
    main()
