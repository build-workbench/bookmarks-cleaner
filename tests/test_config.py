"""配置加载测试"""

from pathlib import Path

import pytest

from cleanbookmarks.config import (
    ResourceResolutionError,
    apply_category_updates,
    backup_config_file,
    load_json_config,
    resolve_config_path,
    write_json_config_file,
)


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


class TestPackagedResources:
    def test_packaged_path_returns_usable_file(self):
        """回归：_packaged_path 返回的路径在 as_file 上下文退出后仍可读取"""
        from cleanbookmarks.config import _packaged_path
        path = _packaged_path("config.json")
        if path is None:
            import pytest as _pytest
            _pytest.skip("packaged resources 不可用")
        # 返回的路径必须是长期有效、可读的真实文件（而非已释放的临时路径）
        assert path.is_file()
        content = path.read_text(encoding="utf-8")
        assert "category_rules" in content

    def test_packaged_taxonomy_file(self):
        from cleanbookmarks.config import _packaged_path
        path = _packaged_path("taxonomy", "subjects.yaml")
        if path is None:
            import pytest as _pytest
            _pytest.skip("packaged resources 不可用")
        assert path.is_file()


class TestApplyCategoryUpdates:
    def _base_config(self):
        return {
            "category_order": ["AI", "编程"],
            "category_rules": {
                "AI": {"rules": [{"match": "domain", "keywords": ["openai.com"], "weight": 1.0}]},
                "编程": {"rules": [{"match": "domain", "keywords": ["github.com"], "weight": 1.0}]},
            },
        }

    def test_add_keywords_to_existing_category(self):
        cfg = self._base_config()
        result = apply_category_updates(cfg, {
            "category_updates": [{"category": "AI", "add_keywords": ["claude", "anthropic"]}],
        })
        kws = [kw for rule in result["category_rules"]["AI"]["rules"] for kw in rule["keywords"]]
        assert "claude" in kws
        assert "anthropic" in kws
        # 原有关键词不被删除
        assert "openai.com" in kws
        # 类目顺序不变
        assert result["category_order"] == ["AI", "编程"]

    def test_deduplicates_existing_keywords(self):
        cfg = self._base_config()
        result = apply_category_updates(cfg, {
            "category_updates": [{"category": "AI", "add_keywords": ["openai.com"]}],
        })
        kws = [kw for rule in result["category_rules"]["AI"]["rules"] for kw in rule["keywords"]]
        assert kws.count("openai.com") == 1

    def test_add_category_appends_to_order(self):
        cfg = self._base_config()
        result = apply_category_updates(cfg, {
            "add_categories": [{"category": "设计", "keywords": ["figma", "dribbble"]}],
        })
        assert "设计" in result["category_rules"]
        assert result["category_order"] == ["AI", "编程", "设计"]

    def test_unknown_update_category_becomes_new(self):
        cfg = self._base_config()
        result = apply_category_updates(cfg, {
            "category_updates": [{"category": "新类", "add_keywords": ["x.com"]}],
        })
        assert "新类" in result["category_rules"]
        assert "新类" in result["category_order"]

    def test_junk_updates_ignored(self):
        cfg = self._base_config()
        result = apply_category_updates(cfg, {
            "category_updates": ["junk", None, {"category": ""}],
            "add_categories": [None, {"keywords": ["no-name"]}],
        })
        assert result["category_rules"] == cfg["category_rules"]

    def test_no_mutation_of_input(self):
        """纯函数：传入的 config 不被修改"""
        cfg = self._base_config()
        import copy
        snapshot = copy.deepcopy(cfg)
        apply_category_updates(cfg, {
            "add_categories": [{"category": "设计", "keywords": ["figma"]}],
        })
        assert cfg == snapshot


class TestConfigFileIO:
    def test_write_and_read_roundtrip(self, tmp_path):
        cfg_path = tmp_path / "cfg.json"
        data = {"a": 1, "nested": {"b": [1, 2]}, "中文": "值"}
        write_json_config_file(cfg_path, data)
        from cleanbookmarks.config import read_json_config_file
        assert read_json_config_file(cfg_path) == data

    def test_backup_creates_copy(self, tmp_path):
        cfg_path = tmp_path / "cfg.json"
        cfg_path.write_text('{"k": "v"}', encoding="utf-8")
        backup = backup_config_file(cfg_path)
        assert backup is not None
        assert backup.exists()
        assert backup.read_text(encoding="utf-8") == '{"k": "v"}'
        assert backup.name.startswith("cfg.llm-backup-")

    def test_backup_keeps_only_recent(self, tmp_path):
        cfg_path = tmp_path / "cfg.json"
        cfg_path.write_text('{"k": "v"}', encoding="utf-8")
        for _ in range(7):
            backup_config_file(cfg_path)
        backups = sorted(tmp_path.glob("cfg.llm-backup-*.json"))
        assert len(backups) == 5  # keep=5

    def test_backup_missing_file_returns_none(self, tmp_path):
        assert backup_config_file(tmp_path / "nope.json") is None
