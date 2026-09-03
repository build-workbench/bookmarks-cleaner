"""LLM 增强工作流测试 - 全部 mock chat_json，无真实网络请求"""

import json

import pytest

from cleanbookmarks.llm_workflow import LLMEnhancedWorkflow, apply_audit_fixes
from cleanbookmarks.config import write_json_config_file


class _FakeLLM:
    """替身：记录 chat_json 调用并返回预设响应"""

    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []
        self.llm_conf = {
            "enable": True,
            "enhanced": {"enable": True, "audit_batch_size": 2},
        }

    def enabled(self):
        return True

    def chat_json(self, messages, **kwargs):
        self.calls.append(messages)
        if self.responses:
            return self.responses.pop(0)
        return None

    def collect_valid_categories(self, config):
        cats = list((config.get("category_order") or []))
        cats.append("未分类")
        return cats


def _make_workflow(tmp_path, responses=None, enhanced=None):
    cfg = {
        "category_order": ["AI", "编程"],
        "category_rules": {
            "AI": {"rules": [{"match": "domain", "keywords": ["openai.com"]}]},
            "编程": {"rules": [{"match": "domain", "keywords": ["github.com"]}]},
        },
    }
    cfg_path = tmp_path / "config.json"
    write_json_config_file(cfg_path, cfg)
    llm_conf = {"enable": True, "enhanced": {"enable": True, **(enhanced or {})}}
    fake = _FakeLLM(responses)
    fake.llm_conf = llm_conf
    return LLMEnhancedWorkflow(fake, str(cfg_path)), fake


class TestEnabled:
    def test_requires_both_switches(self, tmp_path):
        wf, _ = _make_workflow(tmp_path, enhanced={"enable": False})
        assert wf.enabled() is False

    def test_enabled_when_both_on(self, tmp_path):
        wf, _ = _make_workflow(tmp_path)
        assert wf.enabled() is True

    def test_stage_switches(self, tmp_path):
        wf, _ = _make_workflow(tmp_path, enhanced={"audit_results": False})
        assert wf.stage_enabled("audit_results", True) is False
        assert wf.stage_enabled("optimize_config", True) is True


class TestCorpusProfile:
    def test_profile_counts(self):
        bookmarks = [
            {"url": "https://github.com/user/repo", "title": "Python 教程 repo"},
            {"url": "https://github.com/a/b", "title": "Python 指南"},
            {"url": "https://docs.python.org/3/", "title": "Python 文档"},
        ]
        profile = LLMEnhancedWorkflow._corpus_profile(bookmarks)
        assert profile["total"] == 3
        # github.com 出现 2 次
        assert ("github.com", 2) in profile["top_domains"]
        # python 关键词出现
        kw = dict(profile["top_keywords"])
        assert any("python" in k.lower() for k in kw)

    def test_profile_ignores_junk(self):
        profile = LLMEnhancedWorkflow._corpus_profile([None, "junk", {"url": "", "title": ""}])
        assert profile["total"] == 3
        assert profile["top_domains"] == []


class TestAnalyzeCorpus:
    def test_returns_summary(self, tmp_path):
        wf, fake = _make_workflow(tmp_path, responses=[
            {"summary": "语料以编程为主", "suggested_categories": ["编程", "AI"]},
        ])
        result = wf.analyze_corpus([{"url": "https://github.com/x", "title": "Repo"}])
        assert result["summary"] == "语料以编程为主"
        assert result["suggested_categories"] == ["编程", "AI"]
        assert len(fake.calls) == 1

    def test_empty_bookmarks(self, tmp_path):
        wf, _ = _make_workflow(tmp_path)
        assert wf.analyze_corpus([]) is None

    def test_bad_response_returns_none(self, tmp_path):
        wf, _ = _make_workflow(tmp_path, responses=[None])
        assert wf.analyze_corpus([{"url": "https://x.com", "title": "X"}]) is None


