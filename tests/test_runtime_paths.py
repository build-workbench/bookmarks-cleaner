"""运行时路径解析测试"""

from cleanbook.config import resolve_config_path, resolve_taxonomy_path, load_json_config


class TestRuntimePaths:
    def test_config_resolvable(self):
        path, _ = resolve_config_path(None)
        assert path.is_file()

    def test_config_loadable(self):
        config, path, explicit = load_json_config(None)
        assert isinstance(config, dict)
        assert "category_rules" in config

    def test_taxonomy_subjects_resolvable(self):
        config, _, _ = load_json_config(None)
        path = resolve_taxonomy_path(config, "subjects_file", "taxonomy/subjects.yaml")
        assert path.is_file()

    def test_taxonomy_resource_types_resolvable(self):
        config, _, _ = load_json_config(None)
        path = resolve_taxonomy_path(config, "resource_types_file", "taxonomy/resource_types.yaml")
        assert path.is_file()

    def test_explicit_config_path(self):
        import tempfile, json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test": True}, f)
            f.flush()
            path, explicit = resolve_config_path(f.name)
            assert explicit is True
            assert path.is_file()
