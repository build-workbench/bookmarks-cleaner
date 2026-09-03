"""LLM 分类器测试 - 验证模块可导入、默认禁用、成功路径"""

import pytest

requests = pytest.importorskip("requests")

import cleanbookmarks.llm as llm_mod  # noqa: E402
from cleanbookmarks.llm import LLMClassifier, LLMPromptBuilder  # noqa: E402


def _enabled_config():
    return {
        "enable": True,
        "api_key_env": "TEST_API_KEY",
        "base_url": "https://example.com",
        "model": "test-model",
        "temperature": 0.0,
        "top_p": 1.0,
        "timeout_seconds": 5,
        "max_retries": 0,
    }


class _FakeResponse:
    status_code = 200

    def __init__(self, content):
        self._content = content

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


class TestLLMClassifier:
    def test_import_and_init(self):
        """模块可导入且可实例化（回归：strip_category_prefix import bug）"""
        llm = LLMClassifier()
        assert llm is not None

    def test_default_disabled(self):
        """默认配置下 LLM 未启用，classify 返回 None"""
        llm = LLMClassifier()
        assert llm.enabled() is False
        assert llm.classify("https://example.com", "test") is None

    def test_stats_present(self):
        llm = LLMClassifier()
        stats = llm.get_stats()
        assert stats["enabled"] is False
        assert stats["calls"] == 0

    def test_classify_success(self, monkeypatch):
        """启用 + API key + mock 响应：完整成功路径"""
        llm = LLMClassifier()
        llm.llm_conf = _enabled_config()
        monkeypatch.setenv("TEST_API_KEY", "sk-test")
        monkeypatch.setattr(
            llm_mod.requests, "post",
            lambda *a, **k: _FakeResponse(
                '{"category": "编程", "confidence": 0.9, "reasons": ["包含代码仓库"]}'
            ),
        )
        result = llm.classify("https://github.com/user/repo", "My Repo")
        assert result is not None
        assert result["category"] == "编程"
        assert result["confidence"] == 0.9
        assert result["method"] == "llm"
        assert result["reasoning"] == ["LLM: 包含代码仓库"]

    def test_classify_caches_result(self, monkeypatch):
        """同一书签第二次调用走缓存，不再发起请求"""
        llm = LLMClassifier()
        llm.llm_conf = _enabled_config()
        monkeypatch.setenv("TEST_API_KEY", "sk-test")
        calls = {"n": 0}

        def fake_post(*a, **k):
            calls["n"] += 1
            return _FakeResponse('{"category": "编程", "confidence": 0.9, "reasons": ["x"]}')

        monkeypatch.setattr(llm_mod.requests, "post", fake_post)
        llm.classify("https://github.com/user/repo", "My Repo")
        llm.classify("https://github.com/user/repo", "My Repo")
        assert calls["n"] == 1
        assert llm.get_stats()["cache_hits"] == 1

    def test_classify_bad_json_returns_none(self, monkeypatch):
        """LLM 返回非法 JSON -> None，不崩溃"""
        llm = LLMClassifier()
        llm.llm_conf = _enabled_config()
        monkeypatch.setenv("TEST_API_KEY", "sk-test")
        monkeypatch.setattr(
            llm_mod.requests, "post",
            lambda *a, **k: _FakeResponse("not json at all"),
        )
        assert llm.classify("https://github.com/user/repo", "My Repo") is None
        assert llm.get_stats()["failures"] == 1

    def test_classify_retries_on_http_error(self, monkeypatch):
        """首次 HTTP 500 后重试成功"""
        class _RetryResponse:
            status_code = 500

            def json(self):
                return {}

        llm = LLMClassifier()
        llm.llm_conf = {**_enabled_config(), "max_retries": 1}
        monkeypatch.setenv("TEST_API_KEY", "sk-test")
        calls = {"n": 0}

        def fake_post(*a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                return _RetryResponse()
            return _FakeResponse('{"category": "编程", "confidence": 0.9, "reasons": ["x"]}')

        monkeypatch.setattr(llm_mod.requests, "post", fake_post)
        result = llm.classify("https://github.com/user/repo", "My Repo")
        assert result is not None
        assert calls["n"] == 2

    def test_classify_non_numeric_confidence(self, monkeypatch):
        """回归：LLM 返回 "confidence": "high" 不得 ValueError 逃逸"""
        llm = LLMClassifier()
        llm.llm_conf = _enabled_config()
        monkeypatch.setenv("TEST_API_KEY", "sk-test")
        monkeypatch.setattr(
            llm_mod.requests, "post",
            lambda *a, **k: _FakeResponse('{"category": "编程", "confidence": "high", "reasons": ["x"]}'),
        )
        result = llm.classify("https://github.com/user/repo", "My Repo")
        assert result is not None
        assert result["confidence"] == 0.0


class TestLLMPromptBuilder:
    def test_build_messages(self):
        builder = LLMPromptBuilder()
        messages, response_format = builder.build_messages(
            bookmark={"url": "https://example.com", "title": "test"},
            hints={},
            category_library=[{"name": "编程", "parent": None, "description": "主分类 编程"}],
        )
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert response_format == {"type": "json_object"}
