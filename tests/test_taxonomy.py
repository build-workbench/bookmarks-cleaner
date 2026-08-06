"""分类法服务测试"""

from cleanbook.taxonomy import TaxonomyService


class TestTaxonomyService:
    def test_normalize_subject(self):
        ts = TaxonomyService()
        assert ts.normalize_subject("AI") == "人工智能"
        assert ts.normalize_subject("大模型") == "人工智能"
        assert ts.normalize_subject("编程开发") == "编程"
        assert ts.normalize_subject("unknown") == "unknown"

    def test_normalize_resource_type(self):
        ts = TaxonomyService()
        assert ts.normalize_resource_type("代码仓库") == "code_repository"
        assert ts.normalize_resource_type("github") == "code_repository"
        assert ts.normalize_resource_type("视频") == "video"

    def test_derive_from_category(self):
        ts = TaxonomyService()
        subject, rt = ts.derive_from_category("编程/代码仓库")
        assert subject == "编程"
        assert rt == "code_repository"

    def test_derive_from_category_no_slash(self):
        ts = TaxonomyService()
        subject, rt = ts.derive_from_category("编程")
        assert subject == "编程"
        assert rt is None

    def test_derive_with_content_type(self):
        ts = TaxonomyService()
        subject, rt = ts.derive_from_category("学习", content_type="video")
        assert subject == "学习"
        assert rt == "video"

    def test_empty(self):
        ts = TaxonomyService()
        assert ts.normalize_subject("") is None
        subject, rt = ts.derive_from_category("")
        assert subject is None
        assert rt is None
