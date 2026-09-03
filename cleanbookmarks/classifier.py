"""书签分类器 - 规则优先 + LLM(可选) 两级级联"""

from __future__ import annotations

import hashlib
import logging
import threading
from datetime import datetime
from typing import Dict, Optional

from cleanbookmarks.cache import CacheManager
from cleanbookmarks.config import load_json_config, resolve_config_path
from cleanbookmarks.models import BookmarkFeatures, ClassificationResult
from cleanbookmarks.rules import RuleEngine
from cleanbookmarks.text_utils import (
    detect_language,
    is_video_url,
    normalize_category_config,
)

try:
    from cleanbookmarks.llm import LLMClassifier
except ImportError:
    LLMClassifier = None  # type: ignore[assignment,misc]


class BookmarkClassifier:
    """书签分类器

    两级级联：规则引擎给出确定性主分类，LLM(可选)在规则未命中时兜底、命中时补充子分类。
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.logger = logging.getLogger(__name__)

        if isinstance(config, dict):
            normalized = normalize_category_config(config)
            if not isinstance(normalized.get("category_rules"), dict) or not normalized.get("category_rules"):
                raise ValueError("传入的 config 缺少有效的 category_rules")
            self._config = normalized
        else:
            self._config = None
        self._rule_engine: Optional[RuleEngine] = None
        self._llm_classifier = None

        # 缓存大小来自配置（默认 10000），分类结果缓存减半以省内存
        cache_size = 10000
        if isinstance(config, dict):
            try:
                cache_size = int((config.get("ai_settings") or {}).get("cache_size", 10000))
            except (TypeError, ValueError):
                cache_size = 10000
        self.feature_cache: CacheManager[BookmarkFeatures] = CacheManager(max_size=cache_size, strategy="lru")
        self.classification_cache: CacheManager[ClassificationResult] = CacheManager(max_size=max(cache_size // 2, 100), strategy="lru")

        # stats 由多线程（_classify_batch）并发更新，需要锁保护
        self._stats_lock = threading.Lock()

        self.stats = {
            "total_classified": 0,
            "rule_engine": 0,
            "fallback": 0,
            "cache_hits": 0,
            "average_confidence": 0.0,
            "llm": 0,
        }

    @property
    def config(self) -> Dict:
        if self._config is None:
            self._config = self._load_config()
        return self._config

    @property
    def rule_engine(self) -> RuleEngine:
        if self._rule_engine is None:
            self._rule_engine = RuleEngine(self.config)
        return self._rule_engine

    @property
    def llm_classifier(self):
        if self._llm_classifier is None and LLMClassifier is not None:
            try:
                self._llm_classifier = LLMClassifier(self.config_path)
            except Exception as e:
                self.logger.warning(f"LLM 分类器初始化失败: {e}")
        return self._llm_classifier

    def _load_config(self) -> Dict:
        config, _, _ = load_json_config(self.config_path)
        normalized = normalize_category_config(config)
        if not isinstance(normalized.get("category_rules"), dict) or not normalized.get("category_rules"):
            raise ValueError(f"配置缺少有效的 category_rules: {self.config_path}")
        return normalized

    def reload_config(self, config: Optional[Dict] = None) -> None:
        """配置被外部更新（如 LLM 优化覆写）后重载并重建规则引擎。

        同时清空缓存，避免旧规则结果残留。
        """
        if isinstance(config, dict):
            normalized = normalize_category_config(config)
            if not isinstance(normalized.get("category_rules"), dict) or not normalized.get("category_rules"):
                raise ValueError("传入的 config 缺少有效的 category_rules")
            self._config = normalized
        else:
            self._config = self._load_config()
        self._rule_engine = None  # 惰性重建
        self.feature_cache.clear()
        self.classification_cache.clear()
        self.logger.info("分类器配置已重载")

    def extract_features(self, url: str, title: str) -> BookmarkFeatures:
        cache_key = f"{url}::{title}"

        def _extract():
            content_type = self._detect_content_type(url, title)
            language = detect_language(title)
            return BookmarkFeatures.from_url_title(url, title, content_type, language)

        return self.feature_cache.get_or_compute(cache_key, _extract)

    def classify(self, url: str, title: str) -> ClassificationResult:
        start_time = datetime.now()
        cache_key = hashlib.md5(f"{url}::{title}".encode()).hexdigest()
        cached = self.classification_cache.get(cache_key)
        if cached is not None:
            with self._stats_lock:
                self.stats["cache_hits"] += 1
            cached.processing_time = (datetime.now() - start_time).total_seconds()
            return cached

        features = self.extract_features(url, title)

        # 1) 规则引擎 - 确定性优先
        rule_result = self.rule_engine.classify(features)

        # 2) LLM（可选）- 规则未命中时兜底，命中时补充子分类
        llm_result = None
        if self.llm_classifier and self.llm_classifier.enabled():
            try:
                llm_result = self.llm_classifier.classify(
                    url, title,
                    context={"domain": features.domain, "content_type": features.content_type, "language": features.language},
                )
            except Exception as e:
                self.logger.warning(f"LLM 分类调用失败: {e}")

        confidence_threshold = self.config.get("ai_settings", {}).get("confidence_threshold", 0.7)
        final_result = self._cascade_fuse(
            rule_result=rule_result,
            llm_result=llm_result,
            features=features,
            confidence_threshold=float(confidence_threshold),
        )

        with self._stats_lock:
            if "rule_engine" in final_result.method:
                self.stats["rule_engine"] += 1
            if "llm" in final_result.method:
                self.stats["llm"] += 1
            if final_result.method == "fallback":
                self.stats["fallback"] += 1

        final_result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_stats(final_result)
        self.classification_cache.put(cache_key, final_result)
        return final_result

    def _cascade_fuse(
        self,
        rule_result,
        llm_result,
        features: BookmarkFeatures,
        confidence_threshold: float,
    ) -> ClassificationResult:
        """级联决策：规则命中即采用规则主分类，LLM 补子分类/facets；规则未命中才走 LLM"""
        if rule_result is not None:
            result = self._to_classification_result(rule_result)
            # 1) 配置的 category_hierarchy 标题匹配
            if result.subcategory is None:
                result.subcategory = self._determine_subcategory(result.category, features)
            # 2) LLM 补充子分类/facets/理由
            if llm_result is not None:
                llm = self._to_classification_result(llm_result)
                if result.subcategory is None and llm.subcategory:
                    result.subcategory = llm.subcategory
                # LLM 输出不可控，facets 可能是非 dict（如列表/字符串），防御性处理
                llm_facets = llm.facets if isinstance(llm.facets, dict) else {}
                for k, v in llm_facets.items():
                    if v and k not in (result.facets or {}):
                        result.facets[k] = v
                result.reasoning.extend(llm.reasoning or [])
        elif llm_result is not None:
            result = self._to_classification_result(llm_result)
        else:
            return ClassificationResult(
                category="未分类", confidence=0.0,
                reasoning=["没有匹配到任何分类规则"], method="fallback",
            )

        if result.category != "未分类" and result.confidence < confidence_threshold:
            result.reasoning.append(
                f"最终置信度 {result.confidence:.2f} 低于阈值 {confidence_threshold:.2f}，标记为未分类"
            )
            return ClassificationResult(
                category="未分类", subcategory=None,
                confidence=result.confidence,
                reasoning=result.reasoning,
                alternatives=result.alternatives[:3],
                method=result.method, facets=result.facets,
            )
        return result

    @staticmethod
    def _to_classification_result(raw) -> ClassificationResult:
        if isinstance(raw, ClassificationResult):
            return raw
        if isinstance(raw, dict):
            # LLM 输出不可控，facets 可能是非 dict（如列表/字符串），统一防御
            facets = raw.get("facets", {})
            if not isinstance(facets, dict):
                facets = {}
            return ClassificationResult(
                category=raw.get("category", "未分类"),
                confidence=float(raw.get("confidence", 0.0)),
                subcategory=raw.get("subcategory"),
                reasoning=raw.get("reasoning", []),
                alternatives=raw.get("alternatives", []),
                processing_time=float(raw.get("processing_time", 0.0)),
                method=raw.get("method", "unknown"),
                facets=facets,
            )
        raise TypeError(f"Unexpected classification result type: {type(raw)}")

    def _determine_subcategory(self, category: str, features: BookmarkFeatures) -> Optional[str]:
        hierarchy = self.config.get("category_hierarchy", {})
        if not isinstance(hierarchy, dict):
            return None
        # 规则引擎的 category 可能是 '主类/子类' 格式，按主类查 hierarchy
        main = category.split("/", 1)[0].strip()
        subs = hierarchy.get(category) or hierarchy.get(main)
        if not isinstance(subs, list):
            return None
        title_lower = features.title.lower()
        for sub in subs:
            if str(sub).lower() in title_lower:
                return sub
        return None

    def _detect_content_type(self, url: str, title: str) -> str:
        url_lower = url.lower()
        title_lower = title.lower()
        if is_video_url(url):
            return "video"
        if any(d in url_lower for d in ["github.com", "gitlab.com"]):
            return "code_repository"
        if any(p in url_lower for p in ["docs.", "documentation", "wiki"]):
            return "documentation"
        if any(d in url_lower for d in ["arxiv.org", "acm.org", "ieee.org"]):
            return "academic_paper"
        if any(k in title_lower for k in ["news", "新闻", "breaking"]):
            return "news"
        if any(k in title_lower for k in ["tool", "工具", "online", "generator"]):
            return "online_tool"
        return "webpage"

    def _update_stats(self, result: ClassificationResult):
        with self._stats_lock:
            self.stats["total_classified"] += 1
            total = self.stats["total_classified"]
            old_avg = self.stats["average_confidence"]
            self.stats["average_confidence"] = (old_avg * (total - 1) + result.confidence) / total

    def get_statistics(self) -> Dict:
        total_predictions = (
            self.stats["rule_engine"] + self.stats["llm"] + self.stats["fallback"]
        )
        # total_classified 只在缓存未命中时 +1，分母 = 命中 + 未命中 = 总尝试数
        total_attempts = self.stats["cache_hits"] + self.stats["total_classified"]
        return {
            "total_classified": self.stats["total_classified"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": self.stats["cache_hits"] / max(total_attempts, 1),
            "average_confidence": self.stats["average_confidence"],
            "classification_methods": {
                "rule_engine": self.stats["rule_engine"],
                "llm": self.stats["llm"],
                "unclassified (fallback)": self.stats["fallback"],
                "total": total_predictions,
            },
            "llm_enabled": self.llm_classifier is not None and self.llm_classifier.enabled(),
        }
