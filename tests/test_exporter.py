"""导出器测试"""

import json
import os
from cleanbookmarks.exporter import DataExporter


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

    def test_batch_timestamps_consistent(self, tmp_path):
        """回归：同一批次导出的三格式时间戳一致，且文件名含同一批次时刻"""
        import json as _json
        exporter = DataExporter()
        files = exporter.export_all_formats(self._make_bookmarks(), str(tmp_path))
        # 文件名共享同一时间戳前缀
        basenames = [os.path.basename(f) for f in files]
        prefixes = {b.rsplit(".", 1)[0].rsplit("_", 1)[0] for b in basenames}
        assert len(prefixes) == 1, f"文件名时间戳不一致: {basenames}"
        # Markdown 与 JSON 内容里的时间戳一致
        md = open(files[2], encoding="utf-8").read()
        import re as _re
        md_time = _re.search(r"生成时间: (.+)", md).group(1).strip()
        data = _json.load(open(files[1], encoding="utf-8"))
        assert data["metadata"]["export_time"] == md_time, (
            f"内容时间戳不一致: {data['metadata']['export_time']} vs {md_time}"
        )

    def test_empty_categories_skipped(self, tmp_path):
        exporter = DataExporter()
        data = {"空分类": {"_items": [], "_subcategories": {}}}
        out = tmp_path / "test.html"
        exporter.export_html(data, str(out))
        content = out.read_text(encoding="utf-8")
        assert "空分类" not in content
