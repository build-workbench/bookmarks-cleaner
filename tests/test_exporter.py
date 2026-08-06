"""导出器测试"""

import json
import os
from cleanbook.exporter import DataExporter


class TestDataExporter:
    def _make_bookmarks(self):
        return {
            "编程": {
                "_items": [
                    {"url": "https://github.com/user/repo", "title": "My Repo", "confidence": 0.9, "add_date": ""},
                ],
                "_subcategories": {
                    "code_repository": {
                        "_items": [
                            {"url": "https://gitlab.com/user/proj", "title": "GitLab Proj", "confidence": 0.85, "add_date": ""},
                        ]
                    }
                }
            }
        }

    def test_export_html(self, tmp_path):
        exporter = DataExporter()
        out = tmp_path / "test.html"
        exporter.export_html(self._make_bookmarks(), str(out))
        content = out.read_text(encoding="utf-8")
        assert "DOCTYPE NETSCAPE-Bookmark" in content
        assert "My Repo" in content
        assert "GitLab Proj" in content

    def test_export_json(self, tmp_path):
        exporter = DataExporter()
        out = tmp_path / "test.json"
        exporter.export_json(self._make_bookmarks(), str(out))
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "metadata" in data
        assert "bookmarks" in data
        assert "编程" in data["bookmarks"]

    def test_export_markdown(self, tmp_path):
        exporter = DataExporter()
        out = tmp_path / "test.md"
        exporter.export_markdown(self._make_bookmarks(), str(out))
        content = out.read_text(encoding="utf-8")
        assert "My Repo" in content
        assert "GitLab Proj" in content

    def test_export_all_formats(self, tmp_path):
        exporter = DataExporter()
        files = exporter.export_all_formats(self._make_bookmarks(), str(tmp_path))
        assert len(files) == 3
        for f in files:
            assert os.path.exists(f)

    def test_empty_categories_skipped(self, tmp_path):
        exporter = DataExporter()
        data = {"空分类": {"_items": [], "_subcategories": {}}}
        out = tmp_path / "test.html"
        exporter.export_html(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert "空分类" not in content