class TestSuggestAndApply:
    def test_suggest_config_updates(self, tmp_path):
        wf, fake = _make_workflow(tmp_path, responses=[{
            "category_updates": [{"category": "AI", "add_keywords": ["claude"]}],
            "add_categories": [],
        }])
        corpus = {"summary": "AI 相关较多", "suggested_categories": ["AI"]}
        updates = wf.suggest_config_updates(corpus)
        assert updates["category_updates"][0]["add_keywords"] == ["claude"]

    def test_apply_persist_writes_config(self, tmp_path):
        wf, _ = _make_workflow(tmp_path)
        updates = {
            "category_updates": [{"category": "AI", "add_keywords": ["claude", "anthropic"]}],
            "add_categories": [{"category": "设计", "keywords": ["figma"]}],
        }
        assert wf.apply_and_persist(updates, backup=False) is True
        from cleanbookmarks.config import read_json_config_file
        from pathlib import Path
        cfg = read_json_config_file(Path(tmp_path) / "config.json")
        # AI 类目追加了关键词
        kws = [kw for rule in cfg["category_rules"]["AI"]["rules"] for kw in rule["keywords"]]
        assert "claude" in kws and "openai.com" in kws
        # 新增类目进 order
        assert cfg["category_order"] == ["AI", "编程", "设计"]

    def test_apply_creates_backup(self, tmp_path):
        wf, _ = _make_workflow(tmp_path)
        updates = {"category_updates": [{"category": "AI", "add_keywords": ["x"]}]}
        assert wf.apply_and_persist(updates) is True
        backups = list((tmp_path).glob("config.llm-backup-*.json"))
        assert len(backups) >= 1

    def test_apply_backup_disabled(self, tmp_path):
        wf, _ = _make_workflow(tmp_path, enhanced={"backup_config": False})
        updates = {"category_updates": [{"category": "AI", "add_keywords": ["x"]}]}
        assert wf.apply_and_persist(updates) is True
        assert not list((tmp_path).glob("config.llm-backup-*.json"))


class TestAudit:
    def _classified(self):
        return [
            {"url": "https://a.com", "title": "A", "category": "编程", "confidence": 0.9},
            {"url": "https://b.com", "title": "B", "category": "娱乐", "confidence": 0.8},
            {"url": "https://c.com", "title": "C", "category": "AI", "confidence": 0.7},
        ]

    def test_audit_fixes_by_index(self, tmp_path):
        wf, fake = _make_workflow(tmp_path, responses=[{
            "verdicts": [
                {"index": 0, "verdict": "ok"},
                {"index": 1, "verdict": "fix", "category": "编程", "confidence": 0.85, "reason": "实际是编程"},
            ],
        }])
        classified = self._classified()
        stats = wf.audit_results(classified)
        assert stats["audited"] == 2
        assert stats["fixed"] == 1
        assert 1 in stats["fixes"]
        assert stats["fixes"][1]["category"] == "编程"

    def test_audit_batches(self, tmp_path):
        """batch_size=2 时 3 条书签应分 2 批请求"""
        wf, fake = _make_workflow(tmp_path, enhanced={"audit_batch_size": 2})
        wf.audit_results(self._classified())
        # 3 条 / 2 每条 = 2 批
        assert len(fake.calls) == 2

    def test_audit_empty(self, tmp_path):
        wf, _ = _make_workflow(tmp_path)
        stats = wf.audit_results([])
        assert stats == {"audited": 0, "fixed": 0, "fixes": {}}

    def test_audit_bad_batch_skipped(self, tmp_path):
        wf, _ = _make_workflow(tmp_path, responses=[None])  # 第一批无效
        stats = wf.audit_results(self._classified())
        assert stats["audited"] == 0
        assert stats["fixed"] == 0


class TestApplyAuditFixes:
    def test_applies_and_marks(self):
        classified = [
            {"url": "https://a.com", "title": "A", "category": "娱乐", "confidence": 0.9},
        ]
        fixes = {0: {"category": "编程", "confidence": 0.8, "reason": "错分"}}
        assert apply_audit_fixes(classified, fixes) == 1
        assert classified[0]["category"] == "编程"
        assert classified[0]["confidence"] == 0.8
        assert classified[0]["audited"] is True
        assert classified[0]["audit_reason"] == "错分"

    def test_out_of_range_ignored(self):
        classified = [{"url": "https://a.com", "title": "A", "category": "编程"}]
        assert apply_audit_fixes(classified, {5: {"category": "AI"}}) == 0
        assert apply_audit_fixes(classified, {-1: {"category": "AI"}}) == 0
