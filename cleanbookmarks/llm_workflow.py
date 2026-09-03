"""LLM 增强工作流 - 语料分析 / 配置优化 / 结果审核

在 llm.enhanced.enable=true 时，LLM 以三阶段强势参与分类流程：
  A. analyze_corpus  全面读取书签画像，输出主题分布总结
  B. suggest_config_updates 基于画像产出保守的规则增量建议
  C. audit_results   逐条审核分类结果，返回 ok/fix 修正

任何阶段失败（网络/解析/非法响应）都会安全降级：记 warning 跳过该
阶段，保证离线兜底路径永远可用。
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from cleanbookmarks.config import (
    apply_category_updates,
    backup_config_file,
    read_json_config_file,
    write_json_config_file,
)
from cleanbookmarks.text_utils import detect_language

logger = logging.getLogger(__name__)

# 中文/英文/数字单词提取（标题关键词画像用）
_WORD_REGEX = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]{2,}|[\u4e00-\u9fff]{2,}")


class LLMEnhancedWorkflow:
    """三阶段增强工作流，复用 LLMClassifier 的 chat_json 通道"""

    def __init__(self, llm_classifier, config_path: str):
        self.llm = llm_classifier
        self.config_path = config_path
        self.enhanced_conf = ((self.llm.llm_conf or {}).get("enhanced") or {}) or {}

    # ---------- 开关 ----------

    def enabled(self) -> bool:
        """总开关：需 llm.enable 与 llm.enhanced.enable 同时为 true"""
        return bool(self.llm.enabled() and self.enhanced_conf.get("enable", False))

    def stage_enabled(self, stage: str, default: bool = True) -> bool:
        """子阶段开关：analyze_corpus / optimize_config / audit_results"""
        return bool(self.enhanced_conf.get(stage, default))

    def _chat(self, system: str, user_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """构造 messages 并调用 chat_json，返回解析后的 JSON 或 None"""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ]
        return self.llm.chat_json(messages)

    # ---------- A. 语料分析 ----------

    @staticmethod
    def _corpus_profile(bookmarks: List[Dict]) -> Dict[str, Any]:
        """把书签聚合成轻量画像，供 LLM 分析（避免整批原文超长）"""
        domains = Counter()
        titles: List[str] = []
        languages = Counter()
        for b in bookmarks:
            url = (b.get("url") or "") if isinstance(b, dict) else ""
            title = (b.get("title") or "") if isinstance(b, dict) else ""
            if url:
                try:
                    domain = urlparse(url).netloc.lower().replace("www.", "")
                    if domain:
                        domains[domain] += 1
                except (ValueError, AttributeError):
                    pass
            if title:
                titles.append(title)
                languages[detect_language(title)] += 1
        word_counter: Counter = Counter()
        for t in titles:
            for w in _WORD_REGEX.findall(t.lower()):
                word_counter[w] += 1
        return {
            "total": len(bookmarks),
            "top_domains": domains.most_common(20),
            "top_keywords": word_counter.most_common(30),
            "language_distribution": dict(languages),
        }

    def analyze_corpus(self, bookmarks: List[Dict]) -> Optional[Dict[str, Any]]:
        """A 阶段：整体分析书签语料，输出主题判断与建议"""
        if not bookmarks:
            return None
        profile = self._corpus_profile(bookmarks)
        system = (
            "你是书签信息架构师。请分析用户书签语料的整体画像，判断主题分布，"
            "输出 JSON：{\"summary\": \"整体主题判断(中文, 2-4句)\", "
            "\"suggested_categories\": [\"建议关注的主分类名\"]}"
        )
        data = self._chat(system, {"corpus_profile": profile, "task": "分析语料主题"})
        if not data:
            return None
        return {
            "summary": str(data.get("summary", "")),
            "suggested_categories": [
                str(c) for c in (data.get("suggested_categories") or [])
                if isinstance(c, str) and c
            ],
        }

    # ---------- B. 配置优化 ----------

    def _category_summary(self) -> List[Dict[str, Any]]:
        """提取现有 category_rules 摘要（类目 + 关键词前 8 条）供 LLM 参考"""
        try:
            config = read_json_config_file(Path(self.config_path))
        except Exception:
            return []
        summary: List[Dict[str, Any]] = []
        for cat, cat_data in (config.get("category_rules") or {}).items():
            kws: List[str] = []
            for rule in (cat_data or {}).get("rules", []) or []:
                for kw in (rule or {}).get("keywords", []) or []:
                    kws.append(kw)
            summary.append({"category": cat, "existing_keywords": kws[:8]})
        return summary

    def suggest_config_updates(self, corpus: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """B 阶段：基于语料画像产出保守规则增量（只加不减）"""
        categories = self._category_summary()
        if not categories:
            return None
        system = (
            "你是书签分类规则优化器。基于语料画像与现有类目，输出保守的规则增量建议，"
            "只允许给现有类目追加关键词或新增类目，禁止删除/合并/改权重。"
            "输出 JSON：{\"category_updates\": [{\"category\": \"主类/子类\", "
            "\"add_keywords\": [\"关键词\", ...]}], "
            "\"add_categories\": [{\"category\": \"新主类/子类\", \"keywords\": [\"关键词\"]}]}"
        )
        return self._chat(system, {
            "task": "给出配置优化建议",
            "corpus_summary": (corpus or {}).get("summary", ""),
            "suggested_categories": (corpus or {}).get("suggested_categories", []),
            "current_categories": categories,
            "rule": "只增量、不删除；关键词需简短具体（域名片段或标题词）；"
                    "新增类目需确有语料支撑且与现有类目不重叠",
        })

    def apply_and_persist(self, updates: Dict[str, Any], backup: bool = True) -> bool:
        """把 B 阶段建议写入配置文件（覆写前可选备份），返回是否成功"""
        path = Path(self.config_path)
        try:
            config = read_json_config_file(path)
        except Exception as e:
            logger.warning(f"LLM 配置优化：读取配置失败，跳过写入: {e}")
            return False
        if backup and self.stage_enabled("backup_config", True):
            try:
                backup_config_file(path)
            except Exception as e:
                logger.warning(f"LLM 配置优化：备份失败: {e}")
        updated = apply_category_updates(config, updates)
        try:
            write_json_config_file(path, updated)
            logger.info(f"LLM 配置优化：已应用规则增量并写入 {path}")
            return True
        except Exception as e:
            logger.warning(f"LLM 配置优化：写入失败: {e}")
            return False

    # ---------- C. 结果审核 ----------

    def audit_results(self, classified: List[Dict]) -> Dict[str, Any]:
        """C 阶段：分批审核分类结果，返回修正统计与按 index 的修正映射

        返回 {"audited": int, "fixed": int, "fixes": {index: {category, confidence, reason}}}
        任何批次失败跳过该批，不阻断流程。
        """
        stats = {"audited": 0, "fixed": 0, "fixes": {}}
        if not classified:
            return stats
        batch_size = int(self.enhanced_conf.get("audit_batch_size", 40) or 40)
        try:
            config = read_json_config_file(Path(self.config_path))
        except Exception as e:
            logger.warning(f"LLM 审核：读取配置失败，跳过: {e}")
            return stats
        valid_categories = self.llm.collect_valid_categories(config)

        system = (
            "你是书签分类审核员。逐条审核给定的分类结果，判断 category 是否准确。"
            "输出 JSON：{\"verdicts\": [{\"index\": 0, \"verdict\": \"ok\" | \"fix\", "
            "\"category\": \"修正后分类(仅 fix 时)\", \"confidence\": 0.0-1.0, "
            "\"reason\": \"修正理由(仅 fix 时，中文简短)\"}]}"
            "分类必须来自候选列表或 '未分类'；无把握时保留原分类并给 ok。"
        )
        candidate_hint = ", ".join(valid_categories[:15])

        for start in range(0, len(classified), batch_size):
            batch = classified[start : start + batch_size]
            payload_items = [
                {
                    "index": start + i,
                    "url": (b.get("url") or "") if isinstance(b, dict) else "",
                    "title": (b.get("title") or "") if isinstance(b, dict) else "",
                    "category": (b.get("category") or "") if isinstance(b, dict) else "",
                    "confidence": (b.get("confidence") or 0) if isinstance(b, dict) else 0,
                }
                for i, b in enumerate(batch)
            ]
            data = self._chat(system, {
                "task": "审核以下分类结果",
                "bookmarks": payload_items,
                "valid_categories": valid_categories,
                "category_hint": candidate_hint,
            })
            if not data:
                logger.warning(f"LLM 审核：批次 {start // batch_size + 1} 响应无效，跳过该批")
                continue
            for v in (data.get("verdicts") or []):
                if not isinstance(v, dict):
                    continue
                try:
                    idx = int(v.get("index"))
                except (TypeError, ValueError):
                    continue
                if idx < 0 or idx >= len(classified):
                    continue
                stats["audited"] += 1
                if v.get("verdict") == "fix":
                    new_cat = str(v.get("category") or "").strip()
                    if not new_cat:
                        continue
                    stats["fixes"][idx] = {
                        "category": new_cat,
                        "confidence": self._clamp_confidence(v.get("confidence")),
                        "reason": str(v.get("reason") or ""),
                    }
        stats["fixed"] = len(stats["fixes"])
        return stats

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0


def apply_audit_fixes(classified: List[Dict], fixes: Dict[int, Dict[str, Any]]) -> int:
    """把审核修正写回分类结果（按 index），返回修正条数。

    仅改 category/confidence，追加 audited 标记与 audit_reason，不动原始字段。
    """
    applied = 0
    for idx, fix in fixes.items():
        if idx < 0 or idx >= len(classified):
            continue
        bookmark = classified[idx]
        if not isinstance(bookmark, dict):
            continue
        bookmark["category"] = fix.get("category", bookmark.get("category", "未分类"))
        bookmark["confidence"] = fix.get("confidence", bookmark.get("confidence", 0.0))
        bookmark["subcategory"] = None  # 修正后子分类由组织阶段重新推导
        bookmark["audited"] = True
        bookmark["audit_reason"] = fix.get("reason", "")
        applied += 1
    return applied
