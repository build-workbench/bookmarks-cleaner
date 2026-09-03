"""组织与排序管道测试"""

from cleanbookmarks.config import load_json_config
from cleanbookmarks.organizer import OrganizationPipeline
from cleanbookmarks.taxonomy import TaxonomyService
from cleanbookmarks.text_utils import normalize_category_config


def _make_pipeline():
    config, _, _ = load_json_config(None)
    config = normalize_category_config(config)
    return OrganizationPipeline(TaxonomyService(config)), config


def _bookmark(url="https://example.com", title="示例", category="编程", subcategory=None,
              confidence=0.9, facets=None):
    b = {
        "url": url, "title": title, "category": category, "subcategory": subcategory,
        "confidence": confidence, "facets": facets or {},
    }
    return b


class TestOrganizeEmpty:
    def test_empty_list(self):
        pipeline, config = _make_pipeline()
        organized, stats = pipeline.organize([], config)
        assert organized == {}
        assert stats["total_bookmarks"] == 0

    def test_none_and_junk_entries_skipped(self):
        """防御：分类结果混入 None/非 dict 不应崩溃，应跳过"""
        pipeline, config = _make_pipeline()
        bookmarks = [None, "junk", 42, _bookmark(category="编程")]
        organized, stats = pipeline.organize(bookmarks, config)
        assert stats["total_bookmarks"] == 1
        assert organized


class TestOrganizeBasic:
    def test_single_bookmark_subject(self):
        pipeline, config = _make_pipeline()
        b = _bookmark(category="编程", title="GitHub 仓库")
        organized, stats = pipeline.organize([b], config)
        assert stats["total_bookmarks"] == 1
        assert stats["total_subjects"] == 1
        # 编程 是 subjects.yaml 的首选词
        assert "编程" in organized
        assert len(organized["编程"]["_items"]) == 1

    def test_uncategorized_goes_to_other(self):
        pipeline, config = _make_pipeline()
        b = _bookmark(category="", title="杂项")
        organized, stats = pipeline.organize([b], config)
        assert stats["total_bookmarks"] == 1
        assert len(organized) == 1

    def test_missing_category_uses_other(self):
        """bookmark 缺 category 键 -> 归入默认 其他"""
        pipeline, config = _make_pipeline()
        b = {"url": "https://x.com", "title": "X", "confidence": 0.8}
        organized, stats = pipeline.organize([b], config)
        assert stats["total_bookmarks"] == 1
        # 主题要么是 其他，要么只有一个主题桶
        assert len(organized) == 1

    def test_subcategory_becomes_resource_type(self):
        pipeline, config = _make_pipeline()
        # category 形如 主类/子类，子类应被标准化为 resource_type
        b = _bookmark(category="编程/技术文档", subcategory="文档资料")
        organized, _ = pipeline.organize([b], config)
        assert len(organized) == 1
        # 技术文档 的 resource_type 标准化为 documentation
        subcats = next(iter(organized.values()))["_subcategories"]
        assert subcats
        assert any(k == "documentation" for k in subcats)

    def test_mixed_subject_and_subcategory(self):
        pipeline, config = _make_pipeline()
        b1 = _bookmark(category="编程", title="A")
        b2 = _bookmark(category="编程/技术文档", title="B")
        organized, stats = pipeline.organize([b1, b2], config)
        assert stats["total_bookmarks"] == 2
        assert stats["total_subjects"] == 1
        subject_data = organized["编程"]
        assert len(subject_data["_items"]) == 1  # A 在主体
        assert "documentation" in subject_data["_subcategories"]  # B 在子类


class TestSorting:
    def test_items_sorted_by_confidence_desc(self):
        pipeline, config = _make_pipeline()
        b1 = _bookmark(category="编程", title="low", confidence=0.3)
        b2 = _bookmark(category="编程", title="high", confidence=0.95)
        organized, _ = pipeline.organize([b1, b2], config)
        items = organized["编程"]["_items"]
        assert [i["title"] for i in items] == ["high", "low"]

    def test_subcategories_sorted_by_count_desc(self):
        pipeline, config = _make_pipeline()
        b1 = _bookmark(category="编程/技术文档", title="D1")
        b2 = _bookmark(category="编程/技术文档", title="D2")
        b3 = _bookmark(category="编程/代码仓库", title="R1")
        organized, _ = pipeline.organize([b1, b2, b3], config)
        subcats = list(organized["编程"]["_subcategories"].keys())
        assert len(subcats) == 2
        # documentation 有 2 条 > code_repository 1 条
        assert subcats[0] == "documentation"

    def test_subject_order_respects_category_order(self):
        """category_order 中的主体应排在前面"""
        pipeline, config = _make_pipeline()
        b1 = _bookmark(category="娱乐", title="Video")
        b2 = _bookmark(category="编程", title="Code")
        b3 = _bookmark(category="学习", title="Learn")
        organized, _ = pipeline.organize([b1, b2, b3], config)
        keys = list(organized.keys())
        # 编程/学习/娱乐 都在 category_order 里，按配置顺序：AI, 编程, 生物, 学习, ... 娱乐
        assert keys.index("编程") < keys.index("娱乐")
        assert keys.index("学习") < keys.index("娱乐")


class TestStats:
    def test_stats_are_reset_between_calls(self):
        pipeline, config = _make_pipeline()
        pipeline.organize([_bookmark(category="编程")], config)
        pipeline.organize([], config)
        assert pipeline.stats["total_bookmarks"] == 0
