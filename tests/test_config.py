"""配置加载测试"""

from cleanbook.config import resolve_config_path, load_json_config, ResourceResolutionError
from pathlib import Path
import pytest


class TestResolveConfigPath:
    def test_default_config(self):
        path, explicit = resolve_config_path(None)
        assert path.is_file()
        assert explicit is False

    def test_explicit_config(self, tmp_path):
        config_file = tmp_path / "test.json"
        config_file.write_text('{"test": true}')
        path, explicit = resolve_config_path(str(config_file))
        assert explicit is True
        assert path == config_file.resolve()

    def test_nonexistent_config(self):
        with pytest.raises(FileNotFoundError):
            resolve_config_path("/nonexistent/path/config.json")


class TestLoadJsonConfig:
    def test_load_default(self):
        config, path, explicit = load_json_config(None)
        assert isinstance(config, dict)
        assert "category_rules" in config
        assert "ai_settings" in config

    def test_load_explicit(self, tmp_path):
        config_file = tmp_path / "test.json"
        config_file.write_text('{"key": "value"}')
        config, path, explicit = load_json_config(str(config_file))
        assert config == {"key": "value"}
        assert explicit is True

    def test_invalid_json(self, tmp_path):
        config_file = tmp_path / "bad.json"
        config_file.write_text("not json")
        with pytest.raises(ValueError):
            load_json_config(str(config_file))
