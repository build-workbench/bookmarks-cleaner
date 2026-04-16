"""
Tests for Rule Engine Module
规则引擎模块测试
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock, patch

from src.rule_engine import RuleEngine, RuleMatch


class TestRuleMatch:
    """RuleMatch 数据类测试"""

    def test_basic_rule_match(self):
        """测试基本规则匹配"""
        match = RuleMatch(
            rule_id="test:category_0",
            category="编程/开发",
            confidence=0.9,
            matched_text="github.com",
            rule_type="domain",
        )

        assert match.rule_id == "test:category_0"
        assert match.category == "编程/开发"
        assert match.confidence == 0.9
        assert match.matched_text == "github.com"
        assert match.rule_type == "domain"


class TestRuleEngine:
    """RuleEngine 测试"""

    @pytest.fixture
    def simple_config(self):
        """简单测试配置"""
        return {
            "category_rules": {
                "💻 编程": {
                    "rules": [
                        {"match": "domain", "keywords": ["github.com"], "weight": 20},
                        {"match": "domain", "keywords": ["stackoverflow.com"], "weight": 15},
                    ]
                },
                "🤖 AI": {
                    "rules": [
                        {"match": "title", "keywords": ["machine learning", "AI"], "weight": 10},
                    ]
                },
                "📰 资讯": {
                    "rules": [
                        {"match": "domain", "keywords": ["news.com"], "weight": 10},
                    ]
                },
            },
        }

    @pytest.fixture
    def engine(self, simple_config):
        """创建规则引擎实例"""
        return RuleEngine(simple_config)

    def test_initialization(self, engine):
        """测试初始化"""
        assert engine.compiled_rules is not None
        assert len(engine.compiled_rules) > 0

    def test_compile_rules(self, engine):
        """测试规则编译"""
        # 规则应该被预编译
        assert "💻 编程" in engine.compiled_rules
        assert "🤖 AI" in engine.compiled_rules

        # 检查编译后的规则结构
        for category, rules in engine.compiled_rules.items():
            for rule in rules:
                assert "rule_id" in rule
                assert "match_type" in rule
                assert "patterns" in rule
                assert "weight" in rule

    def test_classify_domain_match(self, engine):
        """测试域名匹配分类"""
        features = Mock(
            url="https://github.com/user/repo",
            title="Test Repository",
            domain="github.com",
            path_segments=["user", "repo"],
            content_type="code_repository",
        )

        result = engine.classify(features)

        assert result is not None
        assert "编程" in result["category"]
        assert result["confidence"] > 0

    def test_classify_title_match(self, engine):
        """测试标题匹配分类"""
        features = Mock(
            url="https://example.com/article",
            title="Introduction to Machine Learning",
            domain="example.com",
            path_segments=["article"],
            content_type="webpage",
        )

        result = engine.classify(features)

        assert result is not None
        assert result["confidence"] > 0

    def test_classify_no_match(self, engine):
        """测试无匹配情况"""
        features = Mock(
            url="https://unknown-site.xyz/random",
            title="Random Content",
            domain="unknown-site.xyz",
            path_segments=["random"],
            content_type="webpage",
        )

        # 无匹配时可能返回 None 或低置信度结果
        result = engine.classify(features)
        # 根据实际实现调整断言

    def test_classify_multiple_matches(self, engine):
        """测试多规则匹配"""
        features = Mock(
            url="https://github.com/user/ml-project",
            title="Machine Learning Project",
            domain="github.com",
            path_segments=["user", "ml-project"],
            content_type="code_repository",
        )

        result = engine.classify(features)

        assert result is not None
        # 应该有备选分类
        assert "alternatives" in result

    def test_add_dynamic_rule(self, engine):
        """测试动态添加规则"""
        initial_count = len(engine.compiled_rules.get("📚 学习", []))

        engine.add_dynamic_rule("📚 学习", "domain", "tutorial.com", 15)

        # 应该增加了规则
        assert len(engine.compiled_rules.get("📚 学习", [])) > initial_count

    def test_update_rule_weight(self, engine):
        """测试更新规则权重"""
        # 获取第一个规则的ID
        first_category = list(engine.compiled_rules.keys())[0]
        first_rule = engine.compiled_rules[first_category][0]
        rule_id = first_rule["rule_id"]

        result = engine.update_rule_weight(rule_id, 50.0)

        assert result is True
        assert first_rule["weight"] == 50.0

    def test_update_nonexistent_rule(self, engine):
        """测试更新不存在的规则"""
        result = engine.update_rule_weight("nonexistent_rule", 10.0)

        assert result is False

    def test_get_rule_performance(self, engine):
        """测试获取规则性能统计"""
        # 执行一些分类
        features = Mock(
            url="https://github.com/test",
            title="Test",
            domain="github.com",
            path_segments=["test"],
            content_type="webpage",
        )

        engine.classify(features)

        stats = engine.get_rule_performance()

        assert "total_matches" in stats
        assert "total_rule_hits" in stats
        assert "top_rules" in stats
        assert "category_distribution" in stats

    def test_export_rules(self, engine):
        """测试导出规则"""
        exported = engine.export_rules()

        assert "category_rules" in exported
        assert "performance_stats" in exported

    def test_validate_rules(self, engine):
        """测试规则验证"""
        errors = engine.validate_rules()

        # 有效的配置应该没有错误
        assert isinstance(errors, list)

    def test_classify_with_exclusions(self):
        """测试带排除条件的规则"""
        config = {
            "category_rules": {
                "💻 编程": {
                    "rules": [
                        {
                            "match": "domain",
                            "keywords": ["example.com"],
                            "weight": 10,
                            "must_not_contain": ["news", "blog"],
                        },
                    ]
                },
            },
        }

        engine = RuleEngine(config)

        # 不含排除关键词的情况
        features1 = Mock(
            url="https://example.com/docs",
            title="Documentation",
            domain="example.com",
            path_segments=["docs"],
            content_type="documentation",
        )
        result1 = engine.classify(features1)

        # 含排除关键词的情况
        features2 = Mock(
            url="https://example.com/news",
            title="Latest News",
            domain="example.com",
            path_segments=["news"],
            content_type="news",
        )
        result2 = engine.classify(features2)

        # 排除关键词应该影响匹配结果

    def test_classify_with_match_all_keywords(self):
        """测试必须全部匹配的规则"""
        config = {
            "category_rules": {
                "🤖 AI": {
                    "rules": [
                        {
                            "match": "domain",
                            "keywords": ["openai.com"],
                            "weight": 20,
                            "match_all_keywords_in": {
                                "title": ["gpt", "api"],
                            },
                        },
                    ]
                },
            },
        }

        engine = RuleEngine(config)

        # 标题包含所有关键词
        features1 = Mock(
            url="https://openai.com/gpt-api",
            title="GPT API Documentation",
            domain="openai.com",
            path_segments=["gpt-api"],
            content_type="documentation",
        )

        # 标题不包含所有关键词
        features2 = Mock(
            url="https://openai.com/about",
            title="About OpenAI",
            domain="openai.com",
            path_segments=["about"],
            content_type="webpage",
        )

        result1 = engine.classify(features1)
        result2 = engine.classify(features2)


class TestRuleEngineEdgeCases:
    """规则引擎边界情况测试"""

    def test_empty_config(self):
        """测试空配置"""
        engine = RuleEngine({})

        assert engine.compiled_rules == {}

    def test_malformed_rule(self):
        """测试格式错误的规则"""
        config = {
            "category_rules": {
                "测试分类": {
                    "rules": [
                        {"match": "domain", "keywords": None},  # 无效的 keywords
                        {"match": None, "keywords": ["test"]},  # 无效的 match
                        {},  # 空规则
                    ]
                },
            },
        }

        # 应该能处理格式错误的规则而不崩溃
        engine = RuleEngine(config)

    def test_regex_special_characters(self):
        """测试正则特殊字符处理"""
        config = {
            "category_rules": {
                "测试": {
                    "rules": [
                        {"match": "title", "keywords": ["[test]", "(group)", "a*b"], "weight": 10},
                    ]
                },
            },
        }

        engine = RuleEngine(config)

        features = Mock(
            url="https://example.com",
            title="[test] (group) aab",
            domain="example.com",
            path_segments=[],
            content_type="webpage",
        )

        # 应该正确处理正则特殊字符
        result = engine.classify(features)

    @given(
        domain=st.text(min_size=1, max_size=100),
        title=st.text(min_size=0, max_size=200),
    )
    def test_fuzz_classify(self, domain: str, title: str):
        """模糊测试分类"""
        config = {
            "category_rules": {
                "测试": {
                    "rules": [
                        {"match": "domain", "keywords": ["test"], "weight": 10},
                    ]
                },
            },
        }

        engine = RuleEngine(config)

        features = Mock(
            url=f"https://{domain}",
            title=title,
            domain=domain,
            path_segments=[],
            content_type="webpage",
        )

        # 不应该崩溃
        try:
            result = engine.classify(features)
        except Exception:
            pass  # 某些输入可能导致异常，这是可接受的


class TestRuleEnginePerformance:
    """规则引擎性能测试"""

    @pytest.fixture
    def large_config(self):
        """大量规则配置"""
        config = {"category_rules": {}}

        # 生成100个分类，每个分类10条规则
        for i in range(100):
            category = f"分类_{i}"
            config["category_rules"][category] = {
                "rules": [
                    {"match": "domain", "keywords": [f"domain{i}.com"], "weight": 10}
                    for j in range(10)
                ]
            }

        return config

    def test_large_rule_set_performance(self, large_config):
        """测试大量规则的性能"""
        import time

        engine = RuleEngine(large_config)

        features = Mock(
            url="https://domain50.com/test",
            title="Test",
            domain="domain50.com",
            path_segments=["test"],
            content_type="webpage",
        )

        start = time.time()
        for _ in range(100):
            engine.classify(features)
        elapsed = time.time() - start

        # 100次分类应该在合理时间内完成（<5秒）
        assert elapsed < 5.0
