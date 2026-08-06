"""书签分类器 - 规则优先 + ML(可选) + LLM(可选)"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from cleanbook.cache import CacheManager
from cleanbook.config import load_json_config, resolve_config_path
from cleanbook.fusion import FusionEngine
from cleanbook.models import BookmarkFeatures, ClassificationResult
from cleanbook.rules import RuleEngine
from cleanbook.text_utils import normalize_category_config, normalize_category_string

_CHINESE_REGEX = re.compile(r"[\u4e00-\u9fff]")
_ENGLISH_REGEX = re.compile(r"[a-zA-Z]")

try:
    from cleanbook.ml import MLClassifierWrapper
except ImportError:
    MLClassifierWrapper = None  # type: ignore[assignment,misc]

try:
    from cleanbook.llm import LLMClassifier
except ImportError:
    LLMClassifier = None  # type: ignore[assignment,misc]


class BookmarkClassifier:
    """书签分类器

    集成规则引擎、ML(可选)和 LLM(可选)，通过加权融合输出最终分类。
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        enable_ml: bool = True,
        config: Optional[Dict] = None,
    ):
        resolved_path, _ = resolve_config_path(config_path)
        self.config_path = str(resolved_path)
        self.enable_ml = enable_ml
        self.logger = logging.getLogger(__name__)

        self._config: Optional[Dict] = (
            normalize_category_config(config) if isinstance(config, dict) else None
        )
        self._rule_engine: Optional[RuleEngine] = None
        self._ml_classifier = None
        self._llm_classifier = None
        self._fusion_engine: Optional[FusionEngine] = None

        self.feature_cache: CacheManager[BookmarkFeatures] = CacheManager(max_size=10000, strategy="lru")
        self.classification_cache: CacheManager[ClassificationResult] = CacheManager(max_size=5000, strategy="lru")

        self.stats = {
            "total_classified": 0,
            "rule_engine": 0,
            "ml_classifier": 0,
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
    def ml_classifier(self):
        if self._ml_classifier is None and self.enable_ml and MLClassifierWrapper is not None:
            try:
                self._ml_classifier = MLClassifierWrapper()
                self.logger.info("机器学习组件已启用")
            except Exception as e:
                self.logger.warning(f"机器学习组件初始化失败: {e}")
        return self._ml_classifier

    @property
    def llm_classifier(self):
        if self._llm_classifier is None and LLMClassifier is not None:
            try:
                self._llm_classifier = LLMClassifier(self.config_path)
            except Exception as e:
                self.logger.warning(f"LLM 分类器初始化失败: {e}")
        return self._llm_classifier

    @property
    def fusion_engine(self) -> FusionEngine:
        if self._fusion_engine is None:
            self._fusion_engine = FusionEngine(
                method_weights=self.config.get("method_weights"),
                category_normalizer=normalize_category_string,
            )
        return self._fusion_engine

    def _load_config(self) -> Dict:
        config, _, _ = load_json_config(self.config_path)
        normalized = normalize_category_config(config)
        if not isinstance(normalized.get("category_rules"), dict) or not normalized.get("category_rules"):
            raise ValueError(f"配置缺少有效的 category_rules: {self.config_path}")
        return normalized

    def extract_features(self, url: str, title: str) -> BookmarkFeatures:
        cache_key = f"{url}::{title}"

        def _extract():
            content_type = self._detect_content_type(url, title)
            language = self._detect_language(title)
            return BookmarkFeatures.from_url_title(url, title, content_type, language)

        return self.feature_cache.get_or_compute(cache_key, _extract)

    def classify(self, url: str, title: str) -> ClassificationResult:
        start_time = datetime.now()
        cache_key = hashlib.md5(f"{url}::{title}".encode()).hexdigest()
        cached = self.classification_cache.get(cache_key)
        if cached is not None:
            self.stats["cache_hits"] += 1
            cached.processing_time = (datetime.now() - start_time).total_seconds()
            return cached

        features = self.extract_features(url, title)
        results: List[ClassificationResult] = []

        # 1) 规则引擎
        rule_result = self.rule_engine.classify(features)
        if rule_result is not None:
            results.append(self._to_classification_result(rule_result))

        # 2) 机器学习
        if self.ml_classifier:
            ml_result = self.ml_classifier.classify(features)
            if ml_result is not None:
                results.append(self._to_classification_result(ml_result))

        # 3) LLM（可选）
        if self.llm_classifier and self.llm_classifier.enabled():
            try:
                llm_result = self.llm_classifier.classify(
                    url, title,
                    context={"domain": features.domain, "content_type": features.content_type, "language": features.language},
                )
                if llm_result is not None:
                    results.append(self._to_classification_result(llm_result))
            except Exception as e:
                self.logger.warning(f"LLM 分类调用失败: {e}")

        confidence_threshold = self.config.get("ai_settings", {}).get("confidence_threshold", 0.7)
        final_result = self.fusion_engine.fuse(
            results, features=features,
            confidence_threshold=float(confidence_threshold),
            subcategory_resolver=self._determine_subcategory,
        )

        final_method = final_result.method
        if "rule_engine" in final_method:
            self.stats["rule_engine"] += 1
        if "machine_learning" in final_method:
            self.stats["ml_classifier"] += 1
        if "llm" in final_method:
            self.stats["llm"] += 1
        if final_method == "fallback":
            self.stats["fallback"] += 1

        final_result.processing_time = (datetime.now() - start_time).total_seconds()
        self._update_stats(final_result)
        self.classification_cache.put(cache_key, final_result)
        return final_result

    @staticmethod
    def _to_classification_result(raw) -> ClassificationResult:
        if isinstance(raw, ClassificationResult):
            return raw
        if isinstance(raw, dict):
            return ClassificationResult(
                category=raw.get("category", "未分类"),
                confidence=float(raw.get("confidence", 0.0)),
                subcategory=raw.get("subcategory"),
                reasoning=raw.get("reasoning", []),
                alternatives=raw.get("alternatives", []),
                processing_time=float(raw.get("processing_time", 0.0)),
                method=raw.get("method", "unknown"),
                facets=raw.get("facets", {}),
            )
        raise TypeError(f"Unexpected classification result type: {type(raw)}")

    def _determine_subcategory(self, category: str, features: BookmarkFeatures) -> Optional[str]:
        hierarchy = self.config.get("category_hierarchy", {})
        if isinstance(hierarchy, dict) and category in hierarchy:
            title_lower = features.title.lower()
            for sub in hierarchy[category]:
                if sub.lower() in title_lower:
                    return sub
        return None

    def _detect_content_type(self, url: str, title: str) -> str:
        url_lower = url.lower()
        title_lower = title.lower()
        if any(d in url_lower for d in ["youtube.com", "bilibili.com", "vimeo.com"]):
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

    def _detect_language(self, title: str) -> str:
        if _CHINESE_REGEX.search(title):
            return "zh"
        if _ENGLISH_REGEX.search(title):
            return "en"
        return "unknown"

    def _update_stats(self, result: ClassificationResult):
        self.stats["total_classified"] += 1
        total = self.stats["total_classified"]
        old_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = (old_avg * (total - 1) + result.confidence) / total

    def learn_from_feedback(self, url: str, title: str, correct_category: str, predicted_category: str):
        features = self.extract_features(url, title)
        if self.ml_classifier:
            self.ml_classifier.online_learn(features, correct_category)
        self.feature_cache.invalidate(f"{url}::{title}")
        self.classification_cache.invalidate(hashlib.md5(f"{url}::{title}".encode()).hexdigest())
        self.logger.debug(f"学习反馈: {predicted_category} -> {correct_category}")

    def get_statistics(self) -> Dict:
        total_predictions = (
            self.stats["rule_engine"] + self.stats["ml_classifier"]
            + self.stats["llm"] + self.stats["fallback"]
        )
        return {
            "total_classified": self.stats["total_classified"],
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": self.stats["cache_hits"] / max(self.stats["total_classified"], 1),
            "average_confidence": self.stats["average_confidence"],
            "classification_methods": {
                "rule_engine": self.stats["rule_engine"],
                "ml_classifier": self.stats["ml_classifier"],
                "llm": self.stats["llm"],
                "unclassified (fallback)": self.stats["fallback"],
                "total": total_predictions,
            },
            "ml_enabled": self.ml_classifier is not None,
        }

    def save_model(self, path: str = "models/ai_classifier.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        model_data = {
            "version": "3.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "config": self.config,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(model_data, f, ensure_ascii=False, indent=2)
        if self.ml_classifier:
            self.ml_classifier.save_model()
        self.logger.info(f"模型已保存到: {path}")

    def load_model(self, path: str = "models/ai_classifier.json"):
        if not os.path.exists(path):
            self.logger.warning(f"模型文件不存在: {path}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            self.stats = model_data.get("stats", self.stats)
            if self.ml_classifier:
                self.ml_classifier.load_model()
            self.logger.info(f"模型已从 {path} 加载")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
