"""分类器级联逻辑测试：规则优先，LLM 兜底与补充"""

from cleanbook.classifier import BookmarkClassifier


def _make_config():
    return {
        "ai_settings": {"confidence_threshold": 0.7},
        "category_rules": {
            "编程": {
                "rules": [
                    {"match": "domain", "keywords": ["github.com"], "weight": 10},
                ]
            },
        },
    }


class _FakeLLM:
    """模拟启用的 LLM 分类器"""

    def enabled(self):
        return True

    def classify(self, url, title, context=None):
        return {
            "category": "学习",
            "confidence": 0.9,
            "reasoning": ["LLM 推断"],
            "method": "llm",
            "subcategory": "技术文档",
            "facets": {"priority": "high"},
        }


class TestClassifierCascade:
    def setup_method(self):
        self.classifier = BookmarkClassifier(config=_make_config())

    def test_rule_priority(self):
        """规则命中时采用规则主分类，即使 LLM 给出不同意见"""
        self.classifier._llm_classifier = _FakeLLM()
        result = self.classifier.classify("https://github.com/user/repo", "My Repo")
        assert "编程" in result.category
        assert "rule_engine" in result.method

    def test_llm_fallback(self):
        """规则未命中时由 LLM 兜底"""
        self.classifier._llm_classifier = _FakeLLM()
        result = self.classifier.classify("https://random.example.com", "Random Page")
        assert result.category == "学习"
        assert result.method == "llm"

    def test_fallback_no_llm(self):
        """规则未命中且 LLM 不可用 -> 未分类"""
        result = self.classifier.classify("https://random.example.com", "Random Page")
        assert result.category == "未分类"
        assert result.method == "fallback"

    def test_llm_subcategory_supplement(self):
        """规则命中主分类后，LLM 补充子分类与 facets"""
        self.classifier._llm_classifier = _FakeLLM()
        result = self.classifier.classify("https://github.com/user/repo", "My Repo")
        assert result.subcategory == "技术文档"
        assert result.facets.get("priority") == "high"

    def test_hierarchy_subcategory(self):
        """规则命中后按 category_hierarchy 标题匹配补充子分类"""
        config = {
            "ai_settings": {"confidence_threshold": 0.7},
            "category_hierarchy": {"编程": ["Python", "Rust"]},
            "category_rules": {
                "编程": {"rules": [{"match": "domain", "keywords": ["github.com"], "weight": 10}]},
            },
        }
        classifier = BookmarkClassifier(config=config)
        result = classifier.classify("https://github.com/user/repo", "Python 项目")
        assert result.subcategory == "Python"

    def test_llm_malformed_facets_does_not_crash(self):
        """回归：LLM 返回非 dict facets（列表/字符串）不得崩溃"""
        class _BadFacetsLLM:
            def enabled(self):
                return True

            def classify(self, url, title, context=None):
                return {
                    "category": "学习",
                    "confidence": 0.9,
                    "method": "llm",
                    "facets": ["教程"],  # 非法类型
                }

        self.classifier._llm_classifier = _BadFacetsLLM()
        result = self.classifier.classify("https://random.example.com", "Random Page")
        assert result.category == "学习"
        assert result.facets == {}

    def test_cache_hit_rate_ratio(self):
        """回归：命中率 = 命中/(命中+未命中)，不得因分母只计 miss 而超 100%"""
        classifier = BookmarkClassifier(config=_make_config())
        for _ in range(10):
            classifier.classify("https://github.com/user/repo", "My Repo")
        stats = classifier.get_statistics()
        assert stats["total_classified"] == 1
        assert stats["cache_hits"] == 9
        assert abs(stats["cache_hit_rate"] - 0.9) < 0.001

    def test_low_confidence_marks_unclassified(self):
        """多规则冲突导致置信度低于阈值 -> 未分类"""
        config = {
            "ai_settings": {"confidence_threshold": 0.7},
            "category_rules": {
                "编程": {"rules": [{"match": "title", "keywords": ["python"], "weight": 1}]},
                "学习": {"rules": [{"match": "title", "keywords": ["python"], "weight": 1}]},
                "AI": {"rules": [{"match": "title", "keywords": ["python"], "weight": 1}]},
            },
        }
        classifier = BookmarkClassifier(config=config)
        result = classifier.classify("https://example.com", "Python 教程")
        assert result.category == "未分类"
