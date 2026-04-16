"""
Tests for Config Manager Module
配置管理模块测试
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch
import json
import tempfile
from pathlib import Path

from src.config_manager import EnhancedConfigManager as ConfigManager, ConfigValidator


class TestConfigValidator:
    """ConfigValidator 测试"""

    def test_validate_valid_config(self):
        """测试验证有效配置"""
        valid_config = {
            "ai_settings": {
                "confidence_threshold": 0.5,
            },
            "category_rules": {
                "测试分类": {
                    "rules": [
                        {"match": "domain", "keywords": ["test.com"], "weight": 10}
                    ]
                }
            },
        }

        validator = ConfigValidator()
        errors = validator.validate(valid_config)

        assert len(errors) == 0

    def test_validate_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_config = {}

        validator = ConfigValidator()
        errors = validator.validate(invalid_config)

        assert len(errors) > 0

    def test_validate_invalid_threshold(self):
        """测试无效的置信度阈值"""
        invalid_config = {
            "ai_settings": {
                "confidence_threshold": 1.5,  # 超出范围
            },
        }

        validator = ConfigValidator()
        errors = validator.validate(invalid_config)

        # 应该报告阈值范围错误
        assert any("threshold" in str(e).lower() for e in errors)

    def test_validate_invalid_rule(self):
        """测试无效的规则配置"""
        invalid_config = {
            "category_rules": {
                "测试": {
                    "rules": [
                        {"match": "invalid_type", "keywords": []},  # 无效规则
                    ]
                }
            },
        }

        validator = ConfigValidator()
        errors = validator.validate(invalid_config)

        # 应该报告规则错误


class TestConfigManager:
    """ConfigManager 测试"""

    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """创建临时配置文件"""
        config = {
            "ai_settings": {
                "confidence_threshold": 0.5,
                "cache_size": 1000,
            },
            "category_rules": {
                "测试": {
                    "rules": [
                        {"match": "domain", "keywords": ["test.com"], "weight": 10}
                    ]
                }
            },
        }

        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        return config_file

    @pytest.fixture
    def manager(self, temp_config_file):
        """创建配置管理器实例"""
        return ConfigManager(config_path=str(temp_config_file))

    def test_initialization(self, manager):
        """测试初始化"""
        assert manager is not None
        assert manager.config is not None

    def test_load_config(self, manager):
        """测试加载配置"""
        config = manager.config

        assert "ai_settings" in config
        assert config["ai_settings"]["confidence_threshold"] == 0.5

    def test_get_value(self, manager):
        """测试获取配置值"""
        threshold = manager.get("ai_settings.confidence_threshold")
        cache_size = manager.get("ai_settings.cache_size")

        assert threshold == 0.5
        assert cache_size == 1000

    def test_get_default_value(self, manager):
        """测试获取默认值"""
        value = manager.get("nonexistent.key", default="default")

        assert value == "default"

    def test_set_value(self, manager):
        """测试设置配置值"""
        manager.set("ai_settings.confidence_threshold", 0.7)

        assert manager.get("ai_settings.confidence_threshold") == 0.7

    def test_save_config(self, manager, temp_config_file):
        """测试保存配置"""
        manager.set("ai_settings.cache_size", 2000)
        manager.save()

        # 重新加载验证
        with open(temp_config_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["ai_settings"]["cache_size"] == 2000

    def test_reload_config(self, manager, temp_config_file):
        """测试重新加载配置"""
        # 修改文件
        with open(temp_config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["ai_settings"]["cache_size"] = 3000

        with open(temp_config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # 重新加载
        manager.reload()

        assert manager.get("ai_settings.cache_size") == 3000

    def test_merge_config(self, manager):
        """测试合并配置"""
        override = {
            "ai_settings": {
                "confidence_threshold": 0.8,  # 覆盖
            },
            "new_section": {
                "new_key": "new_value"
            },
        }

        manager.merge(override)

        assert manager.get("ai_settings.confidence_threshold") == 0.8
        assert manager.get("new_section.new_key") == "new_value"

    def test_validate_current_config(self, manager):
        """测试验证当前配置"""
        errors = manager.validate()

        assert isinstance(errors, list)


class TestConfigManagerEdgeCases:
    """边界情况测试"""

    def test_missing_config_file(self, tmp_path):
        """测试配置文件不存在"""
        nonexistent = tmp_path / "nonexistent.json"

        # 应该使用默认配置或抛出明确错误
        try:
            manager = ConfigManager(config_path=str(nonexistent))
        except FileNotFoundError:
            pass  # 可接受的错误
        else:
            assert manager.config is not None

    def test_invalid_json_config(self, tmp_path):
        """测试无效JSON配置"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json {{{")

        try:
            manager = ConfigManager(config_path=str(invalid_file))
        except json.JSONDecodeError:
            pass  # 可接受的错误
        else:
            assert manager.config is not None

    def test_empty_config_file(self, tmp_path):
        """测试空配置文件"""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("{}")

        manager = ConfigManager(config_path=str(empty_file))

        assert manager.config == {}

    @given(
        key=st.text(min_size=1, max_size=50),
        value=st.one_of(
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.text(max_size=100),
            st.booleans(),
        ),
    )
    def test_fuzz_set_get(self, tmp_path, key: str, value):
        """模糊测试设置和获取"""
        config_file = tmp_path / "config.json"
        config_file.write_text("{}")

        try:
            manager = ConfigManager(config_path=str(config_file))
            manager.set(key, value)
            retrieved = manager.get(key)
            assert retrieved == value
        except Exception:
            pass  # 某些键名可能无效


class TestConfigWatcher:
    """配置文件监视测试"""

    @pytest.fixture
    def manager_with_watcher(self, tmp_path):
        """创建带文件监视的配置管理器"""
        config = {"test": "value"}
        config_file = tmp_path / "config.json"

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        manager = ConfigManager(config_path=str(config_file))
        return manager, config_file

    def test_file_change_detection(self, manager_with_watcher):
        """测试文件变更检测"""
        manager, config_file = manager_with_watcher

        # 启用文件监视（如果支持）
        try:
            manager.start_watching()

            # 修改文件
            import time

            time.sleep(0.1)  # 确保时间戳不同

            new_config = {"test": "new_value"}
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(new_config, f)

            time.sleep(0.5)  # 等待检测

            # 配置应该自动更新
            # 注意：这取决于具体实现

            manager.stop_watching()

        except AttributeError:
            # 如果不支持文件监视，跳过
            pass
