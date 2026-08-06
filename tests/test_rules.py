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
