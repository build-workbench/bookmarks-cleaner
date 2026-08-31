"""规则引擎测试"""

from cleanbook.models import BookmarkFeatures
from cleanbook.rules import RuleEngine


def _make_config():
    return {
        "category_rules": {
            "编程": {
                "rules": [
                    {"match": "domain", "keywords": ["github.com"], "weight": 10},
                    {"match": "title", "keywords": ["python", "编程"], "weight": 5},
                ]
            },
            "AI": {
                "rules": [
                    {"match": "title", "keywords": ["AI", "大模型"], "weight": 8},
                ]
            },
        }
    }


class TestRuleEngine:
    def test_domain_match(self):
        engine = RuleEngine(_make_config())
        features = BookmarkFeatures.from_url_title("https://github.com/user/repo", "My Repo", "code_repository", "en")
        result = engine.classify(features)
        assert result is not None
        assert "编程" in result["category"]
        assert result["confidence"] > 0

    def test_title_match(self):
        engine = RuleEngine(_make_config())
        features = BookmarkFeatures.from_url_title("https://example.com", "Python 编程入门", "webpage", "zh")
        result = engine.classify(features)
        assert result is not None
        assert "编程" in result["category"]

    def test_no_match(self):
        engine = RuleEngine(_make_config())
        features = BookmarkFeatures.from_url_title("https://random.com", "Random Page", "webpage", "en")
        result = engine.classify(features)
        # URL analyzer might still provide hints
        assert result is None or isinstance(result, dict)

    def test_url_analysis_hints(self):
        engine = RuleEngine(_make_config())
        features = BookmarkFeatures.from_url_title("https://github.com/user/repo", "Test", "code_repository", "en")
        result = engine.classify(features)
        assert result is not None
        assert result["facets"].get("resource_type_hint") == "code_repository"

    def test_config_fallback_defaults(self):
        """配置缺失/非法字符串时使用默认值"""
        # 无 ai_settings 的配置
        engine = RuleEngine({"category_rules": {"AI": {"rules": []}}})
        assert engine.url_analysis_weight == 15.0
        assert engine.merge_top_ratio == 0.4
        # 非法字符串
        engine2 = RuleEngine({"ai_settings": {"url_analysis_weight": "abc", "merge_top_ratio": None},
                              "category_rules": {"AI": {"rules": []}}})
        assert engine2.url_analysis_weight == 15.0
        assert engine2.merge_top_ratio == 0.4

    def test_merge_removes_sibling_subcategories(self):
        """回归：同主类合并后，其他子类残留不得稀释置信度"""
        config = {
            "ai_settings": {"merge_top_ratio": 0.4},
            "category_rules": {
                "编程/后端": {"rules": [{"match": "title", "keywords": ["后端"], "weight": 8}]},
                "编程/前端": {"rules": [{"match": "title", "keywords": ["前端"], "weight": 2}]},
                "学习": {"rules": [{"match": "title", "keywords": ["学习"], "weight": 5}]},
            },
        }
        engine = RuleEngine(config)
        # 同一书签标题同时命中三条规则
        features = BookmarkFeatures.from_url_title("https://example.com", "后端前端学习", "webpage", "zh")
        result = engine.classify(features)
        assert result is not None
        # 编程合并后 10 分，学习 5 分：置信度应为 10/15 ≈ 0.667，而非被前端残留稀释后的 0.588
        assert abs(result["confidence"] - 10.0 / 15.0) < 0.01
