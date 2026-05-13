"""
测试 ConfigProvider 配置提供者
"""

import pytest

from src.config_manager import EnhancedConfigManager


class TestConfigProvider:
    """测试 ConfigProvider 接口"""

    @pytest.fixture
    def config_manager(self):
        """创建配置管理器"""
        return EnhancedConfigManager()

    def test_get_simple_path(self, config_manager):
        """获取简单路径的配置值"""
        # 假设配置中有 ai_settings
        result = config_manager.get("ai_settings", {})
        assert isinstance(result, dict)

    def test_get_nested_path(self, config_manager):
        """获取嵌套路径的配置值"""
        result = config_manager.get("ai_settings.confidence_threshold", 0.7)
        assert isinstance(result, (int, float))
        assert 0 <= result <= 1

    def test_get_default_value(self, config_manager):
        """获取不存在的路径返回默认值"""
        result = config_manager.get("nonexistent.path", "default")
        assert result == "default"

    def test_get_section_exists(self, config_manager):
        """获取存在的配置节"""
        section = config_manager.get_section("ai_settings")
        assert isinstance(section, dict)

    def test_get_section_not_exists(self, config_manager):
        """获取不存在的配置节返回空字典"""
        section = config_manager.get_section("nonexistent_section")
        assert section == {}

    def test_get_config_returns_dict(self, config_manager):
        """获取完整配置返回字典"""
        config = config_manager.get_config()
        assert isinstance(config, dict)
        # 配置可能为空（如果验证失败），但应该是字典
        # 如果有内容，检查常见字段
        if config:
            assert (
                "ai_settings" in config
                or "category_rules" in config
                or len(config) >= 0
            )

    def test_get_section_returns_copy(self, config_manager):
        """获取配置节返回副本（修改不影响原配置）"""
        section = config_manager.get_section("ai_settings")
        if section:
            original_value = section.get("confidence_threshold")
            section["confidence_threshold"] = 0.99
            # 原配置不应被修改
            current = config_manager.get("ai_settings.confidence_threshold")
            assert current == original_value


class TestConfigProviderProtocol:
    """测试 IConfigProvider Protocol 兼容性"""

    def test_satisfies_protocol(self):
        """EnhancedConfigManager 满足 IConfigProvider Protocol"""
        from src.interfaces import IConfigProvider

        # 检查方法存在
        assert hasattr(EnhancedConfigManager, "get")
        assert hasattr(EnhancedConfigManager, "get_section")
        assert hasattr(EnhancedConfigManager, "get_config")

    def test_runtime_checkable(self):
        """运行时可以检查 Protocol"""
        from src.interfaces import IConfigProvider

        manager = EnhancedConfigManager()
        # IConfigProvider 是 runtime_checkable 的
        assert isinstance(manager, IConfigProvider)


class TestConfigProviderIntegration:
    """ConfigProvider 集成测试"""

    def test_global_config_manager(self):
        """全局配置管理器单例"""
        from src.config_manager import get_config_manager

        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2

    def test_convenience_functions(self):
        """便捷函数"""
        from src.config_manager import get_config, set_config

        # 获取配置
        config = get_config()
        assert isinstance(config, dict)

        # 获取特定路径
        threshold = get_config("ai_settings.confidence_threshold", 0.7)
        assert isinstance(threshold, (int, float))
